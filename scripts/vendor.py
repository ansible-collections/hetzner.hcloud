#!/usr/bin/env python3

import re
from argparse import ArgumentParser
from pathlib import Path
from textwrap import dedent


def main(package: Path) -> int:
    for file in package.rglob("*.py"):
        content = file.read_text()

        # Wrap requests imports
        content = re.sub(
            r"import requests",
            dedent(
                r"""
                try:
                    import requests
                except ImportError:
                    requests = None
                """
            ).strip(),
            content,
        )

        # Wrap dateutil imports
        content = re.sub(
            r"from dateutil.parser import isoparse",
            dedent(
                r"""
                try:
                    from dateutil.parser import isoparse
                except ImportError:
                    isoparse = None
                """
            ).strip(),
            content,
        )

        # Remove requests.Response typings
        content = re.sub(
            r": requests\.Response",
            r"",
            content,
        )

        file.write_text(content)

    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("package", help="path to the vendored package.")
    args = parser.parse_args()

    raise SystemExit(main(package=Path(args.package)))
