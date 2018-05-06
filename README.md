# Git Diff View - sublime plugin

![Example](/img/showcase.gif)
in this example, sublime [git](https://github.com/kemayo/sublime-text-git) plugin is used to add files to the staging area 

### Features
- Show all modified files(Git Status) in the left
- Show the diff view for a file in the right
- Stage/Unstage files (not implemented)
- Dismiss changes for a file (not implemented)

### Installation

* Clone this repository to `sublime-text-3/Packages` folder.
* Add this keybinding. 

```json
    { "keys": ["ctrl+shift+g"], "command": "git_diff_toggle_view"}
```
* Done. :wink:

Here is a line that will be deleted