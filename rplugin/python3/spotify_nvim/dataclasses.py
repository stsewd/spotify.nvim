import dataclasses


@dataclasses.dataclass
class TemplateItem:
    content: str = ""
    width: int = 0
    align: str = "left"
    shorten: bool = False


@dataclasses.dataclass
class PlaybackSymbols:
    playing: str
    paused: str
    stopped: str


@dataclasses.dataclass
class ShuffleSymbols:
    enabled: str
    disabled: str


@dataclasses.dataclass
class VolumeSymbols:
    muted: str
    low: str
    medium: str
    high: str


@dataclasses.dataclass
class SymbolsConfig:
    playback: PlaybackSymbols
    shuffle: ShuffleSymbols
    volume: VolumeSymbols


@dataclasses.dataclass
class PlaybackStates:
    playing: str
    paused: str
    stopped: str


@dataclasses.dataclass
class ShuffleStates:
    enabled: str
    disabled: str


@dataclasses.dataclass
class VolumeStates:
    muted: str
    low: str
    medium: str
    high: str


@dataclasses.dataclass
class StatesConfig:
    playback: PlaybackStates
    shuffle: ShuffleStates
    volume: VolumeStates


@dataclasses.dataclass
class ProgressbarConfig:
    marker: str
    filled: str
    remaining: str
    width: int


@dataclasses.dataclass
class NotificationConfig:
    refresh_interval: int
    cycle_speed: int
    initial_cycle_pause: int
    timeout: int
    template: list[list[TemplateItem]]
    symbols: SymbolsConfig
    states: StatesConfig
    progressbar: ProgressbarConfig
    width: int

    @classmethod
    def from_dict(cls, data):
        return cls(
            refresh_interval=data["refresh_interval"],
            cycle_speed=data["cycle_speed"],
            initial_cycle_pause=data["initial_cycle_pause"],
            timeout=data["timeout"],
            template=[
                [TemplateItem(**item) for item in line] for line in data["template"]
            ],
            symbols=SymbolsConfig(
                playback=PlaybackSymbols(**data["symbols"]["playback"]),
                shuffle=ShuffleSymbols(**data["symbols"]["shuffle"]),
                volume=VolumeSymbols(**data["symbols"]["volume"]),
            ),
            states=StatesConfig(
                playback=PlaybackStates(**data["states"]["playback"]),
                shuffle=ShuffleStates(**data["states"]["shuffle"]),
                volume=VolumeStates(**data["states"]["volume"]),
            ),
            progressbar=ProgressbarConfig(**data["progressbar"]),
            width=data["width"],
        )


@dataclasses.dataclass
class ShuffleContext:
    symbol: str
    state: str


@dataclasses.dataclass
class PlaybackContext:
    symbol: str
    state: str


@dataclasses.dataclass
class VolumeContext:
    symbol: str
    state: str
    value: int


@dataclasses.dataclass
class TimeContext:
    current: str
    duration: str


@dataclasses.dataclass
class AlbumContext:
    name: str
    artists: str
