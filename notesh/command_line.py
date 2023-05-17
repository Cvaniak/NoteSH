#!/usr/bin/env python
from __future__ import annotations

from notesh.main import NoteApp

def run():
    import argparse

    parser = argparse.ArgumentParser(description="Run Sticky Notes in your Terminal!")
    parser.add_argument("-f", "--file", default=NoteApp.DEFAULT_FILE, help=f"Notes file to use. Defaults to $NOTESH_FILE or $XDG_DATA_HOME/notesh/notes.json (currently: {NoteApp.DEFAULT_FILE!r})", required=False)
    argsx = parser.parse_args()
    NoteApp(file=argsx.file).run()


if __name__ == "__main__":
    run()
