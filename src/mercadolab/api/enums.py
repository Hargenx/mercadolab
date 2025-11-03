from enum import StrEnum


class Side(StrEnum):
    """BUY | SELL - tipo da UML para lado da transacao e decisao do investidor."""

    BUY = "buy"
    SELL = "sell"
