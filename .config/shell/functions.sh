e() { emacsclient -nw "$@"; }

proj() {
  local dir
  dir=$(find ~/Source -maxdepth 3 -name ".git" 2>/dev/null \
        | sed 's|/.git$||' \
        | fzf --preview 'ls {}')
  [ -n "$dir" ] && cd "$dir"
}

pf() {
  local file
  file=$(git ls-files | fzf --preview 'cat {}')
  [ -n "$file" ] && ${EDITOR} "$file"
}

groot() {
  cd "$(git rev-parse --show-toplevel)"
}
