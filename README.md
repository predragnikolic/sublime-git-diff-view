# Git Diff View - sublime plugin
This plugin is intended for a quick overview of changes before commiting them. Nothing more, nothing less.

![Example](/img/showcase.gif)
in this example, sublime [git](https://github.com/kemayo/sublime-text-git) plugin is used to commit the changes.

### Features
- Show all modified files
- Show the diff view for a file 
- Stage/Unstage files
- Dismiss changes for a file

### Installation

* Clone this repository to `sublime-text-3/Packages` folder.
* Done. :wink:

### More Info

The default keybinding for toggling the view is:

```json
    { "keys": ["ctrl+shift+g"], "command": "git_diff_toggle_view"}
```

The view won't open if there are no git changes.

