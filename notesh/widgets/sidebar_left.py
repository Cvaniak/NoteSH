from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message, MessageTarget
from textual.widget import Widget
from textual.widgets import Static

from notesh.drawables.drawable import Drawable


class DeleteDrawable(Message):
    def __init__(self, sender: MessageTarget, drawable: Drawable) -> None:
        super().__init__(sender)
        self.drawable = drawable


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

        self.title = Static("Here more settings soon!", id="sidebar-title")

    def compose(self) -> ComposeResult:
        self.current_layout = Vertical(self.title)
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
