import os
import sys
import time
from subprocess import PIPE, Popen

import neovim

try:
    from pydbus import SessionBus
except ImportError:
    # Try to import from python system packages
    sys.path.insert(0, os.path.abspath('/usr/lib/python3.7/site-packages'))
    sys.path.insert(0, os.path.abspath('/usr/lib64/python3.7/site-packages'))
    from pydbus import SessionBus


OPTIONS = [
    ('play/pause', 'PlayPause'),
    ('next', 'Next'),
    ('prev', 'Previous'),
    ('play', 'Play'),
    ('pause', 'Pause'),
    ('stop', 'Stop'),
    ('show', '_show_spotify'),
    ('status', '_show_current_status'),
]
OPTIONS_DICT = dict(OPTIONS)

SYMBOLS_REPR = {
    'playing': {
        'text': '[playing]',
        'ascii': '►',
        'emoji': '▶️',
    },
    'paused': {
        'text': '[paused]',
        'ascii': '■',
        'emoji': '⏸️',
    },
    'stopped': {
        'text': '[stopped]',
        'ascii': '■',
        'emoji': '⏸️',
    },
    'music': {
        'text': '',
        'ascii': '♫♪',
        'emoji': '🎶',
    }
}


def setup_spotify(fun):
    def wrapper(self, *args, **kwargs):
        self.spotify = get_spotify_proxy()
        if not self.spotify:
            self.error('Spotify is not running')
            return
        return fun(self, *args, **kwargs)
    return wrapper


def get_spotify_proxy():
    bus = SessionBus()
    try:
        proxy = bus.get(
            'org.mpris.MediaPlayer2.spotify',
            '/org/mpris/MediaPlayer2'
        )
        return proxy
    except Exception:
        return None


def get_spotify_pids():
    command = ['pgrep', 'spotify']
    with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
        output, error = proc.communicate()
        return output.decode().split('\n')
    return []


def get_window_id(pids):
    command = [
        'wmctrl',
        '-l',  # list windows
        '-p',  # show pids
    ]
    with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
        output, error = proc.communicate()
        windows = output.decode().split('\n')
        for window in windows:
            window_id, workspace, pid, *_ = window.split()
            if pid in pids:
                return window_id
    return None


def focus_window(window_id):
    command = [
        'wmctrl',
        '-i',  # search by id
        '-a',  # search
        window_id,
    ]
    with Popen(command, stderr=PIPE) as proc:
        output, error = proc.communicate()


@neovim.plugin
class SpotifyNvim:

    def __init__(self, nvim):
        self.nvim = nvim
        self.spotify = None
        self.show_status = self.nvim.vars.get('spotify_show_status', 1)
        self.wait_time = self.nvim.vars.get('spotify_wait_time', 0.2)
        self.status_style = self.nvim.vars.get('spotify_status_style', 'ascii')
        self.status_format = self.nvim.vars.get(
            'spotify_status_format',
            ' {status} {song} - {artists} {decorator}'
        )

    def _show_current_status(self):
        data = self.spotify.Metadata
        song = data.get('xesam:title', 'No Title')
        artists = data.get('xesam:artist', ['Unknow'])
        status = self.spotify.PlaybackStatus
        self._show_status(
            status=status, song=song, artists=artists
        )

    def _show_status(self, *, status, song, artists):
        decorator = ''
        if status.lower() == 'playing':
            decorator = self._get_symbol_repr('music')
        status_format = self.status_format + '\n'
        self.nvim.out_write(status_format.format(
            status=self._get_symbol_repr(status),
            song=song,
            artists=', '.join(artists),
            decorator=decorator
        ))

    def _get_symbol_repr(self, symbol):
        symbol = symbol.lower()
        repr_ = (
            SYMBOLS_REPR
            .get(symbol, {})
            .get(self.status_style, '')
        )
        return repr_

    def _show_spotify(self):
        try:
            spotify_pids = get_spotify_pids()
            window_id = get_window_id(spotify_pids)
            if window_id:
                focus_window(window_id)
            else:
                self.error('Spotify is not running')
        except Exception as e:
            self.error('You need to install wmctrl to use this feature')

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
