import dataclasses
import time
from dataclasses import dataclass

import pynvim

from .constants import OPTIONS, SYMBOLS_REPR
from .spotify import Spotify, SpotifyError


@dataclass(slots=True)
class Settings:

    show_status: bool = True
    wait_time: float = 0.2
    status_style: str = "ascii"
    status_format: str = " {status} {song} - {artists} {decorator}"


@pynvim.plugin
class SpotifyNvimPlugin:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    @property
    def settings(self):
        settings = Settings()
        for field in dataclasses.fields(Settings):
            setting = self.nvim.vars.get(f"spotify_{field.name}")
            if setting:
                setattr(settings, field.name, setting)
        return settings

    @property
    def loglevels(self):
        return self.nvim.exec_lua("return vim.log.levels")

    def _show_current_status(self, spotify):
        status, song, artists = spotify.get_status()

        decorator = ""
        if status.lower() == "playing":
            decorator = self._get_symbol_repr("music")
        status_format = self.settings.status_format + "\n"

        self.nvim.api.notify(
            status_format.format(
                status=self._get_symbol_repr(status),
                song=song,
                artists=", ".join(artists),
                decorator=decorator,
            ),
            self.loglevels["INFO"],
            {
                "title": "Spotify",
            },
        )

    def _get_symbol_repr(self, symbol):
        symbol = symbol.lower()
        repr_ = SYMBOLS_REPR.get(symbol, {}).get(self.settings.status_style, "")
        return repr_

    def error(self, msg):
        self.nvim.err_write(f"[spotify] {msg}\n")

    def print(self, msg):
        self.nvim.out_write(f"[spotify] {msg}\n")

    @pynvim.command(
        "Spotify",
        nargs=1,
        complete="customlist,SpotifyCompletions",
    )
    def spotify_command(self, args):
        try:
            attr = dict(OPTIONS).get(args[0])
            if not attr:
                self.error("Invalid option")
                return

            spotify = Spotify()
            if attr.startswith("_"):
                getattr(self, attr)(spotify)
            else:
                getattr(spotify, attr)()

            if self.settings.show_status and attr not in (
                "show_window",
                "_show_current_status",
            ):
                # We need to wait to the previous
                # command to get executed
                time.sleep(self.settings.wait_time)
                self._show_current_status(spotify)
        except SpotifyError as e:
            self.error(str(e))

    @pynvim.function("SpotifyCompletions", sync=True)
    def spotify_completions(self, args):
        arglead, cmdline, cursorpos, *_ = args
        return [
            option
            for option, _ in OPTIONS
            if option.lower().startswith(arglead.lower())
        ]
