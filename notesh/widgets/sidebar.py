from __future__ import annotations

from typing import Optional, OrderedDict

from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Vertical
from textual.message import Message, MessageTarget
from textual.widget import Widget
from textual.widgets import Button, Input

from notesh.drawables.drawable import Drawable
from notesh.play_area import PlayArea
from notesh.widgets.color_picker import ColorPicker
from notesh.widgets.multiline_input import MultilineArray


class DeleteDrawable(Message):
    def __init__(self, sender: MessageTarget, drawable: Drawable) -> None:
        super().__init__(sender)
        self.drawable = drawable


class Sidebar(Vertical):
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

        input = Input("Title", id="sidebar-title")
        multiline_array = MultilineArray()

        body_color_picker = ColorPicker(type="body", title="Body Color Picker")

        border_color_picker = ColorPicker(type="border", title="Border Color Picker")
        border_type = Button("Change Border", id="border-picker", variant="warning")

        button = Button("Delete Note", id="delete-sticknote", variant="error")

        self.widget_list: OrderedDict[str, Widget] = OrderedDict(
            {
                "input": input,
                "multiline_array": multiline_array,
                "body_color_picker": body_color_picker,
                "border_color_picker": border_color_picker,
                "border_picker": border_type,
                "delete_button": button,
            }
        )

    def compose(self) -> ComposeResult:
        self.current_layout = Vertical(*self.widget_list.values())
        yield self.current_layout

    def change_sidebar(self):
        for widget in self.widget_list.values():
            widget.add_class("-hidden")

        if self.drawable is not None:
            self.drawable.sidebar_layout(self.widget_list)

    async def set_drawable(self, drawable: Optional[Drawable], display_sidebar: bool = False):
        self.drawable = drawable
        self.change_sidebar()

        if self.drawable is None:
            self.set_focus(False)
        elif display_sidebar:
            self.set_focus(True)
        self.refresh()

    async def on_input_changed(self, event: Input.Changed):
        if self.drawable is not None:
            self.drawable.input_changed(event)

    async def on_multiline_array_changed(self, event: MultilineArray.Changed):
        if self.drawable is not None:
            self.drawable.multiline_array_changed(event)

    def change_drawable_color(self, color: Color | str, part_type: str):
        if self.drawable:
            self.drawable.change_color(color, part_type=part_type)

    def on_button_pressed(self, event: Button.Pressed):
        if event.sender.id == "delete-sticknote":
            if not self.drawable:
                return
            self.emit_no_wait(DeleteDrawable(self, self.drawable))
            self.screen.query_one(PlayArea).emit_no_wait(DeleteDrawable(self, self.drawable))
            self.refresh()
        if event.sender.id == "border-picker":
            self.drawable.next_border()

    def on_color_picker_change(self, message: ColorPicker.Change):
        self.change_drawable_color(message.color, message.type)

    def toggle_focus(self) -> bool:
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
