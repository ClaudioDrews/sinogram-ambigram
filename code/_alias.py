"""Shared helper for deprecated module aliases.

Every renamed pipeline stage keeps its original filename as a thin shim for one
release. Importing or running the old name emits a ``DeprecationWarning`` and
forwards to the new module.
"""
from __future__ import annotations

import importlib
import runpy
import sys
import warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent


def make_alias(old_name: str, new_module: str, removed_in: str) -> dict:
    """Return the public namespace of ``new_module`` for use as a deprecated alias.

    The caller assigns the result into its own ``globals()`` so that
    ``from build import resample_polyline`` keeps working.
    """
    warnings.warn(
        f"code/{old_name}.py is deprecated and will be removed in release "
        f"{removed_in}; use code/{new_module}.py instead.",
        DeprecationWarning,
        stacklevel=3,
    )
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    module = importlib.import_module(new_module)
    namespace = {k: v for k, v in vars(module).items() if not k.startswith("__")}
    if sys.argv and sys.argv[0].endswith(f"{old_name}.py"):
        runpy.run_path(str(HERE / f"{new_module}.py"), run_name="__main__")
    return namespace