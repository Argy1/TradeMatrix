"""Train, store and activate the live models.

    uv run python -m app.ml.train_models                              # every coin, 1h + 4h + 1d
    uv run python -m app.ml.train_models --timeframes 1h,4h --symbols DOGE,ADA

Why a separate file: pickle (and joblib) saves an object together with the import path of its
class. A module started with `python -m` is named `__main__`, so running app.ml.registry
directly would save `__main__.ModelBundle`, which the worker cannot load. Keeping the command
here makes the files say `app.ml.registry.ModelBundle`.
"""

import argparse
import asyncio
import sys

from app.ml.registry import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Train, store and activate the live models.")
    parser.add_argument("--timeframes", default="1h,4h,1d")
    parser.add_argument("--symbols", default="", help="default: every active coin (1d is pooled)")
    args = parser.parse_args()
    timeframes = [t for t in args.timeframes.split(",") if t]
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()] or None
    asyncio.run(run(timeframes, symbols))
    return 0


if __name__ == "__main__":
    sys.exit(main())
