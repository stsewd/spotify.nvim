import neovim

import os
import sys
import time

try:
    from pydbus import SessionBus
except ImportError:
    # Try to import from python system packages
    sys.path.insert(0, os.path.abspath('/usr/lib/python3.6/site-packages'))
    sys.path.insert(0, os.path.abspath('/usr/lib64/python3.6/site-packages'))
    from pydbus import SessionBus


SPOTIFY_OPTIONS = [
    ('play/pause', 'PlayPause'),
    ('next', 'Next'),
    ('prev', 'Previous'),
    ('play', 'Play'),
    ('pause', 'Pause'),
    ('stop', 'Stop'),
    ('status', '_show_current_status'),
]

SPOTIFY_OPTIONS_DICT = dict(SPOTIFY_OPTIONS)


@neovim.plugin
class SpotifyNvim:

    def __init__(self, nvim):
        self.nvim = nvim
        self.spotify = self._get_spotify_proxy()

    def _get_spotify_proxy(self):
        bus = SessionBus()
        proxy = bus.get(
            'org.mpris.MediaPlayer2.spotify',
            '/org/mpris/MediaPlayer2'
        )
        return proxy

    def _show_status(self, *, status, song, artists):
        self.nvim.out_write('[{status}] {song} - {artists}\n'.format(
            status=status,
            song=song,
            artists=', '.join(artists)
        ))

    def _show_current_status(self):
        data = self.spotify.Metadata
        song = data.get('xesam:title', 'No Title')
        artists = data.get('xesam:artist', ['Unknow'])
        status = self.spotify.PlaybackStatus
        self._show_status(
            status=status, song=song, artists=artists
        )

    def error(self, msg):
        self.nvim.err_write('[spotify] {}\n'.format(msg))

    def print(self, msg):
        self.nvim.out_write('[spotify] {}\n'.format(msg))

    @neovim.command(
        'Spotify', nargs='1', complete='customlist,SpotifyCompletions')
    def spotify_command(self, args):
        attr = SPOTIFY_OPTIONS_DICT.get(args[0])
        if attr:
            if attr.startswith('_'):
                method = getattr(self, attr)
            else:
                method = getattr(self.spotify, attr)
            if callable(method):
                method()
                if not attr.startswith('_'):
                    # We need to wait to the previous command to get executed
                    time.sleep(0.1)
                    self._show_current_status()
                return
        self.error('Invalid option')

    @neovim.function('SpotifyCompletions', sync=True)
    def spotify_completions(self, args):
        arglead, cmdline, cursorpos, *_ = args
        return [
            option
            for option, action in SPOTIFY_OPTIONS
            if option.lower().startswith(arglead.lower())
        ]
