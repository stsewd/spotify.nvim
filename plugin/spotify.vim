if exists('g:loaded_spotify')
  finish
endif

nnoremap <silent> <Plug>(spotify-next) :Spotify next<CR>
nnoremap <silent> <Plug>(spotify-prev) :Spotify prev<CR>
nnoremap <silent> <Plug>(spotify-play/pause) :Spotify play/pause<CR>
nnoremap <silent> <Plug>(spotify-show) :Spotify show<CR>
nnoremap <silent> <Plug>(spotify-status) :Spotify status<CR>

" Workardoun for https://github.com/neovim/pynvim/pull/496
autocmd VimEnter * ++once call Spotify__DummyStart()

let g:loaded_spotify = 1
