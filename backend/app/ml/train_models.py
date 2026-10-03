"""Train, store and activate the live models.

    uv run python -m app.ml.train_models            # all timeframes
    uv run python -m app.ml.train_models 1h         # one timeframe

Why a separate file: pickle (and joblib) saves an object together with the import path of its
class. A module started with `python -m` is named `__main__`, so running app.ml.registry
directly would save `__main__.ModelBundle`, which the worker cannot load. Keeping the command
here makes the files say `app.ml.registry.ModelBundle`.
"""

import asyncio
import sys

from app.ml.registry import run


def main() -> int:
    timeframes = sys.argv[1].split(",") if len(sys.argv) > 1 else ["1h", "4h", "1d"]
    asyncio.run(run(timeframes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
