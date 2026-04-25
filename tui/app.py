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

    def __init__(self) -> None:
        super().__init__()
        self._feed_lines: list[str] = ["Waiting for events..."]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical():
                yield BattleFeed("\n".join(self._feed_lines), id="feed")
            with Vertical():
                yield RegistryPane("Registry updates", id="registry")
        yield RewardBar("Rewards: Red 0.0 | Blue 0.0", id="reward")
        yield Footer()

    async def on_mount(self) -> None:
        self.queue = await event_bus.subscribe("*")
        self.set_interval(0.2, self._poll)

    async def _poll(self) -> None:
        while True:
            try:
                event = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            self._feed_lines.append(f"{event['event']}: {event['payload']}")
            self._feed_lines = self._feed_lines[-80:]
            feed = self.query_one("#feed", BattleFeed)
            feed.update("\n".join(self._feed_lines))


def run() -> None:
    GoatTUI().run()


if __name__ == "__main__":
    run()
