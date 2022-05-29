"SHORTCUTS
" ; is :
" gcc comments out lines
" K shows documentation for variable (python)
" \g goes to definition (python)
" \r renames a variable under cursor (python)
" \u finds all usages of variable under cursor (Python)
" \r renames a variable under cursor (python)
" F5 toggles NERDTree
" F3 Toggles relative number
" F7 toggles line wrapping
" F4 toggles the minimap
" F6 toggles indent guidelines
" \ff triggers a search for text inside files, like sublime's ctrl+shift+f
" \[space], while in Quickfix, previews a result
" ctrl+p will fuzzy-search for files, like in sublime
" \ctrl+p will fuzzy-search most recent files
" ctrl+down, ctrl+up adds a second cursor above or below
" ctrl+n (in normal mode) is like ctrl+d in sublime (selects next occurence with new cursor)
" shift+right, shift+left selects one character to the right or the left

"Vanilla Shortcuts I like to remember:
" :tab split      Duplicates a tab

set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim' " This is the program that downloads all of our plugins...

" Plug 'skywind3000/vim-quickui' 

"Adds indent guide lines
Plugin 'Yggdroot/indentLine'
"Disable by default...
let g:indentLine_enabled = 0 
nmap <F6> : IndentLinesToggle <CR>

"https://github.com/mg979/vim-visual-multi
Plugin 'mg979/vim-visual-multi' "Multiple cursors
"    - select words with Ctrl-N (like Ctrl-d in Sublime Text/VS Code)
"    - create cursors vertically with Ctrl-Down/Ctrl-Up
"    - select one character at a time with Shift-Arrows


""ctrl+p will search for files
Plugin 'kien/ctrlp.vim'
let g:ctrlp_show_hidden = 1
"Fuzzy search recent files
nmap <leader><C-p> :CtrlPMRU<CR>


"fzf requires an external program to be installed
"Plugin 'junegunn/fzf.vim' "To quickly search for files..
""ctrl+p will search for files
"" nnoremap <C-p> :<C-u>FZF<CR>
"" Mapping selecting mappings
"nmap <leader><tab> <plug>(fzf-maps-n)
"xmap <leader><tab> <plug>(fzf-maps-x)
"omap <leader><tab> <plug>(fzf-maps-o)
"" Insert mode completion
"imap <c-x><c-k> <plug>(fzf-complete-word)
"imap <c-x><c-f> <plug>(fzf-complete-path)
"imap <c-x><c-l> <plug>(fzf-complete-line)

" let g:indentLine_color_gui = '#000000'
" let g:indentLine_setColors = 0

" Plugin 'gsiano/vmux-clipboard' " Allows us to synchronize yanks between separate VIM processes (useful in TMUX for example)
" let mapleader = ","
" map <silent> <leader>y :WriteToVmuxClipboard<cr>
" map <silent> <leader>p :ReadFromVmuxClipboard<cr>
" map <silent> y :WriteToVmuxClipboard<cr>
" map <silent> p :ReadFromVmuxClipboard<cr>

Plugin 'ronakg/quickr-preview.vim' " When in a Quickfix window (aka the search result preview window, like you'd see if using \u or \ff), let us use \[space] to preview a result in multiple lines

Plugin 'severin-lemaignan/vim-minimap' " Adds a minimap to vim. Can be seen by pressing 'F4'

" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" plugin on GitHub repo

