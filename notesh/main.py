import os
from typing import Type
from textual.app import App, CSSPathType, ComposeResult
from textual.driver import Driver
from textual.geometry import Offset, Size

from notesh.play_area import PlayArea
from textual.widgets import Footer
from notesh.sticknote import Note
from notesh.sidebar import DeleteSticknote, Sidebar
import json


class NoteApp(App):
    CSS_PATH = "main.css"

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+b", "toggle_sidebar", "Sidebar"),
        ("ctrl+a", "add_note", "Create Stick Note"),
        ("ctrl+s", "save_notes", "Saves Notes"),
        ("ctrl+w", "load_notes", "Load Notes"),
        ("ctrl+t", "app.toggle_dark", "Toggle Dark mode"),
    ]

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType = None,
        watch_css: bool = False,
        file="notes.json",
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.file = file

    def compose(self) -> ComposeResult:
        self.sidebar = Sidebar(classes="-hidden")
        yield self.sidebar
        min_size, max_size = self.new_size()
        self.play_area = PlayArea(min_size=min_size, max_size=max_size, screen_size = self.size)
        self.action_load_notes(min_size)
        yield self.play_area
        yield Footer()
        # print(self.size, "BAS"*10)

    def action_add_note(self) -> None:
        self.play_area.add_new_note()

    def action_toggle_sidebar(self) -> None:
        sidebar = self.sidebar
        self.set_focus(None)
        if sidebar.has_class("-hidden"):
            sidebar.remove_class("-hidden")
        else:
            if sidebar.query("*:focus"):
                self.screen.set_focus(None)
            sidebar.add_class("-hidden")

    async def on_note_focus(self, message: Note.Focus):
        self.sidebar.set_stick_note(
            self.screen.get_widget_by_id(message.index), message.display_sidebar
        )

    def action_save_notes(self):
        obj = {"layers": []}
        layers_set = set()
        note: Note
        for note in self.play_area.notes:
            obj[note.id] = {
                "title": note.title.body,
                "body": note.body.body,
                "pos": (note.styles.offset.x.value, note.styles.offset.y.value),
                "color": note.color.hex6,
                "size": (note.styles.width.value, note.styles.height.value),
                "type": "note",
            }
            layers_set.add(note.id)

        obj["layers"].extend([x for x in self.screen.layers if x in layers_set])

        with open(self.file, "w") as file:
            json.dump(obj, file)

    def new_size(self):
        if not os.path.exists(self.file):
            return Size(0, 0), Size(50, 20)

        with open(self.file, "r") as file:
            obj = json.load(file)


        keys = list(obj.keys())
        keys.remove("layers")

        mxx, mxy = float("-inf"), float("-inf")
        mnx, mny = float("inf"), float("inf")
        for note in sorted(keys, key=lambda x: obj["layers"].index(x)):
            mxx = max(mxx,obj[note]["pos"][0]+obj[note]["size"][0])
            mnx = min(mnx,obj[note]["pos"][0])
            mxy = max(mxy,obj[note]["pos"][1]+obj[note]["size"][1])
            mny = min(mny,obj[note]["pos"][1])

        mxx = 50 if mxx == float("-inf") else max(mxx, 50)
        mxy = 20 if mxy == float("-inf") else max(mxy, 20)
        mnx = 0 if mnx == float("inf") else mnx
        mny = 0 if mny == float("inf") else mny

        return Size(mnx, mny), Size(mxx, mxy)

    def action_load_notes(self, min_size: Size = Size(0, 0)):
        if not os.path.exists(self.file):
            return

        with open(self.file, "r") as file:
            obj = json.load(file)

        if not obj:
            return
        self.play_area.remove_notes()

        keys = list(obj.keys())
        keys.remove("layers")
        for note in sorted(keys, key=lambda x: obj["layers"].index(x)):
            print("Hejo", Offset(*obj[note]["pos"]),Offset(min_size.width, min_size.height))
            self.play_area.add_new_note(
                note_id=note,
                title=obj[note]["title"],
                body=obj[note]["body"],
                color=obj[note]["color"],
                pos=Offset(*obj[note]["pos"])-Offset(min_size.width, min_size.height),
                size=Size(*obj[note]["size"]),
            )
        self.refresh()

    def action_quit(self):
        self.action_save_notes()
        self.exit()

    def on_delete_sticknote(self, message: DeleteSticknote):
        self.play_area.delete_sticknote(message.sticknote)
        # self.action_toggle_sidebar()


if __name__ == "__main__":
    app = NoteApp()
    app.run()
