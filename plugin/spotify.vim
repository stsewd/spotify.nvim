if exists('g:loaded_spotify')
  finish
endif

nnoremap <silent> <Plug>(spotify-next) :Spotify next<CR>
nnoremap <silent> <Plug>(spotify-prev) :Spotify prev<CR>
nnoremap <silent> <Plug>(spotify-play/pause) :Spotify play/pause<CR>
nnoremap <silent> <Plug>(spotify-open) :Spotify open<CR>
nnoremap <silent> <Plug>(spotify-status) :Spotify status<CR>

let g:loaded_spotify = 1
