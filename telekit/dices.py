from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Literal

import telebot
import telebot.types

__all__ = [
    "GameResult",
    "Dice",
    "Darts",
    "Basketball",
    "Football",
    "Bowling",
    "Casino",
]

# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class GameResult(ABC):
    """Base class for all Telegram dice game results."""

    def __init__(self, message: telebot.types.Message) -> None:
        if message.dice is None:
            raise ValueError("Message does not contain a dice")
        self._dice = message.dice

    # --- Abstract interface ---

    @property
    @abstractmethod
    def is_win(self) -> bool:
        """True if the result counts as a win."""

    @property
    @abstractmethod
    def score(self) -> int:
        """Normalised score from 0 to 100."""

    # --- Common ---

    @property
    def is_lose(self) -> bool:
        """True if the result counts as a lose."""
        return not self.is_win

    @property
    def value(self) -> int:
        """Raw Telegram dice value."""
        return self._dice.value

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"value={self.value}, is_win={self.is_win}, score={self.score})"
        )

    # --- Factory ---

    @staticmethod
    def from_message(message: telebot.types.Message) -> GameResult:
        """Create the appropriate DiceResult subclass from a message."""
        if message.dice is None:
            raise ValueError("Message does not contain a dice")

        match message.dice.emoji:
            case "🎰": return Casino(message)
            case "🎲": return Dice(message)
            case "🎯": return Darts(message)
            case "🏀": return Basketball(message)
            case "⚽": return Football(message)
            case "🎳": return Bowling(message)
            case e:
                raise ValueError(f"Unknown dice emoji: {e!r}")


# ---------------------------------------------------------------------------
# 🎲 Classic Dice
# ---------------------------------------------------------------------------

class Dice(GameResult):
    emoji = "🎲"

    @property
    def is_win(self) -> bool:
        return self.value == 6

    @property
    def score(self) -> int:
        return round((self.value / 6) * 100)


# ---------------------------------------------------------------------------
# 🎯 Darts
# ---------------------------------------------------------------------------

class Darts(GameResult):
    emoji = "🎯"

    @property
    def is_win(self) -> bool:
        return self.value == 6

    @property
    def score(self) -> int:
        return round((self.value / 6) * 100)

    @property
    def is_bullseye(self) -> bool:
        """True if the dart hit the bullseye (max value)."""
        return self.value == 6


# ---------------------------------------------------------------------------
# 🏀 Basketball
# ---------------------------------------------------------------------------

class Basketball(GameResult):
    emoji = "🏀"

    @property
    def is_win(self) -> bool:
        return self.value in {4, 5}

    @property
    def score(self) -> int:
        return round((self.value / 5) * 100)

    @property
    def is_perfect(self) -> bool:
        """True if the ball went in cleanly (value 5)."""
        return self.value == 5


# ---------------------------------------------------------------------------
# ⚽ Football
# ---------------------------------------------------------------------------

class Football(GameResult):
    emoji = "⚽"

    @property
    def is_win(self) -> bool:
        return self.value in {3, 4, 5}

    @property
    def score(self) -> int:
        return round((self.value / 5) * 100)

    @property
    def is_top_corner(self) -> bool:
        """True if the ball hit the top corner (value 5)."""
        return self.value == 5


# ---------------------------------------------------------------------------
# 🎳 Bowling
# ---------------------------------------------------------------------------

class Bowling(GameResult):
    emoji = "🎳"

    @property
    def is_win(self) -> bool:
        return self.value in {4, 5, 6}

    @property
    def score(self) -> int:
        return round((self.value / 6) * 100)

    @property
    def is_strike(self) -> bool:
        """True if all pins were knocked down."""
        return self.value == 6

    @property
    def pins_knocked(self) -> int:
        """Approximate number of pins knocked down (0-6)."""
        match self.value:
            case 1: return 0
            case 2: return 1
            case 3: return 3
            case 4: return 4
            case 5: return 5
            case 6: return 6
            case _: return 0


