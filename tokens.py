# Matheus Moreira - matheuseafm - Grupo 17
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(str, Enum):
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    REAL = "REAL"
    INT = "INT"
    OPERATOR = "OPERATOR"
    IDENTIFIER = "IDENTIFIER"
    RES = "RES"


OPERATORS = {"+", "-", "*", "/", "//", "%", "^"}


@dataclass(frozen=True)
class Token:
    token_type: TokenType
    lexeme: str

