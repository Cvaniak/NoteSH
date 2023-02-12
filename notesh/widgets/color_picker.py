from __future__ import annotations

from random import randint

from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Grid, Horizontal, Vertical
from textual.events import MouseScrollDown, MouseScrollUp
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static


class ColorPickerRandom(Button):
    ...


class ColorPickerDisplay(Static):
    ...


class ColorPickerChanger(Grid):
    value: reactive[int] = reactive(0)

    def __init__(
        self,
        *children: Widget,
        parent: ColorPicker,
        color_arg: str = "",
        id: str | None = None,
    ) -> None:
        super().__init__(*children, id=id)
        self.pparent = parent
        self.argument = color_arg
        self.static_widget = Static("  ", classes="-color")
        w = {"r": 50, "g": 50, "b": 50}
        w.update({self.argument: 210})
        self.static_widget.styles.background = Color(**w)
        self.value = getattr(self.pparent, self.argument)

        self.button_up = Button("▲", id="up", classes="-up")
        self.button_down = Button("▼", id="down", classes="-down")

    def compose(self) -> ComposeResult:
        yield self.static_widget
        yield self.button_up
        yield self.button_down

    def watch_value(self, new_value: int):
        self.static_widget.update(f"{self.argument}\n{new_value:<3}")

    def on_button_pressed(self, event: Button.Pressed):
        new_value = 0
        if event.sender.id == "up":
            new_value = 10
        if event.sender.id == "down":
            new_value = -10

        _value = getattr(self.pparent, self.argument) + new_value
        setattr(self.pparent, self.argument, _value)
        self.value = getattr(self.pparent, self.argument)

    async def on_mouse_scroll_down(self, event: MouseScrollDown):
        _value = getattr(self.pparent, self.argument) + 1
        setattr(self.pparent, self.argument, _value)
        self.value = getattr(self.pparent, self.argument)

    async def on_mouse_scroll_up(self, event: MouseScrollUp):
        _value = getattr(self.pparent, self.argument) - 1
        setattr(self.pparent, self.argument, _value)
        self.value = getattr(self.pparent, self.argument)


class ColorPicker(Vertical):
    r: reactive[int] = reactive(0)
    g: reactive[int] = reactive(0)
    b: reactive[int] = reactive(0)
    hue: reactive[int] = reactive(0)

    def __init__(
        self,
        *children: Widget,
        title: str = "Color Picker",
        type: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.color_display = ColorPickerDisplay("")
        self.color_display.styles.background = Color(self.r, self.g, self.b)
        self.title = Static(title, id="color-picker-title")
        self.type = type
        self.color_changers = {
            "r": ColorPickerChanger(color_arg="r", parent=self, id="change-r"),
            "g": ColorPickerChanger(color_arg="g", parent=self, id="change-g"),
            "b": ColorPickerChanger(color_arg="b", parent=self, id="change-b"),
        }

    def compose(self) -> ComposeResult:
        yield self.title
        yield self.color_display
        yield Horizontal(*self.color_changers.values(), Button(" ??  ?? ", id="random-color"), id="color-changers")

    def update_colors(self, color: Color):
        self.r, self.g, self.b = color.rgb
        for c in self.color_changers:
            self.color_changers[c].value = getattr(self, c)

        self.color_display.styles.background = color

    async def update_color(self):
        color = Color(self.r, self.g, self.b)
        self.color_display.styles.background = color
        for c in self.color_changers:
            self.color_changers[c].value = getattr(self, c)

        await self.emit(self.Change(self, color, argument=self.type))

    def on_button_pressed(self, event: Button.Pressed):
        if event.sender.id == "random-color":
            for i in "rgb":
                setattr(self, i, randint(30, 220))

    @staticmethod
    def _clamp(value: int) -> int:
        return max(0, min(value, 255))

    def validate_r(self, new_value: int) -> int:
        return self._clamp(new_value)

    def validate_g(self, new_value: int) -> int:
        return self._clamp(new_value)

    def validate_b(self, new_value: int) -> int:
        return self._clamp(new_value)

    async def watch_r(self, new_value: int):
        await self.update_color()

    async def watch_g(self, new_value: int):
        await self.update_color()

    async def watch_b(self, new_value: int):
        await self.update_color()

    class Change(Message):
        def __init__(self, sender: MessageTarget, color: Color | str, argument: str) -> None:
            super().__init__(sender)
            self.color = color
            self.type = argument
