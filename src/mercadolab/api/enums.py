from enum import StrEnum


class Side(StrEnum):
    """Representa o lado de uma ordem, decisão ou transação no mercado."""

    BUY = "buy"
    SELL = "sell"
