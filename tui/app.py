from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from backend.core.event_bus import event_bus


class BattleFeed(Static):
    pass


class RegistryPane(Static):
    pass


class RewardBar(Static):
    pass


class GoatTUI(App):
    CSS_PATH = "tui.css"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical():
                yield BattleFeed("Waiting for events...", id="feed")
            with Vertical():
                yield RegistryPane("Registry updates", id="registry")
        yield RewardBar("Rewards: Red 0.0 | Blue 0.0", id="reward")
        yield Footer()

    async def on_mount(self) -> None:
        self.queue = await event_bus.subscribe("*")
        self.set_interval(0.2, self._poll)

    async def _poll(self) -> None:
        while not self.queue.empty():
            event = await self.queue.get()
            feed = self.query_one("#feed", BattleFeed)
            feed.update(f"{feed.renderable}\n{event['event']}: {event['payload']}")


def run() -> None:
    GoatTUI().run()


if __name__ == "__main__":
    run()
