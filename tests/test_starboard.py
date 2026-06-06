import asyncio
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STARBOARD_PATH = ROOT / "cogs" / "starboard.py"
spec = importlib.util.spec_from_file_location("starboard", STARBOARD_PATH)
assert spec is not None
assert spec.loader is not None
starboard_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(starboard_module)
Starboard = starboard_module.Starboard


class FakeChannel:
    mention = "#general"

    def __init__(self, nsfw=False):
        self._nsfw = nsfw

    def is_nsfw(self):
        return self._nsfw


class FakeBot:
    def get_channel(self, _channel_id):
        return SimpleNamespace()


def make_reaction(count, emoji="<:OnPhone:1062142401973588039>"):
    return SimpleNamespace(
        emoji=emoji,
        count=count,
        message=SimpleNamespace(
            id=123,
            channel=FakeChannel(),
        ),
    )


def test_starboard_requires_three_matching_reactions_before_posting():
    starboard = Starboard(FakeBot())
    starboard.create_starboard_post = AsyncMock()
    starboard.update_reaction_count = AsyncMock()

    asyncio.run(starboard.on_reaction_add(make_reaction(1), SimpleNamespace()))
    asyncio.run(starboard.on_reaction_add(make_reaction(2), SimpleNamespace()))

    starboard.create_starboard_post.assert_not_called()
    starboard.update_reaction_count.assert_not_called()

    asyncio.run(starboard.on_reaction_add(make_reaction(3), SimpleNamespace()))

    starboard.create_starboard_post.assert_awaited_once()
    starboard.update_reaction_count.assert_not_called()


def test_starboard_ignores_non_matching_emoji_even_at_threshold():
    starboard = Starboard(FakeBot())
    starboard.create_starboard_post = AsyncMock()
    starboard.update_reaction_count = AsyncMock()

    asyncio.run(starboard.on_reaction_add(make_reaction(3, emoji="👍"), SimpleNamespace()))

    starboard.create_starboard_post.assert_not_called()
    starboard.update_reaction_count.assert_not_called()
