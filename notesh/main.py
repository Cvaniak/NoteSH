from __future__ import annotations

from pathlib import Path
from typing import Type

from textual.app import App, ComposeResult, CSSPathType
from textual.binding import Binding
from textual.driver import Driver
from textual.geometry import Offset, Size
from textual.keys import KEY_ALIASES
from textual.widgets import Footer

from notesh.drawables.drawable import Drawable
from notesh.play_area import PlayArea
from notesh.utils import (calculate_size_for_file, load_binding_config_file,
                          load_drawables, save_drawables, set_bindings)
from notesh.widgets.sidebar import DeleteDrawable, Sidebar
from notesh.widgets.sidebar_left import SidebarLeft

KEY_ALIASES["backspace"] = ["ctrl+h"]


class NoteApp(App):
    CSS_PATH = "main.css"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
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
        self.footer = Footer()
        self.sidebar_left = SidebarLeft(classes="-hidden")
        self.sidebar = Sidebar(classes="-hidden")

    def compose(self) -> ComposeResult:
        min_size, max_size = calculate_size_for_file(self.file)
        self.play_area = PlayArea(min_size=min_size, max_size=max_size, screen_size=self.size)
        self.action_load_notes(min_size)
        self._load_key_bindings()

        yield self.sidebar
        yield self.sidebar_left
        yield self.play_area
        yield self.footer

    async def action_delete(self):
        self.play_area.delete_drawable()
        await self.sidebar.set_drawable(None)

    async def _edit_drawable(self):
        if self.play_area.focused_drawable is not None:
            await self.sidebar.set_drawable(self.play_area.focused_drawable, True)
        self.play_area.can_focus_children = False

    async def action_edit(self):
        await self._edit_drawable()

    async def on_drawable_clicked(self, event: Drawable.Clicked):
        self.play_area.focused_drawable = event.drawable
        await self._edit_drawable()

    async def _move_drawable(self, direction: str) -> None:
        value = 1
        if "_" in direction:
            direction_parsed = direction.split("_")
            direction, value = direction_parsed[0], int(direction_parsed[1])
        await self.play_area.move_drawable(direction, value)

    async def _bring(self, direction: str) -> None:
        if self.play_area.focused_drawable is not None:
            getattr(self.play_area.focused_drawable, f"bring_{direction}")()

    async def _resize(self, direction: str) -> None:
        d = {"h_plus": (1, 0), "h_minus": (-1, 0), "v_plus": (0, 1), "v_minus": (0, -1)}
        if self.play_area.focused_drawable is not None:
            await self.play_area.focused_drawable.resize_drawable(*d[direction])

    async def _unfocus(self, fully: bool = False):
        self.play_area.can_focus_children = True
        self.sidebar.set_focus(False)
        self.sidebar_left.set_focus(False)
        if self.focused is None:
            return
        if self.focused is self.play_area.focused_drawable or fully:
            self.set_focus(None)
            self.play_area.focused_drawable = None
            return
        self.set_focus(self.play_area.focused_drawable)
        self.play_area.focused_drawable = None

    async def action_unfocus(self):
        await self._unfocus()

    def action_add_note(self) -> None:
        new_drawable = self.play_area.add_new_drawable("note")
        self._add_new_drawable(new_drawable)

    def action_add_drawable(self) -> None:
        new_drawable = self.play_area.add_new_drawable("drawable")
        self._add_new_drawable(new_drawable)

    def action_add_box(self) -> None:
        new_drawable = self.play_area.add_new_drawable("box")
        self._add_new_drawable(new_drawable)

    def action_toggle_sidebar(self) -> None:
        self.sidebar.toggle_focus()

    def action_toggle_sidebar_left(self) -> None:
        if not self.sidebar_left.toggle_focus():
            focus_candidat = self.play_area.focused_drawable
            self.play_area.can_focus_children = True
            if focus_candidat is not None:
                self.set_focus(focus_candidat)
        else:
            self.play_area.can_focus_children = False
            self.set_focus(self.sidebar_left.children[0])

    def action_save_notes(self) -> None:
        save_drawables(self.file, self.play_area.drawables, list(self.screen.layers))

    def action_load_notes(self, min_size: Size = Size(0, 0)) -> None:
        self.play_area.clear_drawables()
        drawables = load_drawables(self.file)
        for name, drawable_obj in drawables:
            self.play_area.add_parsed_drawable(drawable_obj, name, Offset(min_size.width, min_size.height))
        self.refresh()

    async def action_quit(self) -> None:
        self.action_save_notes()
        self.exit()  # type: ignore

    async def on_play_area_clicked(self, message: PlayArea.Clicked):
        await self._unfocus(fully=True)

    async def on_drawable_focus(self, message: Drawable.Focus):
        drawable = self.screen.get_widget_by_id(message.index)
        if isinstance(drawable, Drawable):
            await self.sidebar.set_drawable(drawable, message.display_sidebar)

    def on_delete_drawable(self, message: DeleteDrawable) -> None:
        self.play_area.delete_drawable(message.drawable)

    def _add_new_drawable(self, new_drawable: Drawable) -> None:
        self.set_focus(new_drawable)
        self.play_area.focused_drawable = new_drawable
        self.play_area.can_focus_children = True

    def _load_key_bindings(self):
        conf = load_binding_config_file(str(Path(__file__).parent / "default_bindings.toml"))
        conf.update(load_binding_config_file(str(Path(__file__).parent / "user_bindings.toml")))

        set_bindings(self, conf["default"], show=True)

        set_bindings(self, conf["moving_drawables"], func=self._move_drawable)
        set_bindings(self, conf["bring_drawable"], func=self._bring)
        set_bindings(self, conf["resize_drawable"], func=self._resize)

        set_bindings(self, conf["normal_insert"])
        set_bindings(self.play_area, conf["normal"])

        self.footer._focus_changed(None)  # type: ignore


if __name__ == "__main__":
    app = NoteApp()
    app.run()  # type: ignore
