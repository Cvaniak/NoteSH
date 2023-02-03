from __future__ import annotations
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message, MessageTarget
from textual.widget import Widget
from textual.widgets import Button, Input
from notesh.color_picker import ColorPicker
from notesh.sticknote import Note
from notesh.play_area import PlayArea
from notesh.utils import generate_short_uuid


class DeleteSticknote(Message):
    def __init__(self, sender: MessageTarget, sticknote: Note) -> None:
        super().__init__(sender)
        self.sticknote = sticknote


class MultilineInput(Input):
    BINDINGS = Input.BINDINGS
    BINDINGS.extend(
        [
            Binding("up", "cursor_up", "cursor up", show=False),
            Binding("down", "cursor_down", "cursor down", show=False),
        ]
    )

    class Backspace(Message):
        ...

    class Arrow(Message):
        def __init__(self, sender: MessageTarget, top_down: str) -> None:
            super().__init__(sender)
            self.top_down = top_down

    def action_cursor_up(self) -> None:
        self.emit_no_wait(self.Arrow(self, "up"))

    def action_cursor_down(self) -> None:
        self.emit_no_wait(self.Arrow(self, "down"))

    def action_delete_left(self) -> None:
        super().action_delete_left()
        if not self.value:
            self.emit_no_wait(self.Backspace(self))


class MultilineArray(Vertical):
    def compose(self) -> ComposeResult:
        self.lines = [MultilineInput("", id="sidebar-input-0")]
        for line in self.lines:
            yield line

    def on_input_submitted(self, event: Input.Submitted):
        idx = self.lines.index(event.sender)
        new_input = MultilineInput("", id=f"sidebar-input-{generate_short_uuid()}")
        self.lines.insert(idx + 1, new_input)
        self.mount(new_input, after=event.sender)
        self.screen.set_focus(new_input)

    def on_multiline_input_backspace(self, event: MultilineInput.Backspace):
        if event.sender not in self.lines:
            return
        idx = self.lines.index(event.sender)
        if len(self.lines) >= 2:
            self.lines.remove(event.sender)
            event.sender.remove()
            if self.lines:
                self.screen.set_focus(self.lines[idx - 1])

    def on_multiline_input_arrow(self, event: MultilineInput.Arrow):
        idx = self.lines.index(event.sender)
        n = len(self.lines)
        if event.top_down == "up":
            if idx == 0:
                return
            self.screen.set_focus(self.lines[idx - 1])
        else:
            if idx + 1 == n:
                return
            self.screen.set_focus(self.lines[idx + 1])

    def recreate_multiline(self, value: str) -> None:
        while self.lines:
            self.lines.pop().remove()

        for line in value.split("  \n"):
            self.lines.append(MultilineInput(line, id=f"sidebar-input-{len(self.lines)}"))
            self.mount(self.lines[-1])


class Sidebar(Vertical):
    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.stick_note: Optional[Note] = None

    def compose(self) -> ComposeResult:
        self.title_input = Input("Title", id="sidebar-title")
        self.multiline_array = MultilineArray()
        self.color_picker = ColorPicker()
        self.button = Button("Delete Note", id="delete-sticknote")

        yield self.title_input

        yield self.multiline_array
        yield self.color_picker
        yield self.button

    def set_stick_note(self, stick_note: Note, display_sidebar: bool = False):
        self.stick_note = stick_note
        self.title_input.value = str(self.stick_note.title.renderable)
        self.multiline_array.recreate_multiline(str(self.stick_note.body.body))
        self.color_picker.update_colors(self.stick_note.color)

        if display_sidebar and self.has_class("-hidden"):
            self.remove_class("-hidden")

    def on_input_changed(self, event: Input.Changed):
        if self.stick_note:
            if event.sender.id == "sidebar-title":
                self.stick_note.title.body = str(event.value)
            else:
                text = [str(x.value) for x in self.multiline_array.lines]
                self.stick_note.body.body = "  \n".join(text)

    def change_stick_note_color(self, color):
        if self.stick_note:
            self.stick_note.change_color(color)

    def on_button_pressed(self, event: Button.Pressed):
        if event.sender.id == "delete-sticknote":
            if not self.stick_note:
                return
            self.emit_no_wait(DeleteSticknote(self, self.stick_note))
            self.screen.query_one(PlayArea).emit_no_wait(DeleteSticknote(self, self.stick_note))
            self.refresh()

    def on_color_picker_change(self, message: ColorPicker.Change):
        self.change_stick_note_color(message.color)
