# Spotify.nvim

Control Spotify from Neovim.

![1](https://github.com/user-attachments/assets/e8298d39-78f8-4c49-a73b-7e6ffae5f936)
![2](https://github.com/user-attachments/assets/02973f67-f35c-4582-b489-1b206fb61aac)

_Showing status using [snacks.nvim's notifier](https://github.com/folke/snacks.nvim/blob/main/docs/notifier.md)_

## Requirements

- Linux operating system (this plugin doesn't work on Windows, and I not sure about Mac).
- [pydbus](https://github.com/LEW21/pydbus) (see [requirements](https://github.com/LEW21/pydbus#requirements)).
  - If you are using pyenv to manage your Python provider, make sure you use:
    `pyenv virtualenv --system-site-packages system neovim` to create it.
  - If you are using uv, use: `uv venv --python-preference system --system-site-packages`.
- [wmctrl](https://en.wikipedia.org/wiki/Wmctrl) (optional, required only for the `show` command)
  - `sudo apt-get install wmctrl`
  - `sudo dnf install wmctrl`
- [nvim-notify](https://github.com/rcarriga/nvim-notify) or [snacks.nvim's notifier](https://github.com/folke/snacks.nvim/blob/main/docs/notifier.md)
  for fancy asynchronous notifications.

## Installation

Install using [lazy.nvim](https://github.com/folke/lazy.nvim):

```lua
{
  "stsewd/spotify.nvim",
  build = ":UpdateRemotePlugins",
  config = function()
    require("spotify").setup()
  end,
  init = function()
    -- Optional mappings.
    vim.keymap.set("n", "<leader>ss", ":Spotify play/pause<CR>", { silent = true })
    vim.keymap.set("n", "<leader>sj", ":Spotify next<CR>", { silent = true })
    vim.keymap.set("n", "<leader>sk", ":Spotify prev<CR>", { silent = true })
    vim.keymap.set("n", "<leader>so", ":Spotify show<CR>", { silent = true })
    vim.keymap.set("n", "<leader>sc", ":Spotify status<CR>", { silent = true })
  end,
},
```

## Usage

- Start Spotify.
- Call `:Spotify {option}`. Where option can be:
  - `play/pause`
  - `next`
  - `prev`
  - `play`
  - `pause`
  - `stop`
  - `show`: Focus Spotify window
  - `status`: Show current song and player status
  - `volume [value]`: Set the volume to `value`.
    The value is a number from 0 to 100,
    you can prefix the value with `+` or `-`
    to change the volume relatively to the current value.
    You can repeat `-`/`+` to change the volume by increments of 5.
  - `time [value]`: Set the time of the current song to `value`.
    The value is given in seconds,
    you can prefix the value with `+` or `-`
    to change the time relatively to the current value.
    You can repeat `-`/`+` to change the time by increments of 5.
  - `shuffle [value]`: De/activate shuffle.
    The value can be: `on`, `off`, `toggle`.
    If no value is given, it will default to `toggle`.

## Configuration

```lua
require("spotify").setup({
  -- Whether to show status after an action is executed using the :Spotify command.
  notify_after_action = true,
  defaults = {
    -- The numeric value that represents each -/+ volume increment.
    volume_increment = 5,
    -- The numeric value that represents each -/+ time increment.
    time_increment = 5,
    -- The default action to take when :Spotify shuffle is called.
    shuffle = "toggle",
  },
  notification = {
    -- The notification backend to use. Can be "builtin", "notify", "snacks", or "auto".
    backend = "auto",
    -- Extra options to pass to the vim.notify function.
    extra_opts = {},
    -- The inverval that the notification will be updated (in milliseconds).
    refresh_interval = 100,
    -- How many refresh intervals to cycle through the text that doesn't fit in the notification.
    cycle_speed = 2,
    -- How many refresh intervals to wait before cycling through the text that doesn't fit in the notification.
    initial_cycle_pause = 5,
    -- The timeout for the notification (in milliseconds).
    timeout = 4000,
    -- The width of text in the notification.
    width = 44,
    -- A template to format the notification text.
    -- The template is a list of lists of tables, where each table represents a line of text,
    -- and each line is a list of tables, where each table represents a block of text.
    -- Each block of text can have the following keys:
    --  - content: The text to display.
    --  - width: The width of the block of text, if not specified, the width will be calculated based on the width of the whole line.
    --  - shorten: Whether to truncate the text if it doesn't fit in the block, the text will cycle on each refresh interval.
    --  - align: The alignment of the text in the block, can be "left", "center", or "right".
    --
    --  The content can have the following placeholders:
    --  - {title}: The title of the current track.
    --  - {artists}: The artists of the current track separated by commas.
    --  - {album.name}: The name of the album of the current track.
    --  - {album.artists}: The artists of the album of the current track separated by commas.
    --  - {shuffle.symbol}: The symbol for the shuffle state (as given in the symbols.shuffle table).
    --  - {shuffle.state}: The state of the shuffle (as given in the states.shuffle table).
    --  - {playback.symbol}: The symbol for the playback state (as given in the symbols.playback table).
    --  - {playback.state}: The state of the playback (as given in the states.playback table).
    --  - {volume.symbol}: The symbol for the volume state (as given in the symbols.volume table).
    --  - {volume.state}: The state of the volume (as given in the states.volume table).
    --  - {volume.value}: The value of the volume (from 0 to 100).
    --  - {time.current}: The current time of the track in the format "mm:ss".
    --  - {time.duration}: The duration of the track in the format "mm:ss".
    --  - {progressbar}: A progress bar that represents the current time of the track (as given in the progressbar table).
    template = {
      {
        {
          content = "🎶",
          width = 2,
        },
        {
          content = "{title}",
          shorten = true,
        },
      },
      {
        {
          content = "👥",
          width = 2,
        },
        {
          content = "{artists}",
          shorten = true,
        },
      },
      {
        {
          content = "💿",
          width = 2,
        },
        {
          content = "{album.name}",
          shorten = true,
        },
      },
      {},
      {
        {
          content = "",
          width = 5,
        },
        {
          content = "{shuffle.symbol} {shuffle.state}",
          align = "left",
        },
        {
          content = "{playback.symbol}",
          align = "center",
        },
        {
          content = "{volume.symbol} {volume.value}%",
          align = "right",
        },
        {
          content = "",
          width = 5,
        },
      },
      {},
      {
        {
          content = "{time.current} / {time.duration}",
          align = "center",
        },
      },
      {
        {
          content = "{progressbar}",
          align = "center",
        },
      },
    },
    symbols = {
      playback = {
        playing = "▶",
        paused = "⏸",
        stopped = "■",
      },
      shuffle = {
        enabled = "🔀",
        disabled = "⤭",
      },
      volume = {
        muted = "🔇",
        low = "🔈",
        medium = "🔉",
        high = "🔊",
      },
    },
    states = {
      playback = {
        playing = "playing",
        paused = "paused",
        stopped = "stopped",
      },
      shuffle = {
        enabled = "on",
        disabled = "off",
      },
      volume = {
        muted = "muted",
        low = "low",
        medium = "medium",
        high = "high",
      },
    },
    progressbar = {
      marker = "●",
      filled = "─",
      remaining = "┈",
      width = 40,
    },
  },
})
```

## Configuration examples

### Put the Spotify logo in the notification

This requires a [nerd font](https://www.nerdfonts.com/) to be installed.

```lua
require("spotify").setup(
  notification = {
    extra_opts = {
      icon = "",
    },
  },
)
```

### Make the notification less wider

```lua
require("spotify").setup(
  notification = {
    width = 34,
    progressbar = {
      width = 30,
    },
  },
)
```

## Inspiration for symbols

- playing: ▶ ▶️
- paused: ⏸ ⏸️
- stopped: ■ ⏹️
- album: 💿︎💿
- artist: © 🎨 👥
- music: ♫♪ 🎶
- volume: ∅ 🕨 🕩 🕪 🔇 🔈 🔉 🔊
- shuffle: ⤮ 🔀

## References

- https://specifications.freedesktop.org/mpris-spec/latest/index.html
- https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html
- https://github.com/LEW21/pydbus/blob/master/doc/tutorial.rst
