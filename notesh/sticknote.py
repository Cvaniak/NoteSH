from textual import events
from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Horizontal, Vertical
from textual.geometry import Offset, Size
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widget import Widget

from textual.widgets import Button, Static
from rich.markdown import Markdown

from notesh.utils import generate_short_uuid


def build_color(color: str):
    color: Color = Color.parse(color)
    return [color.lighten(0.13), color, color.darken(0.12), color.darken(0.3)]


class NoteBody(Static):
    body: reactive[str] = reactive("")

    def __init__(
        self,
        *children: Widget,
        parent=None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        body=body,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.pparent = parent
        self.body = body

    async def on_click(self, event: events.Click):
        layers = tuple(
            x for x in self.screen.styles.layers if x != self.pparent.styles.layer
        )
        self.screen.styles.layers = layers + (self.pparent.styles.layer,)
        await self.emit(Note.Focus(self, self.pparent.id, display_sidebar=True))

    def watch_body(self, body_text):
        self.update(Markdown(body_text))


class NoteTop(Static):
    body: reactive[str] = reactive("")

    def __init__(
        self,
        *children: Widget,
        parent=None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        body="",
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.clicked = Offset(0, 0)
        self.pparent: Note = parent
        self.body = body

    def watch_body(self, body_text):
        self.update(body_text)

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        ...
        if self.clicked is not None and event.button != 0:
            note = self.pparent
            # print(event.screen_offset, note.pparent.offset, note.virtual_region.offset, self.clicked, self.screen.scroll_target_y)
            # note.styles.offset = (
            #     event.screen_offset
            #     # - note.pparent.offset
            #     # - note.virtual_region.offset
            #     - self.clicked
            # )
            if event.delta:
                note.offset = note.offset + event.delta
                await self.emit(Note.Move(self, note=self.pparent))

            else:
                ...
            # print(self.region, self.screen.size, self.region.right, self.pparent.size.width)
            # if note.region.right > self.pparent.pparent.size.width:
            #     self.pparent.pparent.styles.width = self.pparent.pparent.styles.width.value + 20

    async def on_mouse_down(self, event: events.MouseDown):
        self.capture_mouse()
        self.clicked = event.offset
        # temp = self.virtual_region
        layers = tuple(
            x for x in self.screen.styles.layers if x != self.pparent.styles.layer
        )
        self.screen.styles.layers = layers + (self.pparent.styles.layer,)
        await self.emit(Note.Focus(self, self.pparent.id))

    async def on_mouse_up(self, event: events.MouseUp):
        self.capture_mouse(False)
        self.clicked = None


class Spacer(Static):
    ...


class ResizerLeft(Static):
    ...


class Resizer(Static):
    def __init__(
        self,
        *children: Widget,
        parent=None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.clicked = (0, 0)
        self.pparent = parent
        self.size_on_click = (0, 0)

    async def on_mouse_down(self, event: events.MouseDown):
        self.capture_mouse()
        self.clicked = (event.delta_x, event.delta_y)
        self.size_on_click = (self.parent.styles.width, self.parent.styles.height)

    async def on_mouse_up(self, event: events.MouseUp):
        self.capture_mouse(False)
        self.clicked = None

    def on_mouse_move(self, event: events.MouseMove) -> None:
        note: Note
        if self.clicked is not None and event.button != 0:
            note = self.pparent
            note.styles.width = note.styles.width.value + event.delta_x
            note.styles.height = note.styles.height.value + event.delta_y
            note.refresh()


class Note(Button):
    class Mess(Message):
        def __init__(self, sender: MessageTarget, value: str | None) -> None:
            super().__init__(sender)
            self.value = value

    class Focus(Message):
        def __init__(
            self, sender: MessageTarget, index, display_sidebar: bool = False
        ) -> None:
            super().__init__(sender)
            self.index = index
            self.display_sidebar = display_sidebar

    class Move(Message):
        def __init__(
                self, sender: MessageTarget, note: "Note", 
        ) -> None:
            super().__init__(sender)
            self.note = note

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        title="",
        body="",
        color="#ffaa00",
        position=Offset(0, 0),
        size=Size(20, 14),
        parent=None,
    ) -> None:
        if not id:
            id = f"note-{generate_short_uuid()}"
        super().__init__(*children, name=name, id=id, classes=classes)
        self.clicked = (0, 0)
        self.styles.layer = f"{id}"
        self.color = Color.parse(color)
        self.styles.offset = position
        self.styles.width = size.width
        self.styles.height = size.height

        self.title = NoteTop("", id=f"note-top", parent=self, body=title)
        self.body = NoteBody("", id=f"static-{self.id}", parent=self, body=body)
        self.spacer = Spacer("▌", id="spacer")
        self.resizer_left = ResizerLeft("▌", id="resizer-left")
        self.resizer = Resizer("◢█", id="resizer", parent=self)

        self.pparent = parent

    def compose(self) -> ComposeResult:
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
                id="note-resizer",
            ),
        )
        self.change_color(self.color, duration=0.0)
        self.screen.styles.layers = self.screen.styles.layers + (
            f"{self.styles.layer}",
        )

    async def on_mouse_release(self, event: events.MouseRelease):
        ...

    def change_color(self, base_color, duration=1.0):
        lighter, default, darker, much_darker = build_color(base_color)
        self.color = default
        self.spacer.styles.background = much_darker
        self.spacer.styles.color = lighter

        self.title.styles.animate("background", value=default, duration=duration)
        # self.title.styles.animate("border_top", value=("outer", lighter), duration=duration)
        # self.title.styles.border_left = ("outer", lighter)
        # self.title.styles.border_right = ("outer", much_darker)
        # self.title.styles.background = default
        self.title.styles.border_top = ("outer", lighter)
        self.title.styles.border_left = ("outer", lighter)
        self.title.styles.border_right = ("outer", much_darker)

        # self.body.styles.background = darker
        self.body.styles.animate("background", value=darker, duration=duration)
        self.body.styles.border_right = ("outer", much_darker)
        self.body.styles.border_bottom = ("none", much_darker)
        self.body.styles.border_left = ("outer", lighter)

        self.resizer_left.styles.background = much_darker
        self.resizer_left.styles.color = lighter

        self.resizer.styles.background = much_darker
        self.resizer.styles.color = lighter
