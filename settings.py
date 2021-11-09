"""Settings for the Hat Game."""

import os
from pathlib import Path

CWD = Path(os.getcwd())
GAME_SCOPE = "LOCAL"  # Could be "GLOBAL" or "LOCAL"
LOCAL_VOCAB_PATH = CWD / "text_samples" / "nouns_top_50.txt"
N_EXPLAIN_WORDS = 10
N_GUESSING_WORDS = 5
N_ROUNDS = 1
CRITERIA = "soft"