""" I love incsearch, but it was slow when editing rp
" Plugin 'haya14busa/incsearch.vim'
" map /  <Plug>(incsearch-forward)
" map ?  <Plug>(incsearch-backward)
" map g/ <Plug>(incsearch-stay)

Plugin 'eugen0329/vim-esearch' " The vim-easysearch plugin. This plugin adds the ability to search for text in files with the \ff command

Plugin 'davidhalter/jedi-vim' " This adds python-specific refactoring abilities

Plugin 'nathanaelkane/vim-indent-guides'

" Plugin 'christoomey/vim-system-copy' "This doesn't seem to work...

" Plugin 'tpope/vim-fugitive' 

Plugin 'scrooloose/nerdtree' "File explorer. Get it by pressig F5

Plugin 'tpope/vim-commentary' "Allows commenting out code with 'gcc' etc

Plugin 'mhinz/vim-startify' "Shows the startup menu
" Plugin 'dkprice/vim-easygrep' "Currently disabled until I figure out a good way to use it
" plugin from http://vim-scripts.org/vim/scripts.html
" Plugin 'L9'
" Git plugin not hosted on GitHub

Plugin 'git://git.wincent.com/command-t.git'
" git repos on your local machine (i.e. when working on your own plugin)
" Plugin 'file:///home/gmarik/path/to/plugin'
" The sparkup vim script is in a subdirectory of this repo called vim.
" Pass the path to set the runtimepath properly.

Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
" Install L9 and avoid a Naming conflict if you've already installed a
" different version somewhere else.
" Plugin 'ascenator/L9', {'name': 'newL9'}

" https://github.com/mgedmin/taghelper.vim
Plugin 'mgedmin/taghelper.vim'
set statusline=%<%f\ %h%m%r\ %1*%{taghelper#curtag()}%*%=%-14.(%l,%c%V%)\ %P

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line
"
"
"
"
"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

set undofile "Persistent undo
set mouse=a
set nu
set paste
set cursorline

"Highlight all search results
set hlsearch

" noremap : ;
noremap ; :

" map [1;5A <C-Up>
" map [1;5B <C-Down>
" map [1;2D <S-Left>
" map [1;2C <S-Right>
" cmap [1;2D <S-Left>
" cmap [1;2C <S-Right>

set smartindent
set tabstop=4
set shiftwidth=4
set expandtab

" Better search highlight color: blue
	"hi Search ctermfg=NONE  ctermbg=blue
	hi Search ctermfg=white  ctermbg=blue

" Some styling; the vertical separators are ugly as hecklestein
	nmap <C-C> cp
" NOTE: To see all available colors, use :help cterm-colors
	set fillchars+=vert:\|
"set fillchars+=vert:\
" set fillchars+=vert:⁞
	hi VertSplit ctermbg=black ctermfg=darkgray
	hi VertSplit ctermbg=darkcyan ctermfg=black
	set fillchars=vert:\|
	hi LineNr ctermfg=darkcyan
	hi LineNr ctermfg=gray
	hi LineNr ctermfg=darkgray
	hi LineNr ctermbg=black
	hi CursorLineNR cterm=bold ctermfg=lightcyan

function ToggleWrap()
 if (&wrap == 1)
   set nowrap
 else
   set wrap
 endif
endfunction
map <F7> :call ToggleWrap()<CR>
map! <F9> ^[:call ToggleWrap()<CR>


"let us toggle paste mode with the shortcut key:
    set pastetoggle=<F2>
    set list "Initially, we're not in list mode, so we <F3
    nmap <F9> : set list! <CR> : hi ryan_tabs ctermfg=DarkGray <CR> : match ryan_tabs /\t/ <CR>
" Let us see tabs and spaces when we're NOT in paste mode...
    set showbreak=↪\ 
    set listchars=tab:▸\ 
    hi ryan_tabs ctermfg=DarkGray
    match ryan_tabs /\t/
" Toggle relative line number
    nmap <F3> : set invrelativenumber <CR>

" Toggle Minimap
    nmap <F4> : MinimapToggle <CR>

" Toggle NERDTree
    nmap <F5> : NERDTreeToggle <CR>

"""""""" The next section: Remeber the cursor position next time we open the same file
" FROM: https://vim.fandom.com/wiki/Restore_cursor_to_file_position_in_previous_editing_session
"               Tell vim to remember certain things when we exit
"                '10  :  marks will be remembered for up to 10 previously edited files
"                "100 :  will save up to 100 lines for each register
"                :20  :  up to 20 lines of command-line history will be remembered
"                %    :  saves and restores the buffer list
"                n... :  where to save the viminfo files
set viminfo='10,\"100,:20,%,n~/.viminfo
function! ResCur()
  if line("'\"") <= line("$")
    normal! g`"
    return 1
  endif
endfunction
augroup resCur
  autocmd!
  autocmd BufWinEnter * call ResCur()
augroup END

" Instead of having to type :q! have vim ask us 'Would you like to save? Yes or no'
set confirm

" Python JEDI plugin commands (from their git page)
" Look at the below to learn how to effectively use the JEDI plugin!
" \g goes to definition
" \r is to rename a variable
" \n shows all usages of a given variable
" control+space triggers intelligent autocompletion
" K shows documentation for a python function/class/module. Just like regular vim.
let g:jedi#goto_assignments_command = "<leader>g"
let g:jedi#documentation_command = "K"
let g:jedi#usages_command = "<leader>u"
let g:jedi#completions_command = "<C-Space>"
let g:jedi#rename_command = "<leader>r"
"I'm not sure what the next 3 do, so for now I'll comment them out...
" let g:jedi#goto_stubs_command = "<leader>s"
" let g:jedi#goto_command = "<leader>d"
" let g:jedi#goto_definitions_command = ""

" Save us from some lag and don't automatically show python function signatures; leave that for when we're using rp
let g:jedi#show_call_signatures = 0

" Disable swap files. This might be controversial, but I think .swp files might be more of a pain in the butt than they're worth...vim just never crashes...
" set noswapfile

"Enable autocompletion menu while typing vim commands (after pressing :)
"To do this, press 'tab'. For example, try :w[tab] and :write will be an option
set wildmenu

