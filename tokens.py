# Matheus Moreira - matheuseafm - Grupo 17
# Definições centrais: tipos de token, conjunto de operadores e estrutura Token.

from __future__ import annotations

from dataclasses import dataclass  # Gera __init__, __repr__, etc. para classes de dados
from enum import Enum  # Enumeração dos tipos léxicos (constantes nomeadas)


class TokenType(str, Enum):
    # Herda de str para que .value seja string e compare bem com impressão
    LPAREN = "LPAREN"  # '('
    RPAREN = "RPAREN"  # ')'
    REAL = "REAL"  # Número com ponto decimal (ex.: 3.14)
    INT = "INT"  # Inteiro sem ponto (ex.: 42)
    OPERATOR = "OPERATOR"  # + - * / // % ^
    IDENTIFIER = "IDENTIFIER"  # Nome de memória em maiúsculas (ex.: TOTAL)
    RES = "RES"  # Palavra reservada para resultado anterior


# Conjunto usado após o lexer para validar que OPERATOR só contém lexemas permitidos
OPERATORS = {"+", "-", "*", "/", "//", "%", "^"}


@dataclass(frozen=True)  # frozen=True: token imutável (hashable, seguro de compartilhar)
class Token:
    token_type: TokenType  # Qual categoria léxica
    lexeme: str  # Texto exato na entrada (ex.: "3.14", "//")
