import logging

from pydbus import SessionBus

from .windowctrl import WindowCtrlError, focus_program

log = logging.getLogger(__name__)


class SpotifyError(Exception):

    pass


class Spotify:
    def __init__(self):
        self.session_bus = self._get_session_bus()

    def _get_session_bus(self):
        bus = SessionBus()
        try:
            proxy = bus.get("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
            return proxy
        except Exception as e:
            log.info("Failed to load session bus: %s", str(e))
            raise SpotifyError("Spotify is not running")

    def show_window(self):
        try:
            focus_program("spotify")
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

    def _get_relative_value(self, value, increment=10):
        return value + increment

    @property
    def volume(self):
        return int(self.session_bus.Volume * 100)

    @volume.setter
    def volume(self, value):
        """Value from 0 to 100, can be relative."""
        if value.startswith("+") or value.startswith("-"):
            self.session_bus.Volume = self.session_bus.Volume + int(value) / 100
        else:
            self.session_bus.Volume = int(value) / 100

    @property
    def shuffle(self):
        return self.session_bus.Shuffle

    @shuffle.setter
    def shuffle(self, value):
        self.session_bus.Shuffle = value

    @property
    def length(self):
        return self.session_bus.Metadata["mpris:length"] // (10**6)

    @property
    def time(self):
        return self.session_bus.Position // (10**6)

    @time.setter
    def time(self, value: str):
        """Value in seconds, can be relative."""
        if value.startswith("+") or value.startswith("-"):
            self.session_bus.Seek(int(value) * 10**6)
        else:
            meta = self.session_bus.Metadata
            id = meta["mpris:trackid"]
            self.session_bus.SetPosition(id, int(value) * 10**6)

    @property
    def status(self):
        return self.session_bus.PlaybackStatus.lower()

    def metadata(self, defaults=True):
        keys = [
            ("id", "mpris:trackid", None),
            ("title", "xesam:title", "No Title"),
            ("artists", "xesam:artist", ["Unknow"]),
            ("album.name", "xesam:album", "No Title"),
            ("album.artists", "xesam:albumArtist", ["Unknow"]),
            ("url", "xesam:url", None),
        ]
        metadata = self.session_bus.Metadata
        return {
            name: metadata.get(key, default if defaults else None)
            for name, key, default in keys
        }
