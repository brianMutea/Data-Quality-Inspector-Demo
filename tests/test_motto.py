"""Tests for optional QA motto lines."""

import random

from dqi.motto import MOTTOS, random_motto


def test_random_motto_is_deterministic_when_seed_fixed():
    random.seed(1337)
    a = random_motto()
    random.seed(1337)
    b = random_motto()
    assert a == b
    assert a in MOTTOS
