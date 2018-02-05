# Spotify.nvim

Control Spotify from Neovim

## Requirements

- Linux operating system (this plugin doesn't work on Windows, and I not sure about Mac).
- [pydbus](https://github.com/LEW21/pydbus) (see [requirements](https://github.com/LEW21/pydbus#requirements)).

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
  - `status`: show current song and player status.

## Configuration

Show current song and player status after each command.

```vim
g:spotify_show_status = 1
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
nnoremap <C-s>c :Spotify status<CR>
```
