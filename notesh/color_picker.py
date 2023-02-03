from __future__ import annotations

from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Grid, Horizontal, Vertical
from textual.events import MouseScrollDown, MouseScrollUp
from textual.message import Message, MessageTarget
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static
from random import randint


class ColorPickerRandom(Button):
    ...


class ColorPickerDisplay(Static):
    ...


class ColorPickerChanger(Grid):
    value: reactive[int] = reactive(0)

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        parent=None,
        color_arg="",
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
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

    def watch_value(self, new_value):
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
    r: reactive = reactive(0)
    g: reactive = reactive(0)
    b: reactive = reactive(0)
    hue: reactive = reactive(0)
    color_display = ColorPickerDisplay("VV Scroll to Change VV")

    class Change(Message):
        def __init__(self, sender: MessageTarget, color) -> None:
            super().__init__(sender)
            self.color = color

    def compose(self) -> ComposeResult:
        yield Static("Color Picker", id="color-picker-title")
        yield self.color_display
        self.color_changers = {
            "r": ColorPickerChanger(color_arg="r", parent=self, id="change-r"),
            "g": ColorPickerChanger(color_arg="g", parent=self, id="change-g"),
            "b": ColorPickerChanger(color_arg="b", parent=self, id="change-b"),
        }
        yield Horizontal(*self.color_changers.values(), id="color-changers")

        yield Horizontal(
            Button("Random Color", id="random-color"),
            id="random-hor",
        )

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)
        self.color_display.styles.background = Color(self.r, self.g, self.b)

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

        await self.emit(self.Change(self, color))

    def on_button_pressed(self, event: Button.Pressed):
        if event.sender.id == "random-color":
            for i in "rgb":
                setattr(self, i, randint(30, 220))

    @staticmethod
    def _clamp(value):
        return max(0, min(value, 255))

    def validate_r(self, new_value):
        return self._clamp(new_value)

    def validate_g(self, new_value):
        return self._clamp(new_value)

    def validate_b(self, new_value):
        return self._clamp(new_value)

    async def watch_r(self, new_value: float):
        await self.update_color()

    async def watch_g(self, new_value: float):
        await self.update_color()

    async def watch_b(self, new_value: float):
        await self.update_color()
