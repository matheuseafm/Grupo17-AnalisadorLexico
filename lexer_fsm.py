# Matheus Moreira - matheuseafm - Grupo 17
from __future__ import annotations

from dataclasses import dataclass

from tokens import OPERATORS, Token, TokenType


class LexerError(ValueError):
    pass


@dataclass
class _FSMContext:
    line: str
    pos: int = 0
    paren_balance: int = 0
    tokens: list[Token] | None = None

    def __post_init__(self) -> None:
        if self.tokens is None:
            self.tokens = []

    def current_char(self) -> str | None:
        if self.pos >= len(self.line):
            return None
        return self.line[self.pos]


def _state_initial(ctx: _FSMContext):
    char = ctx.current_char()
    if char is None:
        return None
    if char.isspace():
        ctx.pos += 1
        return _state_initial
    if char == "(":
        ctx.tokens.append(Token(TokenType.LPAREN, char))
        ctx.paren_balance += 1
        ctx.pos += 1
        return _state_initial
    if char == ")":
        ctx.tokens.append(Token(TokenType.RPAREN, char))
        ctx.paren_balance -= 1
        if ctx.paren_balance < 0:
            raise LexerError("Parenteses desbalanceados: ')' sem abertura.")
        ctx.pos += 1
        return _state_initial
    if char.isdigit():
        return _state_number
    if char in "+-*/%^":
        return _state_operator
    if char.isalpha():
        return _state_identifier
    raise LexerError(f"Token invalido: '{char}'.")


def _state_number(ctx: _FSMContext):
    start = ctx.pos
    has_dot = False

    while True:
        char = ctx.current_char()
        if char is None:
            break
        if char.isdigit():
            ctx.pos += 1
            continue
        if char == ".":
            if has_dot:
                raise LexerError("Numero malformado: ponto decimal duplicado.")
            has_dot = True
            ctx.pos += 1
            continue
        if char == ",":
            raise LexerError("Numero malformado: use ponto como separador decimal.")
        break

    lexeme = ctx.line[start:ctx.pos]
    if lexeme.startswith(".") or lexeme.endswith("."):
        raise LexerError(f"Numero malformado: '{lexeme}'.")
    if not lexeme:
        raise LexerError("Numero malformado.")

    token_type = TokenType.REAL if has_dot else TokenType.INT
    ctx.tokens.append(Token(token_type, lexeme))
    return _state_initial


def _state_operator(ctx: _FSMContext):
    char = ctx.current_char()
    if char is None:
        raise LexerError("Fim inesperado ao ler operador.")

    if char == "/":
        next_char = ctx.line[ctx.pos + 1] if ctx.pos + 1 < len(ctx.line) else None
        if next_char == "/":
            ctx.tokens.append(Token(TokenType.OPERATOR, "//"))
            ctx.pos += 2
            return _state_initial

    if char in "+-*/%^":
        ctx.tokens.append(Token(TokenType.OPERATOR, char))
        ctx.pos += 1
        return _state_initial

    raise LexerError(f"Operador invalido: '{char}'.")


def _state_identifier(ctx: _FSMContext):
    start = ctx.pos
    while True:
        char = ctx.current_char()
        if char is None:
            break
        if char.isalpha():
            ctx.pos += 1
            continue
        break

    lexeme = ctx.line[start:ctx.pos]
    if lexeme == "RES":
        ctx.tokens.append(Token(TokenType.RES, lexeme))
        return _state_initial

    if not lexeme.isupper():
        raise LexerError(
            f"Identificador invalido '{lexeme}': use apenas letras maiusculas."
        )

    ctx.tokens.append(Token(TokenType.IDENTIFIER, lexeme))
    return _state_initial


def _validar_tokens(tokens: list[Token]) -> None:
    for token in tokens:
        if token.token_type == TokenType.OPERATOR and token.lexeme not in OPERATORS:
            raise LexerError(f"Operador invalido: '{token.lexeme}'.")


def parse_expressao(linha: str) -> list[Token]:
    ctx = _FSMContext(linha)
    state = _state_initial

    while state is not None:
        state = state(ctx)

    if ctx.paren_balance != 0:
        raise LexerError("Parenteses desbalanceados.")

    _validar_tokens(ctx.tokens)
    return ctx.tokens


# Alias para manter nomenclatura solicitada no enunciado
parseExpressao = parse_expressao

