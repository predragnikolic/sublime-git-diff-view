# Git Diff View

Get a quick overview of changes before committing them.

### Features

-   Show modified files (AKA "Status View")
-   View diff for a file. (AKA "Diff View")
-   Stage/Unstage files/hunks
-   Discard changes to files/hunks
-   Goto a file

![Example](img/showcase.png)

### Getting Started

Open the command palette and run `Package Control: Install Package`, then select `GitDiffView`.

Toggle the git diff view with `ctrl+shift+g`(Linux) or `alt+shift+g`(Mac) or via the command palette by selecting: `Git Diff View: Toggle`.
The git diff view won't open if there are no git changes.


### Keybindings in Status View (the right view)

- <kbd>a</kbd> / <kbd>space</kbd> - stage/unstage file
- <kbd>d</kbd> / <kbd>backspace</kbd> - dismiss file changes
- <kbd>g</kbd> - open file


### Keybindings in Diff View (the left view)

- <kbd>a</kbd> / <kbd>space</kbd> - stage/unstage hunk
- <kbd>d</kbd> / <kbd>backspace</kbd> - dismiss hunk change

Type of modification will be shown in the git status, next to the file name.
Here is a list of the types:

```
  "??" - Untracked
  " A" - Added
  "AM" - Added and Staged
  " M" - Modified
  "MM" - Modified and Staged
  " D" - Deleted
  " R" - Renamed
  " C" - Copied
  "UU" - Unmerged(Conflict)
```

### Workflow Example

[HowToUseIt.webm](https://github.com/predragnikolic/sublime-git-diff-view/assets/22029477/3af9654c-664c-4d0c-94bf-faa6af804e5c)

> NOTE:
For other commands like `git commit`, `git push`, `git pull`, use a different plugin like [Git](https://github.com/kemayo/sublime-text-git) or [GitSavvy](https://github.com/divmain/GitSavvy).
