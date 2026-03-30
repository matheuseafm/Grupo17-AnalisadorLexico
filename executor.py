# Matheus Moreira - matheuseafm - Grupo 17
# Avalia a AST em Python (referência); mantém memória e histórico para RES.

from __future__ import annotations

from assembly_generator import (
    BinOpNode,
    MemLoadNode,
    MemStoreNode,
    NumberNode,
    ResNode,
    parse_tokens,  # Mesmo parser do gerador: tokens → uma raiz AST
)
from tokens import Token


class ExecutionError(RuntimeError):
    # Erros em tempo de execução (divisão por zero, memória indefinida, RES inválido)
    pass


class ExpressionExecutor:
    """Avalia expressoes RPN usando pilha, gerencia memoria e historico de resultados."""

    def __init__(self) -> None:
        self._memoria: dict[str, float] = {}  # Nome da variável → valor atual
        self._resultados: list[float] = []  # Ordem: cada expressão avaliada após a anterior

    @property
    def memoria(self) -> dict[str, float]:
        return dict(self._memoria)  # Cópia: leitura externa não altera estado interno

    @property
    def resultados(self) -> list[float]:
        return list(self._resultados)  # Cópia da lista de histórico

    def _avaliar_node(self, node: object) -> float:
        # Visita recursiva da AST; tipo de nó define a semântica
        if isinstance(node, NumberNode):
            return float(node.literal)

        if isinstance(node, MemLoadNode):
            if node.name not in self._memoria:
                raise ExecutionError(
                    f"Variavel de memoria '{node.name}' nao definida."
                )
            return self._memoria[node.name]

        if isinstance(node, ResNode):
            # offset 0 = último resultado, 1 = penúltimo, ...
            idx = len(self._resultados) - 1 - node.offset
            if idx < 0:
                raise ExecutionError(
                    f"RES invalido: nao existe resultado para deslocamento {node.offset}."
                )
            return self._resultados[idx]

        if isinstance(node, MemStoreNode):
            valor = self._avaliar_node(node.value)  # Avalia subárvore
            self._memoria[node.name] = valor
            return valor  # Valor da expressão é o valor armazenado

        if isinstance(node, BinOpNode):
            esquerda = self._avaliar_node(node.left)
            direita = self._avaliar_node(node.right)
            return self._aplicar_operador(node.op, esquerda, direita)

        raise ExecutionError("No de AST desconhecido.")

    @staticmethod
    def _aplicar_operador(op: str, a: float, b: float) -> float:
        # Ordem RPN na AST: left e right já refletem operandos na ordem correta
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
            return float(int(a) // int(b))  # Trunca para int, resultado como float
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
        node = parse_tokens(tokens)  # Uma expressão = uma raiz AST
        resultado = self._avaliar_node(node)
        self._resultados.append(resultado)  # Próximo RES usa esta lista
        return resultado


# Enunciado: nome executarExpressao — aqui aponta para a CLASSE (instanciada no main)
executarExpressao = ExpressionExecutor
