from __future__ import annotations

import json
import os
import sys
from typing import Any, Type

from textual.app import App, ComposeResult, CSSPathType
from textual.binding import Binding
from textual.driver import Driver
from textual.geometry import Offset, Size
from textual.widgets import Footer

from notesh.drawables.drawable import Drawable
from notesh.play_area import PlayArea
from notesh.widgets.sidebar import DeleteDrawable, Sidebar


class NoteApp(App):
    CSS_PATH = "main.css"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar"),
        Binding("ctrl+a", "add_note", "Create Stick Note"),
        Binding("ctrl+x", "add_box", "Create Box"),
        Binding("ctrl+s", "save_notes", "Saves Notes"),
        Binding("ctrl+t", "app.toggle_dark", "Toggle Dark mode"),
    ]

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType = None,
        watch_css: bool = False,
        file: str = "notes.json",
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.file = file

    def compose(self) -> ComposeResult:
        self.sidebar = Sidebar(classes="-hidden")
        yield self.sidebar
        min_size, max_size = self.new_size()
        self.play_area = PlayArea(min_size=min_size, max_size=max_size, screen_size=self.size)
        self.action_load_notes(min_size)
        yield self.play_area
        yield Footer()

    def action_add_note(self) -> None:
        self.play_area.add_new_drawable("note")

    def action_add_drawable(self) -> None:
        self.play_area.add_new_drawable("drawable")

    def action_add_box(self) -> None:
        self.play_area.add_new_drawable("box")

    def action_toggle_sidebar(self) -> None:
        sidebar = self.sidebar

        if sidebar.has_class("-hidden"):
            sidebar.remove_class("-hidden")
        else:
            sidebar.add_class("-hidden")

    async def on_drawable_focus(self, message: Drawable.Focus):
        drawable = self.screen.get_widget_by_id(message.index)
        if isinstance(drawable, Drawable):
            await self.sidebar.set_drawable(drawable, message.display_sidebar)

    def new_size(self):
        if not os.path.exists(self.file):
            return Size(0, 0), Size(50, 20)

        with open(self.file, "r") as file:
            obj = json.load(file)

        keys = list(obj.keys())
        keys.remove("layers")

        mxx, mxy = -sys.maxsize, -sys.maxsize
        mnx, mny = sys.maxsize, sys.maxsize
        for note in sorted(keys, key=lambda x: obj["layers"].index(x)):
            mxx = max(mxx, obj[note]["pos"][0] + obj[note]["size"][0])
            mnx = min(mnx, obj[note]["pos"][0])
            mxy = max(mxy, obj[note]["pos"][1] + obj[note]["size"][1])
            mny = min(mny, obj[note]["pos"][1])

        mxx = 50 if mxx == sys.maxsize else max(mxx, 50)
        mxy = 20 if mxy == sys.maxsize else max(mxy, 20)
        mnx = 0 if mnx == sys.maxsize else mnx
        mny = 0 if mny == sys.maxsize else mny

        return Size(mnx, mny), Size(mxx, mxy)

    def action_save_notes(self):
        obj: dict[str, Any] = {"layers": []}
        layers_set: set[str] = set()
        drawable: Drawable
        for drawable in self.play_area.drawables:
            if drawable.id is None:
                continue
            obj[drawable.id] = drawable.dump()
            layers_set.add(drawable.id)

        obj["layers"].extend([x for x in self.screen.layers if x in layers_set])

        with open(self.file, "w") as file:
            json.dump(obj, file)

    def action_load_notes(self, min_size: Size = Size(0, 0)):
        if not os.path.exists(self.file):
            return

        with open(self.file, "r") as file:
            obj = json.load(file)

        if not obj:
            return
        self.play_area.remove_drawables()

        keys = list(obj.keys())
        keys.remove("layers")
        for drawable in sorted(keys, key=lambda x: obj["layers"].index(x)):
            self.play_area.add_parsed_drawable(obj[drawable], drawable, Offset(min_size.width, min_size.height))

        self.refresh()

    async def action_quit(self) -> None:
        self.action_save_notes()
        self.exit()

    def on_delete_drawable(self, message: DeleteDrawable) -> None:
        self.play_area.delete_drawable(message.drawable)


if __name__ == "__main__":
    app = NoteApp()
    app.run()
