#!/usr/bin/env bash

set -euo pipefail

backup_dir=''
backup_created=false
migration_started=false
migration_succeeded=false
created_worktrees=()

error() {
    printf 'error: %s\n' "$1" >&2
    exit 1
}

log() {
    printf 'worktree: %s\n' "$1"
}

write_readme() {
    printf '%s\n' \
        '# Git Worktree Layout' \
        '' \
        'This repository uses a shared bare Git repository and separate worktree' \
        'folders for each checked-out branch. The `.bare` folder contains the' \
        'shared Git history; `.git` points Git at it. Branch files live in the' \
        'worktree folders beside them.' \
        '' \
        '## Root commands' \
        '' \
        'Run these from the repository root.' \
        '' \
        '```bash' \
        '# List all worktrees' \
        'git worktree list' \
        '' \
        '# Remove references to worktrees deleted manually (e.g. with rm -rf)' \
        'git worktree prune' \
        '```' \
        '' \
        '## Worktree creation commands' \
        '' \
        'Also run from the repository root, unless creating a nested worktree.' \
        '' \
        '```bash' \
        '# Create a worktree for an existing branch (path, then branch)' \
        'git worktree add feature feature' \
        '' \
        '# Create a new branch and its worktree in one step' \
        'git worktree add -b experiment experiment' \
        '```' \
        '' \
        '### Nested worktree example' \
        '' \
        'Assuming `feat/` already exists because another worktree is at' \
        '`feat/something`, create a new branch and worktree from inside `feat/`:' \
        '' \
        '```bash' \
        'cd feat' \
        'git worktree add -b feat/example-feat-name example-feat-name' \
        '```' \
        '' \
        'This creates the branch `feat/example-feat-name` and the worktree at' \
        '`feat/example-feat-name`.' \
        '' \
        'The worktree folder and branch name do not have to match; Git treats' \
        'them as separate values. Keeping the same structure for both is good' \
        'practice, since it makes worktrees easier to identify and navigate.' \
        '' \
        '## Worktree commands' \
        '' \
        'Run these from inside a worktree folder.' \
        '' \
        '```bash' \
        '# Work in a branch' \
        'git status' \
        '' \
        '# Remove a worktree once its branch is no longer needed (run one' \
        '# level up, from the repository root)' \
        'cd ..' \
        'git worktree remove feature' \
        '```'
}

rollback() {
    local worktree

    if [ "$migration_succeeded" = true ] || [ "$backup_created" = false ]; then
        return
    fi

    set +e

    if [ "${#created_worktrees[@]}" -gt 0 ]; then
        for worktree in "${created_worktrees[@]}"; do
            git worktree remove --force "$worktree" >/dev/null 2>&1
            rm -rf -- "$worktree"
        done
    fi

    if [ "$migration_started" = true ]; then
        find . -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
        find "$backup_dir" -mindepth 1 -maxdepth 1 -exec cp -a {} . \
            \;
    fi

    rm -rf -- "$backup_dir"
}

trap rollback EXIT

repo_root=$(git rev-parse --show-toplevel 2>/dev/null) \
    || error 'worktree must run inside a git repository'
[ "$(pwd -P)" = "$(cd "$repo_root" && pwd -P)" ] \
    || error 'worktree must run from the repository root'
[ -d .git ] \
    || error 'repository is already converted or has an unsupported .git file'
[ ! -e .bare ] \
    || error '.bare already exists; refusing to overwrite it'

current_branch=$(git symbolic-ref --quiet --short HEAD) \
    || error 'detached HEAD is not supported'

backup_dir=$(dirname "$repo_root")/$(basename "$repo_root")-legacy-bak
[ ! -e "$backup_dir" ] \
    || error "backup path already exists: $backup_dir"
log "creating backup: $backup_dir"
mkdir "$backup_dir" \
    || error "unable to create backup directory: $backup_dir"
backup_created=true
cp -a "$repo_root"/. "$backup_dir"/ \
    || error "unable to copy the repository to: $backup_dir"
migration_started=true
log 'backup created'

log 'fetching remotes'
if ! git fetch --all; then
    error 'unable to fetch all remotes'
fi

if git remote get-url origin >/dev/null 2>&1; then
    git remote set-head origin -a >/dev/null 2>&1 \
        || error "unable to determine origin's default branch"
    default_ref=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD) \
        || error 'origin has no default branch'
    default_branch=${default_ref#origin/}
else
    default_branch=$current_branch
fi

[ ! -e "$default_branch" ] \
    || error "worktree path already exists: $default_branch"
if [ "$current_branch" != "$default_branch" ]; then
    [ ! -e "$current_branch" ] \
        || error "worktree path already exists: $current_branch"
fi

log "converting repository root for branch '$current_branch'"
mv .git .bare
printf 'gitdir: ./.bare\n' > .git
git config --file .bare/config core.bare true

find . -mindepth 1 -maxdepth 1 ! -name .bare ! -name .git \
    -exec rm -rf -- {} +
log 'original repository files removed from root'

if git show-ref --verify --quiet "refs/heads/$default_branch"; then
    log "creating worktree: $default_branch"
    git worktree add "$default_branch" "$default_branch" \
        >/dev/null 2>&1 \
        || error "unable to create worktree for $default_branch"
    created_worktrees+=("$default_branch")
else
    log "creating worktree: $default_branch"
    git worktree add --track -b "$default_branch" "$default_branch" \
        "origin/$default_branch" \
        >/dev/null 2>&1 \
        || error "unable to create worktree for $default_branch"
    created_worktrees+=("$default_branch")
fi

if [ "$current_branch" != "$default_branch" ]; then
    log "creating worktree: $current_branch"
    git worktree add "$current_branch" "$current_branch" \
        >/dev/null 2>&1 \
        || error "unable to create worktree for $current_branch"
    created_worktrees+=("$current_branch")
fi

current_worktree="$repo_root/$current_branch"
log "restoring original files to worktree: $current_branch"
if ! find "$backup_dir" -mindepth 1 -maxdepth 1 ! -name .git \
    -exec cp -a {} "$current_worktree"/ \;; then
    error "unable to restore the original files to: $current_worktree"
fi

log 'writing README.md'
if ! write_readme > README.md; then
    error 'unable to write README.md to the repository root'
fi
printf 'Worktree migration complete.\n'
printf 'Default branch: %s\n' "$default_branch"
[ "$current_branch" = "$default_branch" ] \
    || printf 'Current branch: %s\n' "$current_branch"
printf 'Backup retained at sibling path: %s\n' "$backup_dir"
migration_succeeded=true
