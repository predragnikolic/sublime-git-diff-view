# Git Diff View - sublime plugin

Get a quick overview of changes before commiting them.

![Example](/img/showcase.gif)

### Features

-   Show all modified files
-   Show the diff view for a file
-   Stage/Unstage files (Staged files are marked with "✔")
-   Dismiss changes for a file
-   Go to a file

### Installation

-   Clone this repository to `sublime-text-3/Packages` folder.
-   Rename the folder to `GitDiffView`.
-   Done. :wink:

### Instructions

The default keybinding for toggling the view is `ctrl+shift+g`.
The git view won't open if there are no git changes.

Type of modification will be shown in the git status, next to the file name.
Here is a list of the types:

```
    ?? - Untracked
     A - Added
     M - Modified
     D - Deleted
     R - Renamed
    UU - Unmerged(Conflict)
```
