import dataclasses
from functools import cached_property, partial

import pynvim

from .spotify import Spotify, SpotifyError


# TODO: merge the dict defaults.
@dataclasses.dataclass
class RenderStatusOptions:
    return_array: bool = False
    template: list = dataclasses.field(
        default_factory=lambda: [
            [
                {
                    "template": "🎶",
                    "width": 3,
                    "align": "center",
                },
                {
                    "template": "{title}",
                    "shorten": True,
                },
            ],
            [
                {
                    "template": "🎨",
                    "width": 3,
                    "align": "center",
                },
                {
                    "template": "{artists}",
                    "shorten": True,
                },
            ],
            [
                {
                    "template": "💿",
                    "width": 3,
                    "align": "center",
                },
                {
                    "template": "{album_name}",
                    "shorten": True,
                },
            ],
            {},
            [
                {
                    "template": " ",
                    "width": 1,
                },
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
            [
                {
                    "template": " ",
                    "width": 1,
                },
                {
                    "template": "{time} / {length}",
                    "align": "center",
                },
            ],
            [
                {
                    "template": " ",
                    "width": 1,
                },
                {
                    "template": "{progress_bar}",
                    "align": "center",
                },
            ],
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
    progress_bar_width: int = 34
    # width: int = 34
    width: int = 45


@pynvim.plugin
class SpotifyNvimPlugin:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    @cached_property
    def settings(self):
        settings = RenderStatusOptions()
        for field in dataclasses.fields(RenderStatusOptions):
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
                partial(self._spotify_method, event="show_window"),
                False,
            ),
            "volume": (self._handle_volume, True),
            "shuffle": (self._handle_shuffle, True),
            "time": (self._handle_time, True),
        }

    def _spotify_method(self, event):
        spotify = Spotify()
        getattr(spotify, event)()
        return True

    def _handle_volume(self, value=None):
        spotify = Spotify()
        if value:
            spotify.volume = str(value)
        return spotify.volume

    def _handle_time(self, value=None):
        spotify = Spotify()
        if value:
            spotify.time = str(value)
        return spotify.time

    def _handle_shuffle(self, value=None):
        spotify = Spotify()
        yes_values = ("yes", "on", "true")
        no_values = ("no", "off", "false")
        if value == "toggle":
            value = not spotify.shuffle
        if value is not None:
            if value in yes_values or value is True:
                spotify.shuffle = True
            elif value in no_values or value is False:
                spotify.shuffle = False
            else:
                valid_options = (
                    ", ".join(yes_values) + ", " + ", ".join(no_values) + ", toggle"
                )
                self.notify(
                    f"Invalid option. Valid options are: {valid_options}.",
                    level="error",
                )
                return

        return spotify.shuffle

    def _get_volume_symbol(self, volume, settings: RenderStatusOptions):
        if volume == 0:
            status = "volume.muted"
        elif volume < 50:
            status = "volume.low"
        elif volume < 75:
            status = "volume.medium"
        else:
            status = "volume.high"
        return self.get_symbol(status, settings.symbols)

    def _get_progress_bar(self, settings: RenderStatusOptions, percent=0, length=35):
        middle = int(length * percent)
        bar = self.get_symbol("progress.complete", settings.symbols) * middle
        bar += self.get_symbol("progress.mark", settings.symbols)
        bar += self.get_symbol("progress.missing", settings.symbols) * (
            length - middle - 1
        )
        return bar

    def _format_seconds(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:=02}:{seconds:=02}"

    def _get_shuffle_symbol(self, shuffle, settings: RenderStatusOptions):
        state = "shuffle.enabled" if shuffle else "shuffle.disabled"
        return self.get_symbol(state, settings.symbols)

    def _show_current_status(self, spotify: Spotify, settings: RenderStatusOptions):
        status = "\n".join(self._render_current_status(spotify, settings))
        self.notify(status)

    def _render_current_status(
        self, spotify: Spotify, settings: RenderStatusOptions, cycle: int = 0
    ):
        width = settings.width
        meta = spotify.metadata()

        context = {
            "title": meta["title"],
            "artists": ", ".join(meta["artists"]),
            "album_name": meta["album.name"],
            "album_artists": meta["album.artists"],
            "shuffle_symbol": self._get_shuffle_symbol(spotify.shuffle, settings),
        }

        status = spotify.status
        context["status"] = status
        context["status_symbol"] = self.get_symbol(status, settings.symbols)

        volume = int(spotify.volume)
        context["volume"] = volume
        context["volume_symbol"] = self._get_volume_symbol(volume, settings)

        current_time = spotify.time
        total_length = spotify.length
        context["time"] = self._format_seconds(current_time)
        context["length"] = self._format_seconds(total_length)
        context["progress_bar"] = self._get_progress_bar(
            settings=settings,
            percent=current_time / total_length,
            length=settings.progress_bar_width,
        )

        result = []
        for block in settings.template:
            if isinstance(block, dict):
                text = self._render(
                    block=block, width=width, context=context, cycle=cycle
                )
            else:
                line = []
                block_width = width
                for i, subblock in enumerate(block):
                    default_subblock_width = block_width // (len(block) - i)
                    subblock_width = subblock.get("width", default_subblock_width)
                    block_width -= subblock_width
                    line.append(
                        self._render(
                            block=subblock,
                            width=subblock_width,
                            context=context,
                            cycle=cycle,
                        )
                    )
                text = "".join(line)
            result.append(text)

        if settings.return_array:
            return result
        return "\n".join(result)

    def _render(self, block: dict, context: dict, width: int, cycle: int = 0):
        pause = 6
        template = block.get("template", "")
        text = template.format(**context)
        text_len = len(text)
        if block.get("shorten") and text_len > width:
            tail = "..."
            width -= len(tail)
            cycle = cycle % (text_len - width + 1 + (pause * 2))
            if cycle < pause:
                cycle = 0
            else:
                cycle -= pause

            if cycle > text_len - width:
                cycle = text_len - width + 1

            start = cycle
            end = start + width
            text = text[start:end]
            if end < text_len:
                text += tail[: text_len - end]
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

    def get_symbol(self, symbol, symbols, default=""):
        return symbols.get(symbol, default)

    @pynvim.function("SpotifyMetadata", sync=True)
    def get_spotify_metadata(self, args):
        spotify = Spotify()
        result = {
            "volume": spotify.volume,
            "shuffle": spotify.shuffle,
            "length": spotify.length,
            "time": spotify.time,  # Current time
            "status": spotify.status,
            "metadata": spotify.metadata(),
        }
        return result

    @pynvim.function("SpotifyRenderStatus", sync=True)
    def get_rendered_status(self, args):
        """
        Get the rendered status.


        The first argument indicates the current cycle of the rendered content.

        The second argument are the options,
        they will be merged with the Settings object defaults.
        """
        cycle = 0
        if args:
            cycle = args[0]
        options = {}
        if args or len(args) > 1:
            options = args[1] or {}
        settings = RenderStatusOptions(**options)

        try:
            spotify = Spotify()
            status = self._render_current_status(
                spotify, cycle=cycle, settings=settings
            )
            return status
        except SpotifyError as e:
            self.notify(msg=str(e), level="error")
            return None

    @pynvim.function("SpotifyAction", sync=True)
    def execute_action(self, args):
        """
        The fist argument is the name of the action.
        If the action takes a value, the second argument is the value.
        """
        try:
            attr = self.handlers.get(args[0])
            if not attr:
                raise ValueError(f"Invalid action `{args[0]}`.")
            func, accept_args = attr
            if accept_args and len(args) > 1:
                return func(args[1])
            else:
                return func()
        except SpotifyError as e:
            self.notify(msg=str(e), level="error")
            return False
