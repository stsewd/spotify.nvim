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


OPTIONS = [
    ('play/pause', 'PlayPause'),
    ('next', 'Next'),
    ('prev', 'Previous'),
    ('play', 'Play'),
    ('pause', 'Pause'),
    ('stop', 'Stop'),
    ('status', '_show_current_status'),
]

OPTIONS_DICT = dict(OPTIONS)


def setup_spotify(fun):
    def wrapper(self, *args, **kwargs):
        self.spotify = _get_spotify_proxy()
        if not self.spotify:
            self.error('Spotify is not running')
            return
        return fun(self, *args, **kwargs)
    return wrapper


def _get_spotify_proxy():
    bus = SessionBus()
    try:
        proxy = bus.get(
            'org.mpris.MediaPlayer2.spotify',
            '/org/mpris/MediaPlayer2'
        )
        return proxy
    except Exception:
        return None


@neovim.plugin
class SpotifyNvim:

    def __init__(self, nvim):
        self.nvim = nvim
        self.spotify = None
        self.show_status = self.nvim.vars.get('spotify_show_status', 1)
        self.wait_time = self.nvim.vars.get('spotify_wait_time', 0.2)

    def _show_current_status(self):
        data = self.spotify.Metadata
        song = data.get('xesam:title', 'No Title')
        artists = data.get('xesam:artist', ['Unknow'])
        status = self.spotify.PlaybackStatus
        self._show_status(
            status=status, song=song, artists=artists
        )

    def _show_status(self, *, status, song, artists):
        self.nvim.out_write('[{status}] {song} - {artists}\n'.format(
            status=status,
            song=song,
            artists=', '.join(artists)
        ))

    def error(self, msg):
        self.nvim.err_write('[spotify] {}\n'.format(msg))

    def print(self, msg):
        self.nvim.out_write('[spotify] {}\n'.format(msg))

    @neovim.command(
        'Spotify', nargs=1, complete='customlist,SpotifyCompletions')
    @setup_spotify
    def spotify_command(self, args):
        attr = OPTIONS_DICT.get(args[0])
        if attr:
            if attr.startswith('_'):
                method = getattr(self, attr)
            else:
                method = getattr(self.spotify, attr)

            method()
            if self.show_status and not attr.startswith('_'):
                # We need to wait to the previous
                # command to get executed
                time.sleep(self.wait_time)
                self._show_current_status()
        else:
            self.error('Invalid option')

    @neovim.function('SpotifyCompletions', sync=True)
    def spotify_completions(self, args):
        arglead, cmdline, cursorpos, *_ = args
        return [
            option
            for option, action in OPTIONS
            if option.lower().startswith(arglead.lower())
        ]
