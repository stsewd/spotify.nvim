import dataclasses
import time
from functools import cached_property, partial

import pynvim

from .spotify import Spotify, SpotifyError


@dataclasses.dataclass(slots=True)
class Settings:

    show_status: bool = True
    wait_time: float = 0.2
    template: list = dataclasses.field(
        default_factory=lambda: [
            {
                "template": " 🎶 {title}",
                "shorten": True,
            },
            {
                "template": " 🎨 {artists}",
                "shorten": True,
            },
            {
                "template": " 💿 {album_name}",
                "shorten": True,
            },
            {},
            [
                {
                    "template": "  {shuffle_symbol}",
                    "align": "center",
                },
                {
                    "template": "{status_symbol}",
                    "align": "center",
                },
                {
                    "template": "{volume_symbol} {volume}%  ",
                    "align": "center",
                },
            ],
            {},
            {
                "template": "{time} / {length}",
                "align": "center",
            },
            {
                "template": "{progress_bar}",
                "align": "center",
            },
        ]
    )
    symbols: dict = dataclasses.field(
        default_factory=lambda: {
            "playing": "▶",
            "paused": "⏸",
            "stopped": "■",
            "volume.high": "🔊",
            "volume.medium": "🔉",
            "volume.low": "🔈",
            "volume.muted": "🔇",
            "shuffle.enabled": "⤮ on",
            "shuffle.disabled": "⤮ off",
            "progress.mark": "●",
            "progress.complete": "─",
            "progress.missing": "┈",
        }
    )
    progress_bar_width: int = 32
    width: int = 34


