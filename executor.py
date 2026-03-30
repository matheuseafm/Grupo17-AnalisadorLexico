# Matheus Moreira - matheuseafm - Grupo 17
# =============================================================================
# executor.py — Avaliação de expressões RPN em Python
#
# Finalidade: servir como REFERÊNCIA para validar o Assembly gerado.
# O executor recebe a lista de tokens de parse_expressao, converte para AST
# (usando o mesmo parser do assembly_generator), e avalia recursivamente.
#
# Mantém dois estados entre chamadas sucessivas:
#   _memoria   → dicionário com variáveis de memória (IDENTIFIER → float)
#   _resultados → lista de resultados na ordem de avaliação (usado por RES)
# =============================================================================

from __future__ import annotations

# Importa os nós da AST e a função parse_tokens do assembly_generator.
# Reusar o mesmo parser garante que executor e gerador sempre interpretam
# a expressão da mesma forma (sem risco de divergência).
from assembly_generator import (
    BinOpNode,    # Nó de operação binária: (esq dir op)
    MemLoadNode,  # Nó de leitura de memória: (NOME)
    MemStoreNode, # Nó de armazenamento em memória: (valor NOME)
    NumberNode,   # Nó de literal numérico: inteiro ou real
    ResNode,      # Nó de resultado anterior: (N RES)
    parse_tokens, # Função que converte list[Token] → raiz da AST
)
from tokens import Token


# ExecutionError é lançado quando a avaliação falha em tempo de execução.
# Herda de RuntimeError para que main.py possa capturá-la com "except RuntimeError".
class ExecutionError(RuntimeError):
    pass


