# Matheus Moreira - matheuseafm - Grupo 17
from __future__ import annotations

import unittest

from lexer_fsm import LexerError, parse_expressao
from tokens import TokenType


class LexerFSMTests(unittest.TestCase):
    def test_entrada_valida_tokens_basicos(self) -> None:
        tokens = parse_expressao("(3.14 2.0 +)")
        lexemas = [t.lexeme for t in tokens]
        tipos = [t.token_type for t in tokens]

        self.assertEqual(lexemas, ["(", "3.14", "2.0", "+", ")"])
        self.assertEqual(
            tipos,
            [
                TokenType.LPAREN,
                TokenType.REAL,
                TokenType.REAL,
                TokenType.OPERATOR,
                TokenType.RPAREN,
            ],
        )

    def test_entrada_valida_comandos_especiais(self) -> None:
        tokens_res = parse_expressao("(5 RES)")
        tokens_mem_store = parse_expressao("(10.5 MEM)")
        tokens_mem_load = parse_expressao("(MEM)")

        self.assertEqual([t.lexeme for t in tokens_res], ["(", "5", "RES", ")"])
        self.assertEqual([t.lexeme for t in tokens_mem_store], ["(", "10.5", "MEM", ")"])
        self.assertEqual([t.lexeme for t in tokens_mem_load], ["(", "MEM", ")"])

    def test_numero_malformado(self) -> None:
        with self.assertRaises(LexerError):
            parse_expressao("(3.14.5 2 +)")

        with self.assertRaises(LexerError):
            parse_expressao("(3,45 2 +)")

    def test_operador_invalido(self) -> None:
        with self.assertRaises(LexerError):
            parse_expressao("(3.14 2.0 &)")

    def test_parenteses_desbalanceados(self) -> None:
        with self.assertRaises(LexerError):
            parse_expressao("((3 2 +)")


if __name__ == "__main__":
    unittest.main()