@pynvim.plugin
class SpotifyNvimPlugin:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    @cached_property
    def settings(self):
        settings = Settings()
        for field in dataclasses.fields(Settings):
            setting = self.nvim.vars.get(f"spotify_{field.name}")
            if setting:
                default = getattr(settings, field.name)
                if isinstance(default, dict):
                    default.update(setting)
                else:
                    setattr(settings, field.name, setting)
        if self.nvim.vars.get("spotify_status_style"):
            self.notify(
                msg=(
                    "The `spotify_status_style` option has been removed. "
                    "Use the `spotify_symbols` option instead."
                ),
                level="error",
            )
        if self.nvim.vars.get("spotify_status_format"):
            self.notify(
                msg=(
                    "The `spotify_status_format` option has been removed. "
                    "Use the `spotify_template` option instead.",
                ),
                level="error",
            )
        return settings

    def wait(self):
        """
        Wait before retrieving information from DBus after an update.

        Dbus can take some time to return the latest updated state,
        after a modification.
        """
        time.sleep(self.settings.wait_time)

    @cached_property
    def handlers(self):
        return {
            "play/pause": (partial(self._spotify_method, event="toggle"), False),
            "next": (partial(self._spotify_method, event="next"), False),
            "prev": (partial(self._spotify_method, event="prev"), False),
            "play": (partial(self._spotify_method, event="play"), False),
            "pause": (partial(self._spotify_method, event="pause"), False),
            "stop": (partial(self._spotify_method, event="stop"), False),
            "show": (
                partial(self._spotify_method, event="show_window", show_status=False),
                False,
            ),
            "status": (self._handle_status, False),
            "volume": (self._handle_volume, True),
            "shuffle": (self._handle_shuffle, True),
            "time": (self._handle_time, True),
        }

    def _spotify_method(self, event, show_status=True):
        spotify = Spotify()
        getattr(spotify, event)()
        if show_status and self.settings.show_status:
            self.wait()
            self._show_current_status(spotify=spotify)

    def _handle_status(self):
        spotify = Spotify()
        self._show_current_status(spotify=spotify)

    def _handle_volume(self, value=None):
        spotify = Spotify()
        if value:
            spotify.volume = value
            self.wait()
        self._show_current_status(spotify)

    def _handle_time(self, value=None):
        spotify = Spotify()
        if value:
            spotify.time = value
            self.wait()
        self._show_current_status(spotify)

    def _handle_shuffle(self, value=None):
        spotify = Spotify()
        yes_values = ("yes", "on", "true")
        no_values = ("no", "off", "false")
        if value:
            if value in yes_values:
                spotify.shuffle = True
            elif value in no_values:
                spotify.shuffle = False
            else:
                valid_options = ", ".join(yes_values) + ", " + ", ".join(no_values)
                self.notify(
                    f"Invalid option. Valid options are: {valid_options}.",
                    level="error",
                )
                return
            self.wait()

        self._show_current_status(spotify)

    def _get_volume_symbol(self, volume):
        if volume == 0:
            status = "volume.muted"
        elif volume < 50:
            status = "volume.low"
        elif volume < 75:
            status = "volume.medium"
        else:
            status = "volume.high"
        return self.get_symbol(status)

    def _get_progress_bar(self, percent=0, length=35):
        middle = int(length * percent)
        bar = self.get_symbol("progress.complete") * (middle - 1)
        bar += self.get_symbol("progress.mark")
        bar += self.get_symbol("progress.missing") * (length - middle)
        return bar

    def _format_seconds(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:=02}:{seconds:=02}"

    def _get_shuffle_symbol(self, shuffle):
        state = "shuffle.enabled" if shuffle else "shuffle.disabled"
        return self.get_symbol(state)

    def _show_current_status(self, spotify: Spotify):
        width = self.settings.width
        meta = spotify.metadata()

        context = {
            "title": meta["title"],
            "artists": ", ".join(meta["artists"]),
            "album_name": meta["album.name"],
            "album_artists": meta["album.artists"],
            "shuffle_symbol": self._get_shuffle_symbol(spotify.shuffle),
        }

        status = spotify.status
        context["status"] = status
        context["status_symbol"] = self.get_symbol(status)

        volume = int(spotify.volume)
        context["volume"] = volume
        context["volume_symbol"] = self._get_volume_symbol(volume)

        current_time = spotify.time
        total_length = spotify.length
        context["time"] = self._format_seconds(current_time)
        context["length"] = self._format_seconds(total_length)
        context["progress_bar"] = self._get_progress_bar(
            percent=current_time / total_length,
            length=self.settings.progress_bar_width,
        )

        result = []
        for block in self.settings.template:
            if isinstance(block, dict):
                text = self._render(block=block, width=width, context=context)
            else:
                block_width = width // len(block)
                line = [
                    self._render(block=subblock, width=block_width, context=context)
                    for subblock in block
                ]
                text = "".join(line)
            result.append(text)
        self.notify("\n".join(result))

    def _render(self, block, context, width):
        template = block.get("template", "")
        text = template.format(**context)
        if block.get("shorten") and len(text) > width:
            text = text[: width - 3] + "..."
        align = block.get("align")
        if align == "center":
            return text.center(width)
        elif align == "left":
            return text.ljust(width)
        return text

    @cached_property
    def loglevels(self):
        return self.nvim.exec_lua("return vim.log.levels")

    def notify(self, msg, level="info"):
        level = self.loglevels[level.upper()]
        self.nvim.api.notify(msg, level, {"title": "Spotify"})

    def get_symbol(self, symbol, default=""):
        return self.settings.symbols.get(symbol, default)

    def error(self, msg):
        self.nvim.err_write(f"[spotify] {msg}\n")

    def print(self, msg):
        self.nvim.out_write(f"[spotify] {msg}\n")

    @pynvim.command(
        "Spotify",
        nargs="+",
        complete="customlist,SpotifyCompletions",
    )
    def spotify_command(self, args):
        try:
            attr = self.handlers.get(args[0])
            if not attr:
                self.error("Invalid option")
                return

            func, accept_args = attr
            if accept_args and len(args) > 1:
                func(args[1])
            else:
                func()
        except SpotifyError as e:
            self.error(str(e))

    @pynvim.function("SpotifyCompletions", sync=True)
    def spotify_completions(self, args):
        arglead, cmdline, cursorpos, *_ = args
        return [
            option
            for option in self.handlers
            if option.lower().startswith(arglead.lower())
        ]
