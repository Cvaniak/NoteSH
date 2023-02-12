from __future__ import annotations

from typing import Any, cast

from textual.containers import Container
from textual.events import MouseDown, MouseMove, MouseUp
from textual.geometry import Offset, Size
from textual.widget import Widget

from notesh.drawables.box import Box
from notesh.drawables.drawable import Drawable
from notesh.drawables.sticknote import Note

CHUNK_SIZE = Offset(20, 5)


class PlayArea(Container):
    drawables: list[Drawable] = []
    is_draggin = False

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        min_size: Size = Size(0, 0),
        max_size: Size = Size(100, 40),
        screen_size: Size | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        calculated_width = ((max_size.width - min_size.width + 1) // CHUNK_SIZE.x) * CHUNK_SIZE.x + CHUNK_SIZE.x
        calculated_height = ((max_size.height - min_size.height + 1) // CHUNK_SIZE.y) * CHUNK_SIZE.y + CHUNK_SIZE.y
        self.styles.width = calculated_width
        self.styles.height = calculated_height
        self.offset += Offset(
            (screen_size.width - calculated_width) // 2, (screen_size.height - calculated_height) // 2
        )

    def add_new_drawable(self, drawable_type: str) -> None:

        if drawable_type == "note":
            note: Drawable = cast(Drawable, Note())
        elif drawable_type == "box":
            note: Drawable = cast(Drawable, Box())
        else:
            note: Drawable = Drawable()

        self.drawables.append(note)
        self.mount(note)
        self.is_draggin = False

    def add_parsed_drawable(self, obj: dict[Any, Any], drawable_id: str, offset: Offset = Offset(0, 0)) -> None:
        drawable_type = obj["type"]

        if drawable_type == "note":
            note: Drawable = cast(Drawable, Note.load(obj, drawable_id, offset))
        elif drawable_type == "box":
            note: Drawable = cast(Drawable, Box.load(obj, drawable_id, offset))
        else:
            note: Drawable = Drawable.load(obj, drawable_id, offset)

        self.drawables.append(note)
        self.mount(note)
        self.is_draggin = False

    def remove_drawables(self) -> None:
        while self.drawables:
            self.drawables.pop().remove()

    def delete_drawable(self, sticknote: Drawable) -> None:
        self.drawables = [note for note in self.drawables if note != sticknote]
        sticknote.remove()

    def on_mouse_move(self, event: MouseMove) -> None:
        if event.ctrl and self.is_draggin:
            self.offset = self.offset + event.delta

    async def on_mouse_down(self, event: MouseDown) -> None:
        if event.ctrl:
            self.is_draggin = True
            self.capture_mouse()

    async def on_mouse_up(self, event: MouseUp) -> None:
        self.is_draggin = False
        self.capture_mouse(False)

    async def on_drawable_move(self, event: Drawable.Move) -> None:
        note = event.drawable
        if note.region.right >= self.region.right:
            self.styles.width = self.styles.width.value + CHUNK_SIZE.x

        if note.region.bottom >= self.region.bottom:
            self.styles.height = self.styles.height.value + CHUNK_SIZE.y

        if note.region.x <= self.region.x:
            self.styles.width = self.styles.width.value + CHUNK_SIZE.x
            self.styles.offset = (self.styles.offset.x.value - CHUNK_SIZE.x, self.styles.offset.y.value)
            for child in self.children:
                child.styles.offset = (child.styles.offset.x.value + CHUNK_SIZE.x, child.styles.offset.y.value)

        if note.region.y <= self.region.y:
            self.styles.height = self.styles.height.value + CHUNK_SIZE.y
            self.styles.offset = (self.styles.offset.x.value, self.styles.offset.y.value - CHUNK_SIZE.y)
            for child in self.children:
                child.styles.offset = (child.styles.offset.x.value, child.styles.offset.y.value + CHUNK_SIZE.y)
