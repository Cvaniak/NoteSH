from __future__ import annotations

from typing import Any, Optional, cast

from textual.containers import Container
from textual.events import Click, MouseDown, MouseMove, MouseUp
from textual.geometry import Offset, Size
from textual.message import Message, MessageTarget
from textual.widget import Widget

from notesh.drawables.box import Box
from notesh.drawables.drawable import Drawable
from notesh.drawables.sticknote import Note

CHUNK_SIZE = Offset(20, 5)


class PlayArea(Container):
    drawables: list[Drawable] = []
    is_draggin = False
    focused_drawable: Optional[Drawable] = None

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        min_size: Size = Size(0, 0),
        max_size: Size = Size(100, 40),
        screen_size: Size = Size(100, 100),
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        calculated_width, calculated_height = self._calculate_size(min_size, max_size)
        self.styles.width, self.styles.height = calculated_width, calculated_height
        self.offset += self._calculate_additional_offset(screen_size, Size(calculated_width, calculated_height))

    def add_new_drawable(self, drawable_type: str) -> Drawable:
        d = {"note": Note, "box": Box}
        drawable = cast(Drawable, d.get(drawable_type, Drawable)())
        self._mount_drawable(drawable)

        return drawable

    def add_parsed_drawable(self, obj: dict[Any, Any], drawable_id: str, offset: Offset = Offset(0, 0)) -> None:
        drawable_type = obj["type"]
        d = {"note": Note, "box": Box}
        drawable = cast(Drawable, d.get(drawable_type, Drawable).load(obj, drawable_id, offset))
        self._mount_drawable(drawable)

    def clear_drawables(self) -> None:
        while self.drawables:
            self.drawables.pop().remove()

    def delete_drawable(self, drawable: Optional[Drawable] = None) -> None:
        if drawable is None:
            drawable = self.focused_drawable
        if drawable is None:
            return

        self.drawables = [note for note in self.drawables if note != drawable]
        drawable.remove()

    async def on_mouse_move(self, event: MouseMove) -> None:
        if event.ctrl and self.is_draggin:
            await self._move_play_area(event.delta)

    async def on_mouse_down(self, event: MouseDown) -> None:
        if event.ctrl:
            self.is_draggin = True
            self.capture_mouse()

    async def on_mouse_up(self, _: MouseUp) -> None:
        self.is_draggin = False
        self.capture_mouse(False)

    async def on_click(self, event: Click) -> None:
        await self.emit(PlayArea.Clicked(self))

    async def on_drawable_move(self, event: Drawable.Move) -> None:
        await self._resize_field_to_drawable(event.drawable, event.offset)

    async def on_drawable_focus(self, message: Drawable.Focus) -> None:
        drawable = self.screen.get_widget_by_id(message.index)
        self.focused_drawable = cast(Drawable, drawable)

    async def move_drawable(self, direction: str, value: int) -> None:
        if self.focused_drawable is not None:
            await self.focused_drawable.move(direction, value)

    def _calculate_additional_offset(self, size_a: Size, size_b: Size):
        return Offset((size_a.width - size_b.width) // 2, (size_a.height - size_b.height) // 2)

    def _calculate_size(self, min_size: Size, max_size: Size):
        calculated_width = ((max_size.width - min_size.width + 1) // CHUNK_SIZE.x) * CHUNK_SIZE.x + CHUNK_SIZE.x
        calculated_height = ((max_size.height - min_size.height + 1) // CHUNK_SIZE.y) * CHUNK_SIZE.y + CHUNK_SIZE.y
        return calculated_width, calculated_height

    def _mount_drawable(self, drawable: Drawable) -> None:
        self.drawables.append(drawable)
        self.mount(drawable)
        self.is_draggin = False

    async def _move_play_area(self, offset: Offset) -> None:
        self.offset = self.offset + offset

    async def _resize_field_to_drawable(self, drawable: Drawable, offset: Offset = Offset(0, 0)) -> None:
        xx, yy = offset.x, offset.y
        if drawable.region.right + xx >= self.region.right:
            self.styles.width = self.styles.width.value + CHUNK_SIZE.x

        if drawable.region.bottom + yy >= self.region.bottom:
            self.styles.height = self.styles.height.value + CHUNK_SIZE.y

        if drawable.region.x + xx <= self.region.x:
            self.styles.width = self.styles.width.value + CHUNK_SIZE.x
            self.styles.offset = (self.styles.offset.x.value - CHUNK_SIZE.x, self.styles.offset.y.value)
            for child in self.children:
                child.styles.offset = (child.styles.offset.x.value + CHUNK_SIZE.x, child.styles.offset.y.value)

        if drawable.region.y + yy <= self.region.y:
            self.styles.height = self.styles.height.value + CHUNK_SIZE.y
            self.styles.offset = (self.styles.offset.x.value, self.styles.offset.y.value - CHUNK_SIZE.y)
            for child in self.children:
                child.styles.offset = (child.styles.offset.x.value, child.styles.offset.y.value + CHUNK_SIZE.y)

    class Clicked(Message):
        def __init__(
            self,
            sender: MessageTarget,
        ) -> None:
            super().__init__(sender)
