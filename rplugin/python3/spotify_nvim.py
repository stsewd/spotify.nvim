import neovim

from gi.repository import GLib
from pydbus import SessionBus

SPOTIFY_OPTIONS = [
    'PlayPause',
    'Next',
    'Previous',
    'Play',
    'Pause',
    'Stop',
    'Shuffle',
    'Metadata',
]


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

    @neovim.command(
        'Spotify', nargs='1', complete='customlist,SpotifyCompletions')
    def spotify_command(self, args):
        attr = args[0]
        if hasattr(self.spotify, attr):
            method = getattr(self.spotify, attr)
            if callable(method):
                method()
                return
        self.nvim.err_write('[spotify] Invalid option\n')

    @neovim.function('SpotifyCompletions', sync=True)
    def spotify_completions(self, args):
        arglead, cmdline, cursorpos, *_ = args
        return [
            option
            for option in SPOTIFY_OPTIONS
            if option.lower().startswith(arglead.lower())
        ]
