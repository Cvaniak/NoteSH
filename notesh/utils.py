from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import uuid
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

import tomli
from textual.geometry import Size

if TYPE_CHECKING:
    from textual.containers import Container

    from notesh.drawables.drawable import Drawable
    from notesh.main import NoteApp


def generate_short_uuid() -> str:
    return uuid.uuid4().hex[:4]


def calculate_size_for_file(file_name: str) -> tuple[Size, Size]:
    if not os.path.exists(file_name):
        return Size(0, 0), Size(50, 20)

    with open(file_name, "r") as file:
        obj = json.load(file)

    keys = [x for x in obj.keys() if x not in ["background", "layers"]]

    mxx, mxy = -sys.maxsize, -sys.maxsize
    mnx, mny = sys.maxsize, sys.maxsize
    for drawable in sorted(keys, key=lambda x: obj["layers"].index(x)):
        mxx = max(mxx, obj[drawable]["pos"][0] + obj[drawable]["size"][0])
        mnx = min(mnx, obj[drawable]["pos"][0])
        mxy = max(mxy, obj[drawable]["pos"][1] + obj[drawable]["size"][1])
        mny = min(mny, obj[drawable]["pos"][1])

    mxx = 50 if mxx == sys.maxsize else max(mxx, 50)
    mxy = 20 if mxy == sys.maxsize else max(mxy, 20)
    mnx = 0 if mnx == sys.maxsize else mnx
    mny = 0 if mny == sys.maxsize else mny

    return Size(mnx, mny), Size(mxx, mxy)


def save_drawables(
    file_name: str, drawables: list[Drawable], layers: list[str], background: Optional[dict[Any, Any]] = None
) -> None:
    obj: dict[str, Any] = {"layers": []}
    layers_set: set[str] = set()
    drawable: Drawable
    for drawable in drawables:
        if drawable.id is None:
            continue
        obj[drawable.id] = drawable.dump()
        layers_set.add(drawable.id)

    obj["layers"].extend([x for x in layers if x in layers_set])
    if background is not None:
        obj["background"] = background

    Path(file_name).parent.mkdir(parents=True, exist_ok=True)
    with open(file_name, "w") as file:
        json.dump(obj, file, indent=4)


def load_drawables(file_name: str) -> tuple[list[tuple[str, dict[Any, Any]]], Optional[dict[Any, Any]]]:
    if not os.path.exists(file_name):
        return [], None

    with open(file_name, "r") as file:
        obj = json.load(file)

    if not obj:
        return [], None

    background = None
    if "background" in obj:
        background = obj["background"]

    keys = [x for x in obj.keys() if x not in ["background", "layers"]]
    return [(name, obj[name]) for name in sorted(keys, key=lambda x: obj["layers"].index(x))], background


def load_binding_config_file(file_name: str) -> dict[str, Any]:
    if not os.path.exists(file_name):
        return {}
    with open(file_name, "rb") as f:
        conf = tomli.load(f)
    return conf


def set_bindings(
    where: Container | NoteApp,
    config: dict[str, list[str] | str],
    show: bool = False,
    func: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None,
):
    for key, value in config.items():
        key_binding: str
        description: str
        if isinstance(value, list):
            key_binding, description = value[0], value[1]
        elif isinstance(value, str):  # type: ignore
            key_binding, description = value, ""
        else:
            continue
        where._bindings.bind(key_binding, key, description, show=show, priority=False)  # type: ignore
        if func is not None:
            setattr(where, f"action_{key}", partial(func, direction=key))
