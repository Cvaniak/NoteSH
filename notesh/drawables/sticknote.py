from __future__ import annotations

from typing import Any, Optional, OrderedDict, Type, TypeVar

from textual import events
from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Horizontal, Vertical
from textual.geometry import Offset, Size
from textual.widget import Widget
from textual.widgets import Input

from notesh.drawables.drawable import Drawable, DrawablePart, Resizer
from notesh.utils import generate_short_uuid
from notesh.widgets.multiline_input import MultilineArray


def build_color(any_color: str | Color) -> tuple[Color, Color, Color, Color]:
    if isinstance(any_color, str):
        color: Color = Color.parse(any_color)
    else:
        color = any_color

    return (color.lighten(0.13), color, color.darken(0.12), color.darken(0.3))


_T = TypeVar("_T")


class Note(Drawable):
    type: str = "note"

    def __init__(
        self,
        title: str = "",
        body: str = "",
        color: str = "#ffaa00",
        pos: Offset = Offset(0, 0),
        size: Size = Size(20, 14),
        parent: Optional[Widget] = None,
        id: str | None = None,
    ) -> None:
        if id is None or id == "":
            id = f"note-{generate_short_uuid()}"
        self._title = title
        self._body = body
        super().__init__(id=id, color=color, pos=pos, parent=parent, size=size)

    def init_parts(self) -> None:
        self.title = NoteTop(id=f"note-top", parent=self, body=self._title)
        self.body = NoteBody(id=f"note-body", parent=self, body=self._body)
        self.spacer = Spacer(body="▌", id=f"note-spacer", parent=self)
        self.resizer_left = ResizerLeft(body="▌", id=f"note-resizer-left", parent=self)
        self.resizer = Resizer(body="◢█", id=f"note-resizer", parent=self)

    def drawable_body(self) -> ComposeResult:
        yield Vertical(
            Vertical(
                self.title,
                self.spacer,
                id="note-toper",
            ),
            self.body,
            Horizontal(
                self.resizer_left,
                self.resizer,
                id="note-resizer-bar",
            ),
        )

    def change_color(self, new_color: str | Color, duration: float = 1.0, part_type: str = "body") -> None:
        if isinstance(new_color, str):
            base_color = Color.parse(new_color)
        else:
            base_color = new_color

        self.color = base_color
        self.update_layout(duration)

    def update_layout(self, duration: float = 1.0):
        base_color = self.color
        if self.is_entered:
            base_color = base_color.darken(0.1) if base_color.brightness > 0.9 else base_color.lighten(0.1)

        lighter, default, darker, much_darker = build_color(base_color)

        self.spacer.styles.background = much_darker
        self.spacer.styles.color = lighter

        self.title.styles.animate("background", value=default, duration=duration)
        self.title.styles.border_top = ("outer", lighter)
        self.title.styles.border_left = ("outer", lighter)
        self.title.styles.border_right = ("outer", much_darker)

        self.body.styles.animate("background", value=darker, duration=duration)
        self.body.styles.border_right = ("outer", much_darker)
        self.body.styles.border_bottom = ("none", much_darker)
        self.body.styles.border_left = ("outer", lighter)

        self.resizer_left.styles.background = much_darker
        self.resizer_left.styles.color = lighter

        self.resizer.styles.background = much_darker
        self.resizer.styles.color = default

    def sidebar_layout(self, widgets: OrderedDict[str, Widget]) -> None:
        widgets["input"].remove_class("-hidden")
        widgets["multiline_array"].remove_class("-hidden")
        widgets["body_color_picker"].remove_class("-hidden")
        widgets["delete_button"].remove_class("-hidden")

        widgets["input"].value = str(self.title.body)
        widgets["multiline_array"].recreate_multiline(str(self.body.body))
        widgets["body_color_picker"].update_colors(self.color)

    def input_changed(self, event: Input.Changed):
        self.title.body = str(event.value)

    def multiline_array_changed(self, event: MultilineArray.Changed):
        text = [str(x.value) for x in event.input.lines]
        self.body.body = "  \n".join(text)

    def dump(self) -> dict[str, Any]:
        return {
            "title": self.title.body,
            "body": self.body.body,
            "pos": (self.styles.offset.x.value, self.styles.offset.y.value),
            "color": self._last_color.hex6,
            "size": (self.styles.width.value, self.styles.height.value),
            "type": self.type,
        }

    @classmethod
    def load(cls: Type[_T], obj: dict[Any, Any], drawable_id: str, offset: Offset = Offset(0, 0)):
        return cls(
            id=drawable_id,
            title=obj["title"],
            body=obj["body"],
            color=obj["color"],
            pos=Offset(*obj["pos"]) - offset,
            size=Size(*obj["size"]),
        )


class NoteBody(DrawablePart):
    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.pparent.drawable_is_moved(event)


class NoteTop(DrawablePart):
    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.pparent.drawable_is_moved(event)


class Spacer(DrawablePart):
    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.pparent.drawable_is_moved(event)


class ResizerLeft(DrawablePart):
    async def on_mouse_move(self, event: events.MouseMove) -> None:
        await self.pparent.drawable_is_moved(event)
