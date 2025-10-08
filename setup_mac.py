"""Build script for creating a standalone macOS application bundle.

This repository primarily targets running Deep Live Cam via Python, but some
contributors prefer shipping a double-clickable ``.app`` bundle for macOS
users.  ``py2app`` is the most straightforward tool for packaging Tkinter
applications on macOS, so this script wraps the existing ``run.py`` entry
point and collects the resource folders required at runtime.

Usage::

    python3 setup_mac.py py2app

The command will produce ``dist/Deep Live Cam.app``.  Make sure the ``models``
directory already contains the required model weights before running the
build.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Tuple

from setuptools import setup


ROOT = Path(__file__).resolve().parent


APP: List[str] = ["run.py"]

# Directories that should be copied verbatim into the application bundle so
# the packaged app has access to media assets, localization files, and the
# downloaded models.
RESOURCE_FOLDERS = ["media", "models", "locales"]

# Individual resource files that the application expects to load from disk.
RESOURCE_FILES = ["mypi.ini", os.path.join("modules", "ui.json")]


def _collect_data_files(paths: Iterable[str]) -> List[Tuple[str, List[str]]]:
    """Return a list of data-file tuples compatible with ``setuptools``.

    Each tuple contains the destination directory within the bundle and the
    list of files that should be copied there.  ``py2app`` will merge these
    into ``Resources`` inside the generated ``.app`` package.
    """

    data_files: List[Tuple[str, List[str]]] = []

    for relative in paths:
        absolute = ROOT / relative

        if absolute.is_dir():
            for path in absolute.rglob("*"):
                if path.is_file():
                    destination = os.path.relpath(path.parent, ROOT)
                    data_files.append((destination, [str(path)]))
        elif absolute.is_file():
            destination = os.path.relpath(absolute.parent, ROOT)
            data_files.append((destination, [str(absolute)]))

    return data_files


OPTIONS = {
    "argv_emulation": True,
    # The application relies on dynamic imports for some submodules, so we
    # keep the zipfile uncompressed to simplify loading resources.
    "compressed": False,
    # ``py2app`` is usually able to discover the required packages
    # automatically.  Explicitly include the project package to be safe.
    "packages": ["modules"],
}


setup(
    name="Deep Live Cam",
    app=APP,
    version="2.2",
    options={"py2app": OPTIONS},
    data_files=_collect_data_files(RESOURCE_FOLDERS + RESOURCE_FILES),
    setup_requires=["py2app"],
)
