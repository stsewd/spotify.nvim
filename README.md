# Spotify.nvim

Control Spotify from Neovim.

![1](https://user-images.githubusercontent.com/4975310/184558071-58685fed-4fba-459b-a0fd-061981c1ea34.png)
![2](https://user-images.githubusercontent.com/4975310/184558074-bbd5ebd9-39c6-4b69-a579-7d7f28f44f7d.png)

*Showing status using [nvim-notify](https://github.com/rcarriga/nvim-notify)*

## Requirements

- Linux operating system (this plugin doesn't work on Windows, and I not sure about Mac).
- [pydbus](https://github.com/LEW21/pydbus) (see [requirements](https://github.com/LEW21/pydbus#requirements)).
  - If you are using pyenv to manage your Python provider, make sure you use:
    `pyenv virtualenv --system-site-packages system neovim` to create it.
- [wmctrl](https://en.wikipedia.org/wiki/Wmctrl) (optional, required only for the `show` command)
    - `sudo apt-get install wmctrl`
    - `sudo dnf install wmctrl`

## Installation

Install using [vim-plug](https://github.com/junegunn/vim-plug).
Put this on your `init.vim`.

```vim
Plug 'stsewd/spotify.nvim', { 'do': ':UpdateRemotePlugins' }
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
  - `time [value]`: Set the time of the current song to `value`.
     The value is given in seconds,
     you can prefix the value with `+` or `-`
     to change the time relatively to the current value.
  - `shuffle [value]`: De/activate shuffle.
     The value can be `on` or `off`,

## Configuration

### Show the player status after each command

```vim
g:spotify_show_status = 1
```

### Symbols used in the player status

See [below for inspiration](#inspiration-for-symbols).

```vim
let g:spotify_symbols = {
    \ "playing": "▶",
    \ "paused": "⏸",
    \ "stopped": "■",
    \ "volume.high": "🔊",
    \ "volume.medium": "🔉",
    \ "volume.low":  "🔈",
    \ "volume.muted": "🔇",
    \ "shuffle.enabled": "⤮ [on]",
    \ "shuffle.disabled": "⤮ [off]",
    \ "progress.mark": "●",
    \ "progress.complete": "─",
    \ "progress.missing": "┈",
    \}
```

### Template of the player status

The template is given by a list,
where each element represents a line.
And each element can be a template block or a list of of template blocks.

A template block is a dictionary with the folloing options:

- `template`: A string that would be evaluated using the `.format()` Python method.
- `align`: Alignment of the template, can be empty, left or center.
- `shorten`: A boolean value, if it's `true` and the evaluated template is larger than `width`,
  the value will be truncated.

The variables you can use inside a template are:

- `status`: the current status (playing, paused, stopped).
- `status_symbol`: the symbol from `spotify_symbols`.
- `title`: the title of the song.
- `artists`: comma separated artists.
- `album_name`: the name of the album.
- `album_artists`: comma separated artists.
- `shuffle_symbol`: the symbol from `spotify_symbols`.
- `volume`: the current volume level (0 to 100).
- `volume_symbol`: the symbol from `spotify_symbols`.
- `time`: the current time of the song in mm:ss format.
- `length`: the length of the song in mm:ss format.
- `progress_bar`: progress bar.

```vim
let g:spotify_template = [
   \   {
   \       "template": " 🎶 {title}",
   \       "shorten": v:true,
   \   },
   \   {
   \       "template": " 🎨 {artists}",
   \       "shorten": v:true,
   \   },
   \   {
   \       "template": " 💿 {album_name}",
   \       "shorten": v:true,
   \   },
   \   {},
   \   [
   \           {
   \               "template": "  {shuffle_symbol}",
   \               "align": "center",
   \           },
   \           {
   \               "template": "{status_symbol}",
   \               "align": "center",
   \           },
   \           {
   \               "template": "{volume_symbol} {volume}%  ",
   \               "align": "center",
   \           }
   \   ],
   \   {},
   \   {
   \       "template": "{time} / {length}",
   \       "align": "center",
   \   },
   \   {
   \       "template": "{progress_bar}",
   \       "align": "center",
   \   }
   \]
```

### Status width

Used when rendering the template from `spotify_template`.

```vim
g:spotify_width = 34
```

### Progress bar width

The width of the progress bar used when rendering the template from `spotify_template`.

```vim
g:spotify_progress_bar_width = 32
```

### Wait time

Time in milliseconds to wait to show the player status after each command.

_This is needed, since DBus/Spotify takes some time applying a change_.

```vim
g:spotify_wait_time = 0.2
```

## Mappings example

```vim
nmap <leader>ss <Plug>(spotify-play/pause)
nmap <leader>sj <Plug>(spotify-next)
nmap <leader>sk <Plug>(spotify-prev)
nmap <leader>so <Plug>(spotify-show)
nmap <leader>sc <Plug>(spotify-status)
```

## Inspiration for symbols

- playing: ▶ ▶️
- paused: ⏸ ⏸️
- stopped: ■ ⏹️
- album: 💿︎💿
- artist: © 🎨
- music: ♫♪ 🎶
- volume: ∅ 🕨 🕩 🕪  🔇 🔈 🔉 🔊
- shuffle: ⤮ 🔀

## References

- https://specifications.freedesktop.org/mpris-spec/latest/index.html
- https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html
- https://github.com/LEW21/pydbus/blob/master/doc/tutorial.rst
