from __future__ import annotations

from typing import Any, Optional, OrderedDict, Type, TypeVar

from rich.markdown import Markdown
from textual import events
from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Vertical
from textual.geometry import Offset, Size
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static

from notesh.utils import generate_short_uuid
from notesh.widgets.multiline_input import MultilineArray

_T = TypeVar("_T")


class Drawable(Static):
    type: str = "drawable"

    def __init__(
        self,
        id: str | None = None,
        body: str = "",
        color: str = "#ffaa00",
        pos: Offset = Offset(0, 0),
        size: Size = Size(20, 14),
        parent: Optional[Widget] = None,
        init_parts: bool = True,
    ) -> None:
        if id is None or id == "":
            id = f"note-{generate_short_uuid()}"
        super().__init__(id=id)
        self.note_id: str = id
        self.clicked = (0, 0)
        self.styles.layer = f"{id}"
        self.color = Color.parse(color)
        self.styles.offset = pos
        self.styles.width = size.width
        self.styles.height = size.height
        self.pparent = parent
        self.is_entered = False

        if init_parts:
            self.init_parts()

    def init_parts(self) -> None:
        self.body = Body(self, body="", id="default-body")
        self.resizer = Resizer(body=" ", id=f"{self.id}-resizer", parent=self)

    def drawable_body(self) -> ComposeResult:
        yield Vertical(
            self.body,
        )
        yield self.resizer

    def compose(self) -> ComposeResult:
        yield from self.drawable_body()

        self.change_color(self.color, duration=0.0)
        self.screen.styles.layers = self.screen.styles.layers + (f"{self.styles.layer}", f"{self.styles.layer}-resizer")

    def change_color(self, new_color: str | Color, duration: float = 1.0, part_type: str = "body") -> None:
        if isinstance(new_color, str):
            base_color = Color.parse(new_color)
        else:
            base_color = new_color

        if part_type == "" or part_type == "body":
            self.color = base_color
        self.update_layout(duration)

    def update_layout(self, duration: float = 1.0):
        base_color = self.color
        self.body.styles.animate("background", value=base_color, duration=duration)

        self.body.styles.border = ("outer", base_color.darken(0.1))
        self.body.styles.border_left = ("outer", base_color.lighten(0.1))
        self.body.styles.border_top = ("outer", base_color.lighten(0.1))
        self.resizer.styles.animate("background", value=base_color.darken(0.1), duration=duration)

    async def drawable_is_moved(self, event: events.MouseMove):
        if self.clicked is not None and event.button != 0:
            note = self
            if event.delta:
                note.offset = note.offset + event.delta
                await self.emit(Drawable.Move(self, drawable=self))

    async def drawable_is_focused(self, event: events.MouseEvent, display_sidebar: bool = False):
        self.clicked = event.offset
        layers = tuple(x for x in self.screen.styles.layers if x != self.layer)
        self.screen.styles.layers = layers + (self.styles.layer,)
        await self.emit(Drawable.Focus(self, self.note_id, display_sidebar))

    async def drawable_is_unfocused(self, event: events.MouseUp) -> None:
        self.clicked = None

    async def drawable_is_resized(self, event: events.MouseMove) -> None:
        if self.clicked is not None and event.button != 0:
            note = self
            note.styles.width = note.styles.width.value + event.delta_x
            note.styles.height = note.styles.height.value + event.delta_y
            note.refresh()

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.drawable_is_moved(event)

    async def on_mouse_down(self, event: events.MouseDown) -> None:
        if self.app.mouse_captured is None:
            self.capture_mouse()
        await self.drawable_is_focused(event)

    async def on_mouse_up(self, event: events.MouseUp) -> None:
        if self.app.mouse_captured is None:
            self.capture_mouse(False)
        await self.drawable_is_unfocused(event)

    async def on_click(self, event: events.Click):
        await self.drawable_is_focused(event, True)

    async def on_enter(self, event: events.Enter):
        if self.is_entered == False:
            self._last_color: Color = self.color
        self.is_entered = True
        if self._last_color.brightness > 0.9:
            self.change_color(self._last_color.darken(0.1), duration=0.3)
        else:
            self.change_color(self._last_color.lighten(0.1), duration=0.3)

    async def on_leave(self, event: events.Leave):
        self.is_entered = False
        self.change_color(self._last_color, duration=0.1)

    def input_changed(self, event: Input.Changed):
        ...

    def multiline_array_changed(self, event: MultilineArray.Changed):
        ...

    def sidebar_layout(self, widgets: OrderedDict[str, Widget]) -> None:
        widgets["body_color_picker"].remove_class("-hidden")
        widgets["delete_button"].remove_class("-hidden")

        widgets["body_color_picker"].update_colors(self.color)

    def dump(self) -> dict[str, Any]:
        return {
            "body": self.body.body,
            "pos": (self.styles.offset.x.value, self.styles.offset.y.value),
            "color": self.color.hex6,
            "size": (self.styles.width.value, self.styles.height.value),
            "type": self.type,
        }

    @classmethod
    def load(cls: Type[_T], obj: dict[Any, Any], drawable_id: str, offset: Offset = Offset(0, 0)):
        return cls(
            id=drawable_id,
            body=obj["body"],
            color=obj["color"],
            pos=Offset(*obj["pos"]) - offset,
            size=Size(*obj["size"]),
        )

    class Mess(Message):
        def __init__(self, sender: MessageTarget, value: str | None) -> None:
            super().__init__(sender)
            self.value = value

    class Focus(Message):
        def __init__(self, sender: MessageTarget, index: str, display_sidebar: bool = False) -> None:
            super().__init__(sender)
            self.index = index
            self.display_sidebar = display_sidebar

    class Move(Message):
        def __init__(
            self,
            sender: MessageTarget,
            drawable: "Drawable",
        ) -> None:
            super().__init__(sender)
            self.drawable = drawable


class DrawablePart(Static):
    body: reactive[str] = reactive("")

    def __init__(
        self,
        parent: Drawable,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        body: str = "",
    ) -> None:
        super().__init__(body, name=name, id=id, classes=classes)
        self.clicked = Offset(0, 0)
        self.pparent: Drawable = parent
        self.body = str(body)

    def watch_body(self, body_text: str):
        self.update(Markdown(body_text))

    async def on_mouse_down(self, event: events.MouseDown):
        self.capture_mouse()
        await self.pparent.drawable_is_focused(event)

    async def on_mouse_up(self, event: events.MouseUp):
        self.capture_mouse(False)
        await self.pparent.drawable_is_unfocused(event)

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        ...

    async def on_enter(self, event: events.Enter):
        await self.pparent.on_enter(event)

    async def on_leave(self, event: events.Leave):
        await self.pparent.on_leave(event)


class Body(DrawablePart):
    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.pparent.drawable_is_moved(event)


class Resizer(DrawablePart):
    def __init__(
        self,
        parent: Drawable,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        body: str = "",
    ) -> None:
        super().__init__(parent, name=name, id=id, classes=classes, body=body)
        self.styles.layer = f"{id}"

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.pparent.drawable_is_resized(event)
