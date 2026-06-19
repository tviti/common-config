e() { emacsclient -nw "$@"; }

p() {
  local dir
  dir=$(find ~/Source ~/ -maxdepth 3 -name ".git" 2>/dev/null \
        | sed 's|/.git$||' \
        | sort -u \
        | fzf --preview 'ls {}')
  [ -n "$dir" ] && cd "$dir"
}

pf() {
  local file
  file=$(git ls-files | fzf --preview 'cat {}')
  [ -n "$file" ] && ${EDITOR} "$file"
}

pd() {
  local root=$(git rev-parse --show-toplevel 2>/dev/null) || return 1
  local dir=$(find "$root" -type d -not -path '*/.git/*' | fzf) || return 0
  cd "$dir"
}
groot() {
  cd "$(git rev-parse --show-toplevel)"
}