# =============================================================================
# ExpressionExecutor — classe que avalia expressões RPN
#
# É instanciada UMA VEZ em main.py e recebe todas as expressões sequencialmente.
# Isso é necessário porque RES precisa do histórico de expressões anteriores
# e IDENTIFIER (memória) precisa do valor armazenado em expressões anteriores.
# =============================================================================
class ExpressionExecutor:

    # __init__ inicializa o estado vazio: sem variáveis e sem histórico
    def __init__(self) -> None:
        self._memoria: dict[str, float] = {}   # Variáveis de memória: nome → valor
        self._resultados: list[float] = []      # Histórico: resultado[0], resultado[1], ...

    # Propriedade memoria: retorna CÓPIA do dicionário interno.
    # Usando cópia, código externo não consegue alterar _memoria acidentalmente.
    @property
    def memoria(self) -> dict[str, float]:
        return dict(self._memoria)

    # Propriedade resultados: retorna CÓPIA da lista interna pelo mesmo motivo.
    @property
    def resultados(self) -> list[float]:
        return list(self._resultados)

    # ==========================================================================
    # _avaliar_node — avaliação recursiva da AST
    # Recebe: node — qualquer nó da AST (NumberNode, BinOpNode, etc.)
    # Retorna: float — o valor calculado para aquele nó
    # Usa isinstance para detectar o tipo do nó e aplicar a semântica correta.
    # ==========================================================================
    def _avaliar_node(self, node: object) -> float:

        # NumberNode: literal numérico → converte a string do lexema para float
        # Ex.: NumberNode("3.14") → 3.14;  NumberNode("42") → 42.0
        if isinstance(node, NumberNode):
            return float(node.literal)

        # MemLoadNode: leitura de variável de memória → busca no dicionário _memoria
        # Se a variável não foi definida antes, lança ExecutionError
        if isinstance(node, MemLoadNode):
            if node.name not in self._memoria:
                raise ExecutionError(
                    f"Variavel de memoria '{node.name}' nao definida."
                )
            return self._memoria[node.name]

        # ResNode: resultado de uma expressão anterior pelo offset N
        # offset=0 → último resultado, offset=1 → penúltimo, etc.
        # Fórmula: idx = total_resultados - 1 - offset
        # Se idx < 0, o offset pedido é maior que o número de resultados disponíveis
        if isinstance(node, ResNode):
            idx = len(self._resultados) - 1 - node.offset
            if idx < 0:
                raise ExecutionError(
                    f"RES invalido: nao existe resultado para deslocamento {node.offset}."
                )
            return self._resultados[idx]

        # MemStoreNode: avalia a subárvore (node.value), guarda em _memoria e retorna o valor
        # Ex.: (42 TOTAL) → avalia 42, armazena _memoria["TOTAL"] = 42.0, retorna 42.0
        if isinstance(node, MemStoreNode):
            valor = self._avaliar_node(node.value)  # Avalia a subárvore recursivamente
            self._memoria[node.name] = valor         # Armazena no dicionário de memória
            return valor                             # A expressão retorna o valor armazenado

        # BinOpNode: avalia operando esquerdo, depois direito, depois aplica o operador
        # Ex.: BinOpNode("+", NumberNode("1"), NumberNode("2")) → 1.0 + 2.0 = 3.0
        if isinstance(node, BinOpNode):
            esquerda = self._avaliar_node(node.left)   # Avalia lado esquerdo da operação
            direita = self._avaliar_node(node.right)   # Avalia lado direito da operação
            return self._aplicar_operador(node.op, esquerda, direita)

        # Se chegou aqui é bug: tipo de nó desconhecido
        raise ExecutionError("No de AST desconhecido.")

    # ==========================================================================
    # _aplicar_operador — aplica o operador sobre dois operandos float
    # Recebe: op (str) — lexema do operador, a e b (float) — operandos
    # Retorna: float — resultado da operação
    # Trata divisão por zero para /, // e %.
    # @staticmethod: não usa self; pode ser chamado sem instância.
    # ==========================================================================
    @staticmethod
    def _aplicar_operador(op: str, a: float, b: float) -> float:

        if op == "+":
            return a + b  # Soma em ponto flutuante 64 bits (IEEE 754)

        if op == "-":
            return a - b  # Subtração em ponto flutuante 64 bits

        if op == "*":
            return a * b  # Multiplicação em ponto flutuante 64 bits

        if op == "/":
            if b == 0.0:
                raise ExecutionError("Divisao por zero.")
            return a / b  # Divisão real: sempre retorna float (ex.: 9/2 = 4.5)

        if op == "//":
            if b == 0.0:
                raise ExecutionError("Divisao inteira por zero.")
            # int(a) e int(b) truncam para inteiro antes de dividir
            # float() no final mantém o tipo de retorno consistente (ex.: 9//2 = 4.0)
            return float(int(a) // int(b))

        if op == "%":
            if b == 0.0:
                raise ExecutionError("Modulo por zero.")
            # Módulo inteiro: trunca ambos os operandos para int antes da operação
            return float(int(a) % int(b))

        if op == "^":
            exp = int(b)  # O expoente deve ser inteiro (converte para garantir)
            if exp < 0:
                raise ExecutionError("Expoente negativo nao suportado.")
            return a ** exp  # Potência: a elevado a exp

        # Operador não reconhecido: bug no parser se chegou aqui
        raise ExecutionError(f"Operador desconhecido: '{op}'.")

    # ==========================================================================
    # executar_expressao — método público chamado por main.py para cada linha
    # Recebe: tokens (list[Token]) — saída de parse_expressao para uma linha
    # Retorna: float — resultado calculado da expressão
    # Fluxo: tokens → AST (via parse_tokens) → avaliação recursiva → append no histórico
    # ==========================================================================
    def executar_expressao(self, tokens: list[Token]) -> float:
        if not tokens:
            raise ExecutionError("Lista de tokens vazia.")

        # parse_tokens converte a lista linear de tokens em uma árvore AST
        # (a raiz da árvore representa a expressão completa)
        node = parse_tokens(tokens)

        # _avaliar_node percorre a árvore recursivamente e calcula o resultado
        resultado = self._avaliar_node(node)

        # Armazena o resultado no histórico para que expressões futuras possam usar RES
        self._resultados.append(resultado)

        return resultado  # Também retorna para que main.py possa exibir


# Alias exigido pelo enunciado da disciplina (aponta para a CLASSE, não uma instância)
executarExpressao = ExpressionExecutor
