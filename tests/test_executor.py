# Matheus Moreira - matheuseafm - Grupo 17
from __future__ import annotations

import unittest

from executor import ExecutionError, ExpressionExecutor
from lexer_fsm import parse_expressao


class ExecutorOperacoesBasicasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = ExpressionExecutor()

    def test_soma_inteiros(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(3 2 +)"))
        self.assertAlmostEqual(resultado, 5.0)

    def test_soma_reais(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(3.14 2.0 +)"))
        self.assertAlmostEqual(resultado, 5.14)

    def test_subtracao(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(10 3 -)"))
        self.assertAlmostEqual(resultado, 7.0)

    def test_multiplicacao(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(4 5 *)"))
        self.assertAlmostEqual(resultado, 20.0)

    def test_divisao_real(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(10 4 /)"))
        self.assertAlmostEqual(resultado, 2.5)

    def test_divisao_inteira(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(9 2 //)"))
        self.assertAlmostEqual(resultado, 4.0)

    def test_modulo(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(9 2 %)"))
        self.assertAlmostEqual(resultado, 1.0)

    def test_potencia(self) -> None:
        resultado = self.executor.executar_expressao(parse_expressao("(2 3 ^)"))
        self.assertAlmostEqual(resultado, 8.0)

    def test_divisao_por_zero(self) -> None:
        with self.assertRaises(ExecutionError):
            self.executor.executar_expressao(parse_expressao("(5 0 /)"))

    def test_divisao_inteira_por_zero(self) -> None:
        with self.assertRaises(ExecutionError):
            self.executor.executar_expressao(parse_expressao("(5 0 //)"))

    def test_modulo_por_zero(self) -> None:
        with self.assertRaises(ExecutionError):
            self.executor.executar_expressao(parse_expressao("(5 0 %)"))


class ExecutorExpressoesAninhadasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = ExpressionExecutor()

    def test_aninhamento_simples(self) -> None:
        resultado = self.executor.executar_expressao(
            parse_expressao("((1 2 +) (3 4 *) /)")
        )
        self.assertAlmostEqual(resultado, 3.0 / 12.0)

    def test_aninhamento_duplo(self) -> None:
        resultado = self.executor.executar_expressao(
            parse_expressao("((2 3 +) ((4 1 -) 2 *) +)")
        )
        self.assertAlmostEqual(resultado, 5.0 + 6.0)

    def test_aninhamento_triplo(self) -> None:
        resultado = self.executor.executar_expressao(
            parse_expressao("(((1 2 +) (3 4 +) *) 3 -)")
        )
        self.assertAlmostEqual(resultado, (3.0 * 7.0) - 3.0)


class ExecutorMemoriaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = ExpressionExecutor()

    def test_armazenar_e_carregar_memoria(self) -> None:
        self.executor.executar_expressao(parse_expressao("(42 TOTAL)"))
        resultado = self.executor.executar_expressao(parse_expressao("(TOTAL)"))
        self.assertAlmostEqual(resultado, 42.0)

    def test_multiplas_variaveis(self) -> None:
        self.executor.executar_expressao(parse_expressao("(10 X)"))
        self.executor.executar_expressao(parse_expressao("(20 Y)"))
        resultado = self.executor.executar_expressao(
            parse_expressao("((X) (Y) +)")
        )
        self.assertAlmostEqual(resultado, 30.0)

    def test_sobrescrever_memoria(self) -> None:
        self.executor.executar_expressao(parse_expressao("(10 VAR)"))
        self.executor.executar_expressao(parse_expressao("(99 VAR)"))
        resultado = self.executor.executar_expressao(parse_expressao("(VAR)"))
        self.assertAlmostEqual(resultado, 99.0)

    def test_memoria_nao_definida(self) -> None:
        with self.assertRaises(ExecutionError):
            self.executor.executar_expressao(parse_expressao("(INEXISTENTE)"))

    def test_estado_memoria(self) -> None:
        self.executor.executar_expressao(parse_expressao("(5 A)"))
        self.executor.executar_expressao(parse_expressao("(10 B)"))
        self.assertEqual(self.executor.memoria, {"A": 5.0, "B": 10.0})


class ExecutorResTests(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = ExpressionExecutor()

    def test_res_resultado_anterior(self) -> None:
        self.executor.executar_expressao(parse_expressao("(3 2 +)"))
        resultado = self.executor.executar_expressao(parse_expressao("(0 RES)"))
        self.assertAlmostEqual(resultado, 5.0)

    def test_res_com_offset(self) -> None:
        self.executor.executar_expressao(parse_expressao("(10 5 +)"))
        self.executor.executar_expressao(parse_expressao("(3 2 *)"))
        resultado = self.executor.executar_expressao(parse_expressao("(1 RES)"))
        self.assertAlmostEqual(resultado, 15.0)

    def test_res_invalido(self) -> None:
        with self.assertRaises(ExecutionError):
            self.executor.executar_expressao(parse_expressao("(0 RES)"))

    def test_historico_resultados(self) -> None:
        self.executor.executar_expressao(parse_expressao("(1 2 +)"))
        self.executor.executar_expressao(parse_expressao("(3 4 *)"))
        self.executor.executar_expressao(parse_expressao("(5 6 -)"))
        self.assertEqual(self.executor.resultados, [3.0, 12.0, -1.0])


class ExecutorPipelineCompletoTests(unittest.TestCase):
    """Testa o fluxo completo: parseExpressao -> executarExpressao com
    sequencia de expressoes diversificadas."""

    def test_pipeline_completo(self) -> None:
        executor = ExpressionExecutor()
        expressoes = [
            ("(3.14 2.0 +)", 5.14),
            ("(9 2 //)", 4.0),
            ("(9 2 %)", 1.0),
            ("(2 3 ^)", 8.0),
            ("(5.0 VALOR)", 5.0),
            ("(VALOR)", 5.0),
            ("(0 RES)", 5.0),
            ("((1 2 +) (3 4 *) /)", 0.25),
        ]

        for expr_str, esperado in expressoes:
            tokens = parse_expressao(expr_str)
            resultado = executor.executar_expressao(tokens)
            self.assertAlmostEqual(
                resultado, esperado,
                msg=f"Falha em '{expr_str}': esperado {esperado}, obtido {resultado}",
            )

    def test_precisao_64bits(self) -> None:
        executor = ExpressionExecutor()
        resultado = executor.executar_expressao(parse_expressao("(1 3 /)"))
        self.assertAlmostEqual(resultado, 1.0 / 3.0, places=10)


if __name__ == "__main__":
    unittest.main()
