# Matheus Moreira - matheuseafm - Grupo 17
from __future__ import annotations

import unittest

from assembly_generator import AssemblyGenerator
from lexer_fsm import parse_expressao


class CodegenTests(unittest.TestCase):
    def test_gera_assembly_com_operadores_e_comandos(self) -> None:
        linhas = [
            "(3.14 2.0 +)",
            "(9 2 //)",
            "(9 2 %)",
            "(2 3 ^)",
            "(5.0 MEM)",
            "(MEM)",
            "(0 RES)",
            "((1 2 +) (3 4 *) /)",
        ]

        gen = AssemblyGenerator()
        for i, linha in enumerate(linhas, start=1):
            gen.adicionar_expressao(parse_expressao(linha), i)

        asm = gen.gerar_programa()

        self.assertIn(".global _start", asm)
        self.assertIn("line_0:", asm)
        self.assertIn("line_7:", asm)
        self.assertIn("bl op_int_div", asm)
        self.assertIn("bl op_int_mod", asm)
        self.assertIn("bl op_pow_int", asm)
        self.assertIn("mem_MEM: .double 0.0", asm)
        self.assertIn("result_6: .double 0.0", asm)

    def test_res_invalido_lanca_erro(self) -> None:
        gen = AssemblyGenerator()
        with self.assertRaises(ValueError):
            gen.adicionar_expressao(parse_expressao("(0 RES)"), 1)


if __name__ == "__main__":
    unittest.main()

