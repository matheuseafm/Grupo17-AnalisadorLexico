# Matheus Moreira - matheuseafm - Grupo 17
# =============================================================================
# tokens.py — Vocabulário do analisador léxico
# Define os 7 tipos de token que o AFD pode reconhecer, o conjunto de
# operadores válidos e a estrutura de dados Token (tipo + texto original).
# Todos os outros módulos importam daqui.
# =============================================================================

from __future__ import annotations

# dataclass: decorator que gera automaticamente __init__, __repr__, __eq__
# para classes que só guardam dados (evita escrever boilerplate)
from dataclasses import dataclass

# Enum: cria constantes nomeadas agrupadas; herdar de str faz .value retornar string
from enum import Enum


# TokenType é um enum com 7 membros, um para cada categoria léxica possível.
# Herdar de str permite comparar tokens com strings diretamente (ex.: token == "LPAREN")
class TokenType(str, Enum):
    LPAREN = "LPAREN"      # Parêntese de abertura: o caractere '('
    RPAREN = "RPAREN"      # Parêntese de fechamento: o caractere ')'
    REAL = "REAL"          # Número com ponto decimal — ex.: 3.14, 0.5, 2.0
    INT = "INT"            # Número inteiro (sem ponto) — ex.: 3, 42, 0
    OPERATOR = "OPERATOR"  # Operador aritmético: + - * / // % ^
    IDENTIFIER = "IDENTIFIER"  # Nome de variável de memória em MAIUSCULAS — ex.: TOTAL, X
    RES = "RES"            # Palavra reservada especial: acessa resultado anterior


# Conjunto (set) dos lexemas de operadores aceitos pelo programa.
# Usado em _validar_tokens para confirmar que nenhum operador inválido passou.
# Set escolhido para busca O(1): "in OPERATORS" é mais rápido que lista.
OPERATORS = {"+", "-", "*", "/", "//", "%", "^"}


# frozen=True torna o Token imutável: após criado, não pode ser alterado.
# Vantagens: segurança (ninguém corrompe o token), hashable (pode ir em sets/dicts),
# e deixa claro que token é um valor, não um objeto com estado.
@dataclass(frozen=True)
class Token:
    token_type: TokenType  # A categoria do token (INT, REAL, OPERATOR, etc.)
    lexeme: str            # O texto exato que apareceu na entrada (ex.: "3.14", "//", "+")
