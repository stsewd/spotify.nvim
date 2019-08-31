import time

import pynvim

from .constants import OPTIONS, SYMBOLS_REPR
from .spotify import Spotify, SpotifyError


@pynvim.plugin
class SpotifyNvimPlugin:

    def __init__(self, nvim):
        self.nvim = nvim

    @property
    def settings(self):
        settings = {
            'show_status': self.nvim.vars.get(
                'spotify_show_status', 1,
            ),
            'wait_time': self.nvim.vars.get(
                'spotify_wait_time', 0.2,
            ),
            'status_style': self.nvim.vars.get(
                'spotify_status_style', 'ascii',
            ),
            'status_format': self.nvim.vars.get(
                'spotify_status_format',
                ' {status} {song} - {artists} {decorator}',
            ),
        }
        return settings

    def _show_current_status(self, spotify):
        status, song, artists = spotify.get_status()

        decorator = ''
        if status.lower() == 'playing':
            decorator = self._get_symbol_repr('music')
        status_format = self.settings['status_format'] + '\n'
        self.nvim.out_write(
            status_format.format(
                status=self._get_symbol_repr(status),
                song=song,
                artists=', '.join(artists),
                decorator=decorator,
            ),
        )

    def _get_symbol_repr(self, symbol):
        symbol = symbol.lower()
        repr_ = (
            SYMBOLS_REPR
            .get(symbol, {})
            .get(self.settings['status_style'], '')
        )
        return repr_

    def error(self, msg):
        self.nvim.err_write(f'[spotify] {msg}\n')

    def print(self, msg):
        self.nvim.out_write(f'[spotify] {msg}\n')

    @pynvim.command(
        'Spotify',
        nargs=1,
        complete='customlist,SpotifyCompletions',
    )
    def spotify_command(self, args):
        try:
            attr = dict(OPTIONS).get(args[0])
            if not attr:
                self.error('Invalid option')
                return

            spotify = Spotify()
            if attr.startswith('_'):
                getattr(self, attr)(spotify)
            else:
                getattr(spotify, attr)()

            if (
                self.settings['show_status']
                and attr not in ('show_window', '_show_current_status')
            ):
                # We need to wait to the previous
                # command to get executed
                time.sleep(self.settings['wait_time'])
                self._show_current_status(spotify)
        except SpotifyError as e:
            self.error(str(e))

    @pynvim.function('SpotifyCompletions', sync=True)
    def spotify_completions(self, args):
        arglead, cmdline, cursorpos, *_ = args
        return [
            option
            for option, action in OPTIONS
            if option.lower().startswith(arglead.lower())
        ]