# ---------------------------------------------------------------------------
# 🎰 Casino
# ---------------------------------------------------------------------------

class CasinoRank:
    NOTHING   = "nothing"
    PAIR      = "pair"        # two matching symbols
    TRIPLE    = "triple"      # three matching symbols (non-7)
    DOUBLE_7  = "double_7"    # two 7s
    TRIPLE_7  = "triple_7"    # jackpot — three 7s


class Casino(GameResult):
    """
    🎰 Casino slot machine.

    Telegram encodes 3 reels in a single value (1–64).
    Each reel cycles through 4 symbols:
    >>> {1: "BAR", 2: "Cherry", 3: "Lemon", 4: "Seven"}
    >>> {1: "⬛️", 2: "🍒", 3: "🍋", 4: "7️⃣"}
    """
    emoji = "🎰"

    Rank: type[CasinoRank] = CasinoRank

    # Reel symbols in order (value 1–4 per reel)
    _REEL_SYMBOLS = {1: "⬛️", 2: "🍒", 3: "🍋", 4: "7️⃣"}
    _REEL_LETTERS = {1: "B", 2: "C", 3: "L", 4: "7"}
    _REEL_NAMES   = {1: "BAR", 2: "Cherry", 3: "Lemon", 4: "Seven"}

    _TRIPLE_NON_7 = {1, 22, 43}   # ⬛️⬛️⬛️ / 🍒🍒🍒 / 🍋🍋🍋
    _DOUBLE_7     = {16, 32, 48}  # two 7️⃣s
    _TRIPLE_7     = {64}          # 7️⃣7️⃣7️⃣

    @property
    def slots(self) -> tuple[int, int, int]:
        """Raw reel values (1–4) as (left, center, right)."""
        v = self.value - 1
        left   = v % 4 + 1
        center = (v // 4) % 4 + 1
        right  = (v // 16) % 4 + 1
        return left, center, right

    @property
    def symbols(self) -> tuple[str, str, str]:
        """Reel values as emoji symbols."""
        return tuple(self._REEL_SYMBOLS[s] for s in self.slots) # pyright: ignore[reportReturnType]
    
    @property
    def letters(self) -> str:
        """Compact reel representation as letters e.g. 'BCL'."""
        return "".join(self._REEL_LETTERS[s] for s in self.slots)

    @property
    def names(self) -> str:
        """Full reel names as a spaced string e.g. 'BAR Cherry Lemon'."""
        return " ".join(self._REEL_NAMES[s] for s in self.slots)

    @property
    def display(self) -> str:
        """Visual representation of the slot result e.g. 🍒7️⃣🍋"""
        return "".join(self.symbols)

    @property
    def rank(self) -> Literal["nothing", "pair", "triple", "double_7", "triple_7"]:
        """Categorised result rank."""
        v = self.value
        if v in self._TRIPLE_7:
            return CasinoRank.TRIPLE_7
        if v in self._DOUBLE_7:
            return CasinoRank.DOUBLE_7
        if v in self._TRIPLE_NON_7:
            return CasinoRank.TRIPLE
        left, center, right = self.slots
        if left == center or center == right or left == right:
            return CasinoRank.PAIR
        return CasinoRank.NOTHING

    @property
    def is_win(self) -> bool:
        return self.rank != CasinoRank.NOTHING

    @property
    def is_jackpot(self) -> bool:
        """`True` only for 7️⃣7️⃣7️⃣."""
        return self.rank == CasinoRank.TRIPLE_7

    @property
    def score(self) -> int:
        return {
            CasinoRank.NOTHING:  0,
            CasinoRank.PAIR:     25,
            CasinoRank.TRIPLE:   60,
            CasinoRank.DOUBLE_7: 75,
            CasinoRank.TRIPLE_7: 100,
        }[self.rank]

    def __repr__(self) -> str:
        return (
            f"Casino(value={self.value}, display={self.display}, "
            f"rank={self.rank!r}, score={self.score})"
        )