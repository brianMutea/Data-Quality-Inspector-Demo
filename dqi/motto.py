"""Optional whimsy: one-liners for humans who stare at null counts too long."""

from __future__ import annotations

import random

MOTTOS: tuple[str, ...] = (
    "Nulls are not empty— they are Schrödinger's cells.",
    "Measure twice, melt once: always profile before you panic.",
    "If your outlier is the story, the distribution is the setting.",
    "Duplicate rows wander in pairs—like lost socks.",
    "A tidy schema is a love letter to your future self.",
    "Today's forecast: intermittent confidence intervals.",
    "The World Bank does not owe you residuals—only indicators.",
)


def random_motto() -> str:
    """Return one pseudo-profound QA motto."""
    return random.choice(MOTTOS)
