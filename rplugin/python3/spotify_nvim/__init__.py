from functools import cached_property, partial

import pynvim

from .dataclasses import (
    AlbumContext,
    NotificationConfig,
    PlaybackContext,
    ProgressbarConfig,
    ShuffleContext,
    TemplateItem,
    TimeContext,
    VolumeContext,
)
from .spotify import Spotify, SpotifyError


@pynvim.plugin
class SpotifyNvimPlugin:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

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

    def _get_volume_state(self, volume):
        if volume == 0:
            return "muted"
        if volume < 50:
            return "low"
        if volume < 75:
            return "medium"
        return "high"

    def _get_volume_context(self, volume, config: NotificationConfig):
        symbols = config.symbols.volume
        states = config.states.volume
        state = self._get_volume_state(volume)
        return VolumeContext(
            symbol=getattr(symbols, state),
            state=getattr(states, state),
            value=volume,
        )

    def _get_time_context(self, current_time, duration):
        return TimeContext(
            current=self._format_seconds(current_time),
            duration=self._format_seconds(duration),
        )

    def _get_progress_bar(self, config: ProgressbarConfig, percent=0):
        length = config.width
        middle = int(length * percent)
        bar = config.filled * middle
        bar += config.marker
        bar += config.remaining * (length - middle - 1)
        return bar

    def _format_seconds(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:=02}:{seconds:=02}"

    def _get_album_context(self, meta):
        return AlbumContext(
            name=meta["album.name"],
            # name="We are not your kind",
            artists=", ".join(meta["album.artists"]),
        )

    def _get_shuffle_context(self, shuffle, config: NotificationConfig):
        symbols = config.symbols.shuffle
        states = config.states.shuffle
        return ShuffleContext(
            symbol=symbols.enabled if shuffle else symbols.disabled,
            state=states.enabled if shuffle else states.disabled,
        )

    def _get_playback_context(self, state, config: NotificationConfig):
        states = config.states.playback
        symbols = config.symbols.playback
        return PlaybackContext(
            symbol=getattr(symbols, state),
            state=getattr(states, state),
        )

    def _render_current_status(
        self, spotify: Spotify, config: NotificationConfig, cycle: int = 0
    ):
        meta = spotify.metadata()
        context = {
            "title": meta["title"],
            "artists": ", ".join(meta["artists"]),
            "album": self._get_album_context(meta),
            "shuffle": self._get_shuffle_context(spotify.shuffle, config),
            "playback": self._get_playback_context(spotify.status, config),
            "volume": self._get_volume_context(spotify.volume, config),
        }

        current_time = spotify.time
        duration = spotify.length
        context["time"] = self._get_time_context(current_time, duration)
        context["progressbar"] = self._get_progress_bar(
            config=config.progressbar,
            percent=current_time / duration,
        )

        result = []
        for blocks in config.template:
            if not blocks:
                result.append("")
                continue

            line = []
            blocks_with_fixed_width = [block for block in blocks if block.width]
            fixed_width = sum(block.width for block in blocks_with_fixed_width)
            default_block_width = (config.width - fixed_width) // (
                len(blocks) - len(blocks_with_fixed_width)
            )
            for block in blocks:
                block_width = block.width or default_block_width
                line.append(
                    self._render(
                        block=block,
                        width=block_width,
                        context=context,
                        cycle=cycle,
                        initial_cycle_pause=config.initial_cycle_pause,
                    )
                )
            text = "".join(line)
            result.append(text)

        return "\n".join(result)

    def _render(
        self,
        block: TemplateItem,
        context: dict,
        width: int,
        cycle: int = 0,
        initial_cycle_pause: int = 0,
    ):
        pause = initial_cycle_pause
        content = block.content
        text = content.format(**context)
        text_len = len(text)
        tail = "..."
        if block.shorten and text_len > width:
            # The cycle can go from the start of the text to the end, minus the width of the block,
            # since we don't want to continue the cycle after the whole text has been shown.
            max_index_to_cycle = text_len - width
            # We add the pause twice to account for the pause at the start and at the end.
            # Plus one, so we can go up to the last index.
            max_cycle = max_index_to_cycle + pause * 2 + 1
            cycle = cycle % max_cycle
            if cycle <= pause:
                cycle = 0
            else:
                cycle -= pause

            if cycle > max_index_to_cycle:
                cycle = max_index_to_cycle

            start = cycle
            end = start + width
            text = text[start:end]
            rest = text_len - end
            # TODO: This makes the tail to just appear,
            # figure out a nicer transition.
            if rest > 0:
                rest = min(rest, len(tail))
                text = text[:-rest] + tail[:rest]

        align = block.align
        if align == "center":
            return text.center(width)
        elif align == "left":
            return text.ljust(width)
        elif align == "right":
            return text.rjust(width)
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

        The first argument indicates the current cycle of the rendered content,
        the second argument is the plugin config.
        """
        if len(args) != 2:
            self.notify(
                msg="Two arguments are required: cycle and config",
                level="error",
            )
        cycle = args[0]
        config = NotificationConfig.from_dict(args[1])

        try:
            spotify = Spotify()
            status = self._render_current_status(spotify, cycle=cycle, config=config)
            return True, status
        except SpotifyError as e:
            return False, str(e)

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
