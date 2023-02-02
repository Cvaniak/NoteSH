#!/usr/bin/env python
from notesh.main import NoteApp


def run():
    import argparse

    parser = argparse.ArgumentParser(description="Run Sticky Notes in your Terminal!")
    parser.add_argument("-f", "--file", default="notes.json", required=False)
    argsx = parser.parse_args()
    NoteApp(file=argsx.file).run()


if __name__ == "__main__":
    run()
