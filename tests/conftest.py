"""
Enable the server's test fixture and import the providers of this repository.

`mass` gives a started server in dev mode with this repository as its local provider folder.
"""

from pathlib import Path

from music_assistant import providers

# a test imports a provider as music_assistant.providers.<domain>, the way the server loads it;
# first in the path, so it is this repository's copy while the server still ships its own
providers.__path__.insert(0, str(Path(__file__).parents[1] / "providers"))

pytest_plugins = ["music_assistant.testing"]
