# Git Diff View - sublime plugin
Get a quick overview of changes before commiting them.

![Example](/img/showcase.gif)


### Features
- Show all modified files
- Show the diff view for a file 
- Stage/Unstage files
- Dismiss changes for a file
- Go to a file

### Installation

* Clone this repository to `sublime-text-3/Packages` folder.
* Done. :wink:

### More Info


The default keybinding for toggling the view is:

```json
    { "keys": ["ctrl+shift+g"], "command": "git_diff_toggle_view"}
```

Type of modification will be shown in the git status. 
Here is the list of the types: 
```
    ?? - untracked
    A - Added
    M - Modified
    D - Deleted
    R - Renamed
```

The view won't open if there are no git changes.

