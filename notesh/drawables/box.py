from __future__ import annotations

from typing import Any, Optional, OrderedDict, Type, TypeVar

from textual.app import events
from textual.color import Color
from textual.geometry import Offset, Size
from textual.reactive import reactive
from textual.widget import Widget

from notesh.drawables.drawable import Body, Drawable, Resizer
from notesh.widgets.multiline_input import MultilineArray

BORDERS = [
    "outer",
    "ascii",
    "round",
    "solid",
    "double",
    "dashed",
    "heavy",
    "hkey",
    "vkey",
    "none",
]

_T = TypeVar("_T")


class Box(Drawable):
    type: str = "box"
    border_index: int = 0
    border_type: reactive[str] = reactive(BORDERS[border_index], always_update=True)

    def __init__(
        self,
        body: str = "",
        color: str = "#ffaa00",
        pos: Offset = Offset(0, 0),
        size: Size = Size(20, 14),
        parent: Optional[Widget] = None,
        border_color: str = "#ffaa00",
        border_type: str = "outer",
        id: str | None = None,
    ) -> None:
        super().__init__(id=id, init_parts=False, color=color, pos=pos, parent=parent, size=size, body=body)

        self.border_color = Color.parse(border_color)
        self._last_border_color = self.border_color
        self.border_index = BORDERS.index(border_type)
        self.border_type = BORDERS[self.border_index]
        self._body = body

        self.init_parts()

    def init_parts(self) -> None:
        self.body = Body(self, body=self._body, id="default-body")
        self.resizer = Resizer(body=" ", id=f"{self.id}-resizer", parent=self)

    def change_color(self, new_color: str | Color, duration: float = 1.0, part_type: str = "body") -> None:
        if isinstance(new_color, str):
            base_color = Color.parse(new_color)
        else:
            base_color = new_color

        if part_type == "" or part_type == "body":
            self.color = base_color
        else:
            self.border_color = base_color
        self.update_layout(duration)

    def update_layout(self, duration: float = 1.0):
        base_color = self.color
        border_color = self.border_color
        if self.is_entered:
            base_color = base_color.darken(0.1) if base_color.brightness > 0.9 else base_color.lighten(0.1)
            border_color = border_color.darken(0.1) if border_color.brightness > 0.9 else border_color.lighten(0.1)

        self.body.styles.animate("background", value=base_color, duration=duration)

        self.body.styles.border = (self.border_type, border_color.darken(0.1))
        self.body.styles.border_left = (self.border_type, border_color.lighten(0.1))
        self.body.styles.border_top = (self.border_type, border_color.lighten(0.1))
        self.resizer.styles.animate("background", value=border_color.darken(0.1), duration=duration)

    def next_border(self):
        self.border_index = (self.border_index + 1) % len(BORDERS)
        self.border_type = BORDERS[self.border_index]
        self.update_layout(duration=1.0)

    def multiline_array_changed(self, event: MultilineArray.Changed):
        text = [str(x.value) for x in event.input.lines]
        self.body.body = "  \n".join(text)

    def sidebar_layout(self, widgets: OrderedDict[str, Widget]) -> None:
        widgets["multiline_array"].remove_class("-hidden")
        widgets["body_color_picker"].remove_class("-hidden")
        widgets["border_picker"].remove_class("-hidden")
        widgets["border_color_picker"].remove_class("-hidden")
        widgets["delete_button"].remove_class("-hidden")

        widgets["multiline_array"].recreate_multiline(str(self.body.body))
        widgets["body_color_picker"].update_colors(self.color)
        widgets["border_color_picker"].update_colors(self.border_color)

    def dump(self) -> dict[str, Any]:
        return {
            "body": self.body.body,
            "pos": (self.styles.offset.x.value, self.styles.offset.y.value),
            "color": self.color.hex6,
            "border_color": self._last_border_color.hex6,
            "border_type": self.border_type,
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
            border_color=obj["border_color"],
            border_type=obj["border_type"],
        )
