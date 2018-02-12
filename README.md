# Spotify.nvim

Control Spotify from Neovim.

![1](https://user-images.githubusercontent.com/4975310/36114436-055b913e-0ffe-11e8-93ef-37dc9f487852.png)
![2](https://user-images.githubusercontent.com/4975310/36114434-04f6c1e6-0ffe-11e8-9232-eda34f5e0e65.png)
![3](https://user-images.githubusercontent.com/4975310/36114432-04d2de0c-0ffe-11e8-97f0-9b1fb287a20b.png)
![4](https://user-images.githubusercontent.com/4975310/36114431-04a225dc-0ffe-11e8-9085-edc6e60438fe.png)
![5](https://user-images.githubusercontent.com/4975310/36114430-04811716-0ffe-11e8-8291-4a8bb03a466c.png)
![6](https://user-images.githubusercontent.com/4975310/36114429-045eb676-0ffe-11e8-86cd-e180dc04b605.png)
![7](https://user-images.githubusercontent.com/4975310/36114427-043f8e22-0ffe-11e8-9506-cf72f390af1b.png)
![8](https://user-images.githubusercontent.com/4975310/36114426-04195d60-0ffe-11e8-8e1f-fcbf35ec38fd.png)

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
g:spotify_status_format = ' {status} {song} - {artists} {decorator}'
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
