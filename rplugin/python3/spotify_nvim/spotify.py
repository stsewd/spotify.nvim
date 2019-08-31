import logging
import os
import sys

from .windowctrl import WindowCtrlError, focus_program

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

    def show_window(self):
        try:
            focus_program('spotify')
        except WindowCtrlError as e:
            raise SpotifyError(str(e))

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
