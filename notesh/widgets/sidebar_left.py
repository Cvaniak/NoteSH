from __future__ import annotations

from typing import Optional, OrderedDict

from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Vertical
from textual.message import Message, MessageTarget
from textual.widget import Widget
from textual.widgets import Static

from notesh.drawables.drawable import Drawable
from notesh.play_area import PlayArea
from notesh.widgets.color_picker import ColorPicker


class SidebarLeft(Vertical):
    can_focus_children: bool = False

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.drawable: Optional[Drawable] = None

        self.play_area = None

        title = Static("Here more settings soon!", id="sidebar-title")
        body_color_picker = ColorPicker(type="body", title="Body Color Picker")
        border_color_picker = ColorPicker(type="border", title="Border Color Picker")

        self.widget_list: OrderedDict[str, Widget] = OrderedDict(
            {
                "title": title,
                "body_color_picker": body_color_picker,
                "border_color_picker": border_color_picker,
            }
        )

    def compose(self) -> ComposeResult:
        self.current_layout = Vertical(*self.widget_list.values())
        yield self.current_layout

    def toggle_focus(self):
        if self.has_class("-hidden"):
            self.set_focus(True)
            return True
        else:
            self.set_focus(False)
            return False

    def set_focus(self, focus: bool):
        if focus is True:
            self.remove_class("-hidden")
            self.can_focus_children = True
        else:
            self.add_class("-hidden")
            self.can_focus_children = False

    def set_play_area(self, play_area: PlayArea):
        self.play_area = play_area
        self.play_area.sidebar_layout(self.widget_list)

    def change_play_area_color(self, color: Color | str, part_type: str) -> None:
        if self.play_area:
            self.play_area.change_color(color, part_type=part_type)

    def on_color_picker_change(self, message: ColorPicker.Change):
        self.change_play_area_color(message.color, message.type)
