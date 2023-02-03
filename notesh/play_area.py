from __future__ import annotations

from textual.containers import Container
from textual.geometry import Offset, Size
from textual.widget import Widget
from notesh.sticknote import Note
from textual.events import MouseDown, MouseMove, MouseUp

CHUNK_SIZE = Offset(20, 5)


class PlayArea(Container):
    notes: list[Note] = []
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

    def add_new_note(
        self,
        note_id: str = "",
        title: str = "",
        body: str = "",
        color: str = "#ffaa00",
        pos: Offset = Offset(0, 0),
        size: Size = Size(20, 14),
    ) -> None:
        note: Note = Note(
            id=f"{note_id}",
            title=title,
            body=body,
            color=color,
            position=pos,
            size=size,
            parent=self,
        )
        self.notes.append(note)
        self.mount(note)
        self.is_draggin = False

    def remove_notes(self) -> None:
        while self.notes:
            self.notes.pop().remove()

    def delete_sticknote(self, sticknote: Note) -> None:
        self.notes = [note for note in self.notes if note != sticknote]
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

    async def on_note_move(self, event: Note.Move) -> None:
        note = event.note
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
