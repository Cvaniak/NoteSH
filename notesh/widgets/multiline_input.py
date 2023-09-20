from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input

from notesh.utils import generate_short_uuid


class MultilineInput(Input):
    BINDINGS = Input.BINDINGS
    BINDINGS.extend(
        [
            Binding("up", "cursor_up", "cursor up", show=False),
            Binding("down", "cursor_down", "cursor down", show=False),
        ]
    )

    def action_cursor_up(self) -> None:
        self.post_message(self.Arrow(self, "up"))

    def action_cursor_down(self) -> None:
        self.post_message(self.Arrow(self, "down"))

    def action_delete_left(self) -> None:
        super().action_delete_left()
        if not self.value:
            self.post_message(self.Backspace(self))

    class Backspace(Message):
        def __init__(self, multiline_input: MultilineInput) -> None:
            super().__init__()
            self.multiline_input = multiline_input

    class Arrow(Message):
        def __init__(self, multiline_input: MultilineInput, top_down: str) -> None:
            super().__init__()
            self.multiline_input = multiline_input
            self.top_down = top_down


class MultilineArray(Vertical):
    lines = [MultilineInput("", id="sidebar-input-0")]

    def compose(self) -> ComposeResult:
        for line in self.lines:
            yield line

    def on_input_submitted(self, event: Input.Submitted):
        idx = self.lines.index(event.input)
        new_input = MultilineInput("", id=f"sidebar-input-{generate_short_uuid()}")
        self.lines.insert(idx + 1, new_input)
        self.mount(new_input, after=event.input)
        self.screen.set_focus(new_input)

    def on_multiline_input_backspace(self, event: MultilineInput.Backspace):
        if event.multiline_input not in self.lines:
            return
        idx = self.lines.index(event.multiline_input)
        if len(self.lines) >= 2:
            self.lines.remove(event.multiline_input)
            event.multiline_input.remove()
            if self.lines:
                self.screen.set_focus(self.lines[idx - 1])

    def on_multiline_input_arrow(self, event: MultilineInput.Arrow):
        idx = self.lines.index(event.multiline_input)
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

    async def on_input_changed(self, event: MultilineInput.Changed):
        event.stop()
        self.post_message(self.Changed(self))

    class Changed(Message):
        def __init__(self, sender: MultilineArray) -> None:
            super().__init__()
            self.input = sender

    # async def on_key(self, event: events.Key):
    #     print(self.app.rkk)
    #     if event.key in self.app.rkk:
    #         event.stop()
