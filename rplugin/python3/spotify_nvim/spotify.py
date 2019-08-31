import logging
import os
import sys
from subprocess import PIPE, Popen

try:
    from pydbus import SessionBus
except ImportError:
    # Try to import from python system packages
    sys.path.insert(0, os.path.abspath('/usr/lib/python3.7/site-packages'))
    sys.path.insert(0, os.path.abspath('/usr/lib64/python3.7/site-packages'))
    from pydbus import SessionBus

log = logging.getLogger(__name__)


class SpotifyError(Exception):

    pass


class Spotify:

    def __init__(self):
        self.session_bus = self._get_session_bus()

    def _get_session_bus(self):
        bus = SessionBus()
        try:
            proxy = bus.get(
                'org.mpris.MediaPlayer2.spotify',
                '/org/mpris/MediaPlayer2'
            )
            return proxy
        except Exception as e:
            log.info('Failed to load session bus: %s', str(e))
            raise SpotifyError('Spotify is not running')

    def _get_spotify_pids(self):
        command = ['pgrep', 'spotify']
        with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
            output, error = proc.communicate()
            return output.decode().split('\n')
        return []


    def _get_window_id(self, pids):
        command = [
            'wmctrl',
            '-l',  # list windows
            '-p',  # show pids
        ]
        with Popen(command, stdout=PIPE, stderr=PIPE) as proc:
            output, error = proc.communicate()
            windows = (
                window
                for window in output.decode().split('\n')
                if window
            )
            for window in windows:
                window_id, workspace, pid, *_ = window.split()
                if pid in pids:
                    return window_id
        return None


    def _focus_window(self, window_id):
        command = [
            'wmctrl',
            '-i',  # search by id
            '-a',  # search
            window_id,
        ]
        with Popen(command, stderr=PIPE) as proc:
            output, error = proc.communicate()

    def show_window(self):
        spotify_pids = self._get_spotify_pids()
        if not spotify_pids:
            raise SpotifyError('Spotify is not running')
        window_id = self._get_window_id(spotify_pids)
        if window_id:
            self._focus_window(window_id)
        else:
            raise SpotifyError(
                'Unable to find Spotify process, '
                'make sure you have wmctrl installed'
            )

    def play(self):
        self.session_bus.Play()

    def pause(self):
        self.session_bus.Pause()

    def toggle(self):
        self.session_bus.PlayPause()

    def stop(self):
        self.session_bus.Stop()

    def next(self):
        self.session_bus.Next()

    def prev(self):
        self.session_bus.Previous()

    def get_status(self):
        data = self.session_bus.Metadata
        song = data.get('xesam:title', 'No Title')
        artists = data.get('xesam:artist', ['Unknow'])
        status = self.session_bus.PlaybackStatus
        return (status, song, artists)
