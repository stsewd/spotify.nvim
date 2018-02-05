import neovim

import os
import sys

try:
    from gi.repository import GLib
    from pydbus import SessionBus
except ImportError:
    sys.path.insert(0, os.path.abspath('/usr/lib/python3.6/site-packages'))
    sys.path.insert(0, os.path.abspath('/usr/lib64/python3.6/site-packages'))
    from gi.repository import GLib
    from pydbus import SessionBus


SPOTIFY_OPTIONS = [
    ('play/pause', 'PlayPause'),
    ('next', 'Next'),
    ('prev', 'Previous'),
    ('play', 'Play'),
    ('pause', 'Pause'),
    ('stop', 'Stop'),
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

    def _run_main_loop(self):
        loop = GLib.MainLoop()
        self.spotify.onPropertiesChanged = lambda x: print(x)
        loop.run()

    def error(self, msg):
        self.nvim.err_write('[spotify] {}\n'.format(msg))

    def msg(self, msg):
        self.nvim.out_write('[spotify] {}\n'.format(msg))

    @neovim.command(
        'Spotify', nargs='1', complete='customlist,SpotifyCompletions')
    def spotify_command(self, args):
        attr = SPOTIFY_OPTIONS_DICT.get(args[0])
        if attr:
            method = getattr(self.spotify, attr)
            if callable(method):
                method()
                return
        self.error('Invalid option')

    def _show_current_status(self):
        pass

    @neovim.function('SpotifyCompletions', sync=True)
    def spotify_completions(self, args):
        arglead, cmdline, cursorpos, *_ = args
        return [
            option
            for option, action in SPOTIFY_OPTIONS
            if option.lower().startswith(arglead.lower())
        ]
