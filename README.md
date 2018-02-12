# Spotify.nvim

Control Spotify from Neovim

## Requirements

- Linux operating system (this plugin doesn't work on Windows, and I not sure about Mac).
- [pydbus](https://github.com/LEW21/pydbus) (see [requirements](https://github.com/LEW21/pydbus#requirements)).
- [wmctrl](https://en.wikipedia.org/wiki/Wmctrl) (optional, required only for `open` command)
    - `sudo apt-get install wmctrl`
    - `sudo dnf install wmctrl`

## Install

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
  - `open`: focus Spotify window.
  - `status`: show current song and player status.

## Configuration

Show current song and player status after each command.

```vim
g:spotify_show_status = 1
```

Choose the style of the symbols in the status.

Options can be:

- `text`
- `ascii` (default)
- `emoji`

```vim
g:spotify_status_style = 'ascii'
```

Set the format of the status.

The available variables are:

- `status`: the current status (the style is decided by `g:spotify_status_style`).
- `song`: the current song name.
- `artists`: comma separated artists.
- `decorator`: only visible when a song is playing.

_Note_: this is a python format string.

```vim
g:spotify_status_format = '{status} {song} - {artists} {decorator}'
```

Time in milliseconds to wait to show the player status after each command.
_This is needed, since Spotify could return the previous state, no the current one_.

```vim
g:spotify_wait_time = 0.2
```

## Mappings example

```vim
nnoremap <C-s>n :Spotify next<CR>
nnoremap <C-s>p :Spotify prev<CR>
nnoremap <C-s>s :Spotify play/pause<CR>
nnoremap <C-s>o :Spotify open<CR>
nnoremap <C-s>c :Spotify status<CR>
```

## References

- https://specifications.freedesktop.org/mpris-spec/latest/Player_Interface.html
- https://github.com/LEW21/pydbus/blob/master/doc/tutorial.rst
