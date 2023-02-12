<p align="center">
  <h1 align="center"> 📝 NoteSH </h1>
</p>

<p align="center">
 Fully functional sticky notes App in your Terminal! Built with <a href="https://github.com/Textualize/textual">Textual</a>, an amazing TUI framework!
</p>

<p align="center">
 <a href="https://github.com/Cvaniak/NoteSH"><img alt="" src="https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/NoteshApp.png" width="100%"></a>
</p>

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

## NEW FEATURES

## 💡 Highlight when mouse is over

![Resize Background](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/HoverOver.gif)

## ➕ New Drawable that support borders change

![Resize Background](https://raw.githubusercontent.com/Cvaniak/NoteSH/master/documentation/NewDrawable.png)

## TODO

There are many thigs to add! If you have idea, please create Issue with your suggestions.

* [ ] Safe saving (now if there are any bugs you may lost your notes)
* [ ] Vim Key bindings
* [ ] Duplicate Note
* [ ] Hiding menu (Color Picker etc.)
* [ ] TOML config file
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
