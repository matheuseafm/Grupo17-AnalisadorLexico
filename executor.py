# Matheus Moreira - matheuseafm - Grupo 17
from __future__ import annotations

from assembly_generator import (
    BinOpNode,
    MemLoadNode,
    MemStoreNode,
    NumberNode,
    ResNode,
    parse_tokens,
)
from tokens import Token


class ExecutionError(RuntimeError):
    pass


class ExpressionExecutor:
    """Avalia expressoes RPN usando pilha, gerencia memoria e historico de resultados."""

    def __init__(self) -> None:
        self._memoria: dict[str, float] = {}
        self._resultados: list[float] = []

    @property
    def memoria(self) -> dict[str, float]:
        return dict(self._memoria)

    @property
    def resultados(self) -> list[float]:
        return list(self._resultados)

    def _avaliar_node(self, node: object) -> float:
        if isinstance(node, NumberNode):
            return float(node.literal)

        if isinstance(node, MemLoadNode):
            if node.name not in self._memoria:
                raise ExecutionError(
                    f"Variavel de memoria '{node.name}' nao definida."
                )
            return self._memoria[node.name]

        if isinstance(node, ResNode):
            idx = len(self._resultados) - 1 - node.offset
            if idx < 0:
                raise ExecutionError(
                    f"RES invalido: nao existe resultado para deslocamento {node.offset}."
                )
            return self._resultados[idx]

        if isinstance(node, MemStoreNode):
            valor = self._avaliar_node(node.value)
            self._memoria[node.name] = valor
            return valor

        if isinstance(node, BinOpNode):
            esquerda = self._avaliar_node(node.left)
            direita = self._avaliar_node(node.right)
            return self._aplicar_operador(node.op, esquerda, direita)

        raise ExecutionError("No de AST desconhecido.")

    @staticmethod
    def _aplicar_operador(op: str, a: float, b: float) -> float:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0.0:
                raise ExecutionError("Divisao por zero.")
            return a / b
        if op == "//":
            if b == 0.0:
                raise ExecutionError("Divisao inteira por zero.")
            return float(int(a) // int(b))
        if op == "%":
            if b == 0.0:
                raise ExecutionError("Modulo por zero.")
            return float(int(a) % int(b))
        if op == "^":
            exp = int(b)
            if exp < 0:
                raise ExecutionError("Expoente negativo nao suportado.")
            return a ** exp
        raise ExecutionError(f"Operador desconhecido: '{op}'.")

    def executar_expressao(self, tokens: list[Token]) -> float:
        """Recebe tokens de parseExpressao, avalia a expressao e retorna o resultado."""
        if not tokens:
            raise ExecutionError("Lista de tokens vazia.")
        node = parse_tokens(tokens)
        resultado = self._avaliar_node(node)
        self._resultados.append(resultado)
        return resultado


executarExpressao = ExpressionExecutor
