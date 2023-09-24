from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.geometry import Offset, Size
from textual.keys import KEY_ALIASES
from textual.widget import Widget

from notesh.drawables.drawable import Drawable
from notesh.play_area import PlayArea
from notesh.utils import calculate_size_for_file, load_binding_config_file, load_drawables, save_drawables, set_bindings
from notesh.widgets.focusable_footer import FocusableFooter
from notesh.widgets.sidebar import DeleteDrawable, Sidebar
from notesh.widgets.sidebar_left import SidebarLeft
from hoptex.configs import HoptexBindingConfig
from hoptex.decorator import hoptex

KEY_ALIASES["backspace"] = ["ctrl+h"]


def load_confing_hoptex():
    conf = load_binding_config_file(str(Path(__file__).parent / "default_bindings.toml"))
    conf.update(load_binding_config_file(str(Path(__file__).parent / "user_bindings.toml")))
    return conf.get("hoptex", {})


# Not perfect solution to load file here,
# but cant load confing for hoptex other way
hoptex_conf = load_confing_hoptex()

hoptex_binding = HoptexBindingConfig(
    focus=hoptex_conf.get("hoptex_focus", "ctrl+n"),
    quit=hoptex_conf.get("hoptex_quit", "escape,ctrl+c"),
    unfocus="",
)


@hoptex(bindings=hoptex_binding)
class NoteApp(App[None]):
    CSS_PATH = "main.css"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
    ]

    DEFAULT_FILE = os.environ.get(
        "NOTESH_FILE",
        str(
            (
                Path(os.getenv("APPDATA", Path.home()))
                if os.name == "nt"
                else Path(os.getenv("XDG_DATA_HOME", Path("~/.local/share").expanduser()))
            )
            / "notesh"
            / "notes.json"
        ),
    )

    def __init__(
        self,
        watch_css: bool = False,
        file: str = DEFAULT_FILE,
    ):
        super().__init__(watch_css=watch_css)
        self.file = file
        self.footer = FocusableFooter()
        self.sidebar_left = SidebarLeft(classes="-hidden")
        self.sidebar = Sidebar(classes="-hidden")

    def compose(self) -> ComposeResult:
        min_size, max_size = calculate_size_for_file(self.file)
        self.play_area = PlayArea(min_size=min_size, max_size=max_size, screen_size=self.size)
        self.action_load_notes(min_size)
        self.sidebar_left.set_play_area(self.play_area)

        self._load_key_bindings()

        yield self.sidebar
        yield self.sidebar_left
        yield self.play_area
        yield self.footer
        self._hoptex_parent_widgets: set[Widget] = {self.play_area}

        self.set_focus(self.footer)

    async def action_delete(self):
        await self._delete_drawable()

    async def _edit_drawable(self):
        if self.play_area.focused_drawable is None:
            return
        self._hoptex_parent_widgets.add(self.sidebar)
        await self.sidebar.set_drawable(self.play_area.focused_drawable, True)
        self.set_focus(self.sidebar.get_child())
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

    def _unfocus(self, fully: bool = False):
        self.play_area.can_focus_children = True
        self.sidebar.set_focus(False)
        self.sidebar_left.set_focus(False)
        self._hoptex_parent_widgets.discard(self.sidebar)
        self._hoptex_parent_widgets.discard(self.sidebar_left)
        # Already Unfocused
        if self.focused is None:
            return
        # Unfocuss Fully (forced) or from view with selected one drawable
        if self.focused is self.play_area.focused_drawable or fully:
            self.set_focus(self.footer)
            self.play_area.focused_drawable = None
            return
        self.set_focus(self.play_area.focused_drawable)
        self.play_area.focused_drawable = None

    async def _delete_drawable(self, drawable: Optional[Drawable] = None):
        self.play_area.delete_drawable(drawable)
        await self.sidebar.set_drawable(None)
        if self.play_area.can_focus:
            self.set_focus(self.play_area)
        else:
            self._unfocus()

    async def action_unfocus(self):
        self._unfocus()

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
        if self.sidebar.toggle_focus():
            self._hoptex_parent_widgets.add(self.sidebar)
        else:
            self._hoptex_parent_widgets.discard(self.sidebar)

    def action_toggle_sidebar_left(self) -> None:
        if not self.sidebar_left.toggle_focus():
            self._hoptex_parent_widgets.discard(self.sidebar_left)
            focus_candidat = self.play_area.focused_drawable
            self.play_area.can_focus_children = True
            if focus_candidat is not None:
                self.set_focus(focus_candidat)
        else:
            self._hoptex_parent_widgets.add(self.sidebar_left)
            self.play_area.can_focus_children = False
            self.set_focus(self.sidebar_left.children[0])

    def action_save_notes(self) -> None:
        save_drawables(self.file, self.play_area.drawables, list(self.screen.layers), self.play_area.dump())

    def action_load_notes(self, min_size: Size = Size(0, 0)) -> None:
        self.play_area.clear_drawables()
        drawables, background = load_drawables(self.file)
        for name, drawable_obj in drawables:
            self.play_area.add_parsed_drawable(drawable_obj, name, Offset(min_size.width, min_size.height))
        self.play_area.load(background)
        self.refresh()

    async def action_quit(self) -> None:
        self.action_save_notes()
        self.exit()  # type: ignore

    async def on_play_area_clicked(self, message: PlayArea.Clicked):
        self._unfocus(fully=True)

    async def on_drawable_focus(self, message: Drawable.Focus):
        drawable = self.screen.get_widget_by_id(message.index)
        if isinstance(drawable, Drawable):
            await self.sidebar.set_drawable(drawable, message.display_sidebar)

    async def on_delete_drawable(self, message: DeleteDrawable) -> None:
        await self._delete_drawable(message.drawable)

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


if __name__ == "__main__":
    app = NoteApp(watch_css=True)
    app.run()  # type: ignore
