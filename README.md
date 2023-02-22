<p align="center">
  <h1 align="center"> 📝 NoteSH </h1>
</p>

<p align="center">
 Fully functional sticky notes App in your Terminal! Built with <a href="https://github.com/Textualize/textual">Textual</a>, an amazing TUI framework!
</p>

<p align="center">
 <a href="https://github.com/Cvaniak/NoteSH"><img alt="" src="https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/NoteshApp.png" width="100%"></a>
</p>

## In last Update - Vim/Custom Key bindings

In last update you can find support for for custom key bindings. More info in seperate section.

## Installation

Best option to install is using [pipx](https://github.com/pypa/pipx):

```bash
pipx install notesh
# but it is still possible to do it with just pip:
pip install notesh
```

## Usage

To start using just type in your terminal:

```bash
notesh
```

it will create new file notes.json in current directory.
You can also specify file by using `-f` flag:

```bash
notesh -f MyNotes.json
# or full/relative path
notesh -f ~/Documents/MyNotes.json
```

## ➕ Create new Note

* To create new note just press `Ctrl+A`
* You can change color with buttons but also using scroll
* To edit note just click in its body

![New note](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/CreateNote.gif)

## 🧅 It supports layers

* To move note grab it top part and move with mouse

![Layers](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/Layers.gif)

## 🗚  You can resize notes

* To resize grab left bottom corner and move with mouse

![Resize Notes](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/Resizing.gif)

## 💡 And background is resizable

* If you make make background to big it will readjust after you reopen App
* You can also click `CTRL-Mouse` to look around whole wall

![Resize Background](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/DynamicResize.gif)

## 💡 Highlight when mouse is over

![Resize Background](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/HoverOver.gif)

## ➕ New Drawable that support borders change

![Resize Background](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/NewDrawable.png)

## NEW FEATURES

## ⌨️  Vim/Custom key bindings

You can now do everything using KEYBOARD!
This is first version so if you have any suggestions please write them in existing issue.  
Default keybindings are in `default_bindings.toml`
file that is in root of installation.  
You can also create second file `user_bindings.toml` where you can overwrite defaults.

### What you can do

* Change focus `focus_next/focus_previous` using `ctrl+i,ctrl+j/ctrl+o,ctrl+k`
* Edit note `edit` using `i`
* When note is focused you can move it with `j/k/l/h`.
  Also adding shift moves it more with one click
* Clicking `unfocus` using `escape` returns from edit mode,
  and unfocus drawable if not in edit mode.
* Resize note using `+/-` for vertical and `>/<` for horizontal
* Bring 'ctrl+f' Forward and `ctrl+b` Backward Note

### Bindings file

<details>
<summary>Default file</summary>

```toml
# These are default, they also are displayed at the footer
[default]
quit = ["ctrl+q,ctrl+c", "Quit"]
toggle_sidebar_left = ["ctrl+e", "Sidebar Left"]
add_note = ["ctrl+a", "Create Stick Note"]
add_box = ["ctrl+x", "Create Box"]
save_notes = ["ctrl+s", "Save Notes"]
unfocus = ["escape", "Unfocus"]
"app.toggle_dark" = ["ctrl+t", "Dark/Light"]

[moving_drawables]
# Default movement
left = "h"
right = "l"
up = "k"
down = "j"
# You can add number after _ and it will move note that many times
left_5 = "H"
right_5 = "L"
up_5 = "K"
down_5 = "J"

[normal_insert]
# there is only `next` and `previous` and the order is not changable yet
focus_next = "ctrl+i,ctrl+j"
focus_previous = "ctrl+o,ctrl+k"
unfocus = "escape"

[normal]
edit = "i"
delete = "Q"
add_note = "o"
add_box = "O"

# For special characters like `+` or `<` you need to use names
# You can check the name using textual `textual keys`
[resize_drawable]
h_plus = "greater_than_sign"
h_minus = "less_than_sign"
v_plus = "plus"
v_minus = "minus"

# It brings at the top or bottom the note
[bring_drawable]
forward = "ctrl+f"
backward = "ctrl+b"
```

</details>

## TODO

There are many thigs to add! If you have idea, please create Issue with your suggestions.

* [ ] Safe saving (now if there are any bugs you may lost your notes)
* [x] Vim Key bindings
  * Wait for feedback
* [ ] Duplicate Note
* [ ] Hiding menu (Color Picker etc.)
* [x] TOML config file
* [ ] Left Sidebar (for background and preferences)
* [ ] Align tool for text
* [ ] Fixed layers (if needed)
* [ ] Diffrent Drawables:
  * [ ] Check List
  * [ ] Arrows

and also resolve problems:

* [ ] Multiline Input (currently textual does not support it and here we have my hacky solution)  

## Thanks

Big thanks to [Will McGugan](https://github.com/willmcgugan) and all members and contributors of [Textualize.io](https://textualize.io)!
Go checkout [Textual](https://github.com/Textualize/textual) amazing TUI framework on which this app is based.
