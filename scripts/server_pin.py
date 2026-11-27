"""
Move the server these providers are developed against to a release of the server.

It sets the release in the `music-assistant` line of pyproject.toml and copies the requirements
of the server's Sendspin provider, which the server starts at every boot. Run it from the root of
the repository, then lock:

    uv run python scripts/server_pin.py 2.11.0
    uv lock
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

PYPROJECT = Path(__file__).parents[1] / "pyproject.toml"
# a release of the server, such as 2.11.0, 2.11.0b10 or 2.11.0.dev2026112603
VERSION = re.compile(r"\d+\.\d+\.\d+(?:b\d+|rc\d+|\.dev\d+)?")
# what follows the @ of the server line
PIN = re.compile(r'(?<="music-assistant @ git\+https://github\.com/music-assistant/server@)[^"]+')
# the requirements in the sendspin dependency group
SENDSPIN = re.compile(r'(?<=^sendspin = \[\n)(?:  "[^"\n]+",\n)*(?=\]$)', re.MULTILINE)
MANIFEST = (
    "https://raw.githubusercontent.com/music-assistant/server/{}/"
    "music_assistant/providers/sendspin/manifest.json"
)


def main() -> int:
    """Move the pin to the release given on the command line and return the exit code."""
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    version = sys.argv[1]
    if not VERSION.fullmatch(version):
        print(f"{version!r} is not a release of the server, such as 2.11.0 or 2.11.0b10")
        return 1
    with urllib.request.urlopen(MANIFEST.format(version), timeout=30) as response:  # noqa: S310 - a fixed https address
        requirements = json.load(response)["requirements"]
    lines = "".join(f'  "{requirement}",\n' for requirement in requirements)
    content = PYPROJECT.read_text(encoding="utf-8")
    content, pins = PIN.subn(version, content)
    content, blocks = SENDSPIN.subn(lambda _: lines, content)
    if pins != 1 or blocks != 1:
        print("pyproject.toml does not hold the server line and the Sendspin requirements once")
        return 1
    PYPROJECT.write_text(content, encoding="utf-8")
    print(f"the server is now {version}; now run: uv lock && uv run pytest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
