# Matheus Moreira - matheuseafm - Grupo 17
# =============================================================================
# assembly_generator.py — Parser de tokens + Gerador de código Assembly ARMv7
#
# Este módulo tem DUAS responsabilidades:
#
# 1. PARSER (tokens → AST):
#    Transforma a lista linear de tokens em uma árvore sintática abstrata (AST).
#    Usa um cursor (_TokenCursor) para percorrer os tokens um a um com peek/consume.
#    A função _parse_expr reconhece os 5 padrões da linguagem:
#      (IDENT)              → MemLoadNode  (leitura de memória)
#      (N RES)              → ResNode      (resultado anterior)
#      (valor IDENT)        → MemStoreNode (armazenamento em memória)
#      (esq dir op)         → BinOpNode    (operação binária)
#      número               → NumberNode   (literal numérico)
#
# 2. GERADOR DE CÓDIGO (AST → IR → Assembly):
#    A classe AssemblyGenerator percorre a AST e produz primeiro uma
#    Representação Intermediária (IR) — lista de tuplas como ("BIN_OP", "+") —
#    depois serializa essa IR como strings Assembly ARMv7 (arquivo .s).
# =============================================================================

from __future__ import annotations

# dataclass gera __init__, __repr__ e __eq__ automáticos para os nós da AST
from dataclasses import dataclass

from tokens import Token, TokenType


# =============================================================================
# NÓS DA AST — cada classe representa um padrão sintático da linguagem
# frozen=True torna o nó imutável (hashable, seguro de compartilhar)
# =============================================================================

# NumberNode: representa um literal numérico na expressão
# Ex.: token INT "42" → NumberNode("42", is_int=True)
# Ex.: token REAL "3.14" → NumberNode("3.14", is_int=False)
@dataclass(frozen=True)
class NumberNode:
    literal: str   # Texto exato do número (ex.: "42", "3.14")
    is_int: bool   # True se é inteiro (exigido para validar (N RES) onde N precisa ser int)


# MemLoadNode: representa a leitura de uma variável de memória
# Ex.: expressão (TOTAL) → MemLoadNode("TOTAL")
@dataclass(frozen=True)
class MemLoadNode:
    name: str  # Nome da variável de memória (sempre maiúsculas)


# MemStoreNode: representa o armazenamento de um valor em uma variável de memória
# Ex.: expressão (42 TOTAL) → MemStoreNode("TOTAL", NumberNode("42", True))
@dataclass(frozen=True)
class MemStoreNode:
    name: str      # Nome da variável de memória onde o valor será armazenado
    value: object  # Subárvore que representa o valor a armazenar (pode ser qualquer nó)


# ResNode: representa o acesso ao resultado de uma expressão anterior
# Ex.: expressão (0 RES) → ResNode(offset=0) — offset 0 = último resultado
# Ex.: expressão (1 RES) → ResNode(offset=1) — offset 1 = penúltimo resultado
@dataclass(frozen=True)
class ResNode:
    offset: int  # Número de posições para voltar no histórico de resultados


# BinOpNode: representa uma operação aritmética binária entre dois operandos
# Ex.: expressão (1 2 +) → BinOpNode("+", NumberNode("1"), NumberNode("2"))
@dataclass(frozen=True)
class BinOpNode:
    op: str        # Lexema do operador: "+", "-", "*", "/", "//", "%", "^"
    left: object   # Nó do operando esquerdo (pode ser qualquer nó, inclusive aninhado)
    right: object  # Nó do operando direito (pode ser qualquer nó, inclusive aninhado)


# =============================================================================
# _TokenCursor — cursor para percorrer a lista de tokens no parser
# Fornece dois métodos principais:
#   peek(ahead)       → olha o token em index+ahead SEM avançar o cursor
#   consume(expected) → retorna e CONSOME o próximo token, validando o tipo
# =============================================================================
class _TokenCursor:

    # Inicializa o cursor com a lista de tokens e o índice em 0 (início)
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0  # Índice do próximo token a ser consumido

    # peek olha tokens futuros sem avançar o cursor.
    # ahead=0 → próximo token, ahead=1 → token depois do próximo, etc.
    # Retorna None se o índice ultrapassar o fim da lista (lookahead seguro).
    def peek(self, ahead: int = 0) -> Token | None:
        idx = self.index + ahead
        if idx >= len(self.tokens):
            return None  # Não há token nessa posição
        return self.tokens[idx]

    # consume retorna o próximo token E avança o cursor (índice += 1).
    # Se expected não for None, valida que o token tem o tipo esperado.
    # Lança ValueError se a lista acabou ou o tipo não bate.
    def consume(self, expected: TokenType | None = None) -> Token:
        token = self.peek()
        if token is None:
            raise ValueError("Fim inesperado de tokens.")
        if expected is not None and token.token_type != expected:
            raise ValueError(f"Esperado token {expected}, encontrado {token.token_type}.")
        self.index += 1
        return token


# =============================================================================
# _parse_item — tenta reconhecer um OPERANDO (número ou subexpressão)
# Recebe: cursor posicionado no primeiro token do operando
# Retorna: NumberNode (se for INT ou REAL) ou chama _parse_expr (se for LPAREN)
# Lança ValueError se não for nenhum dos tipos esperados
# =============================================================================
def _parse_item(cursor: _TokenCursor):
    token = cursor.peek()  # Olha o próximo token sem consumir ainda

    if token is None:
        raise ValueError("Item esperado, mas fim de tokens encontrado.")

    # LPAREN: o operando é uma subexpressão aninhada — chama _parse_expr recursivamente
    # Ex.: em ((1 2 +) (3 4 *) /), o "item" (1 2 +) é uma subexpressão
    if token.token_type == TokenType.LPAREN:
        return _parse_expr(cursor)  # Recursão: analisa a subexpressão completa

    # REAL: literal com ponto decimal → NumberNode com is_int=False
    if token.token_type == TokenType.REAL:
        cursor.consume(TokenType.REAL)  # Consome o token REAL
        return NumberNode(token.lexeme, is_int=False)

    # INT: literal inteiro → NumberNode com is_int=True
    if token.token_type == TokenType.INT:
        cursor.consume(TokenType.INT)   # Consome o token INT
        return NumberNode(token.lexeme, is_int=True)

    # Qualquer outro token neste contexto é erro de sintaxe
    raise ValueError(f"Item invalido no contexto: {token.lexeme}.")


# =============================================================================
# _parse_expr — reconhece uma expressão completa entre parênteses
# Gramática:
#   expr → '(' IDENT ')'               # Leitura de memória: (TOTAL)
#        | '(' INT 'RES' ')'           # Resultado anterior: (0 RES)
#        | '(' item IDENT ')'          # Armazenamento: (42 TOTAL)
#        | '(' item item OPERATOR ')'  # Operação binária: (1 2 +)
#
# Usa LOOKAHEAD para decidir qual caso:
#   peek(0)==IDENT e peek(1)==RPAREN → é leitura de memória
#   após primeiro item, peek()==RES  → é ResNode
#   após primeiro item, peek()==IDENT → é MemStoreNode
#   caso contrário → é BinOpNode
# =============================================================================
def _parse_expr(cursor: _TokenCursor):
    # Toda expressão começa com '(' — consome e valida
    cursor.consume(TokenType.LPAREN)

    # LOOKAHEAD de 2 tokens para detectar leitura de memória: ( IDENT )
    # peek(0) = token logo após o '(', peek(1) = token depois
    maybe_ident = cursor.peek()
    maybe_rparen = cursor.peek(1)
    if (
        maybe_ident is not None
        and maybe_rparen is not None
        and maybe_ident.token_type == TokenType.IDENTIFIER
        and maybe_rparen.token_type == TokenType.RPAREN
    ):
        # É leitura de memória: (TOTAL) → MemLoadNode("TOTAL")
        name = cursor.consume(TokenType.IDENTIFIER).lexeme  # Consome o nome
        cursor.consume(TokenType.RPAREN)                     # Consome o ')'
        return MemLoadNode(name)

    # Analisa o primeiro item (número ou subexpressão aninhada)
    first = _parse_item(cursor)

    # Olha o token seguinte sem consumir para decidir qual padrão é este
    next_token = cursor.peek()
    if next_token is None:
        raise ValueError("Expressao incompleta.")

    # Padrão: ( N RES ) — acessa resultado anterior pelo offset N
    if next_token.token_type == TokenType.RES:
        # Valida que o primeiro item é um inteiro não negativo (ex.: 0 ou 1, não 3.14)
        if not isinstance(first, NumberNode) or not first.is_int:
            raise ValueError("Comando RES exige inteiro nao negativo no formato (N RES).")
        offset = int(first.literal)
        if offset < 0:
            raise ValueError("Comando RES exige inteiro nao negativo.")
        cursor.consume(TokenType.RES)    # Consome a palavra RES
        cursor.consume(TokenType.RPAREN) # Consome o ')'
        return ResNode(offset=offset)

    # Padrão: ( valor IDENT ) — armazenamento em memória
    # Ex.: (42 TOTAL) → armazena 42 na variável TOTAL
    if next_token.token_type == TokenType.IDENTIFIER:
        mem_name = cursor.consume(TokenType.IDENTIFIER).lexeme  # Consome o nome da variável
        cursor.consume(TokenType.RPAREN)                         # Consome o ')'
        return MemStoreNode(name=mem_name, value=first)          # Cria nó de armazenamento

    # Padrão: ( esq dir op ) — operação binária
    # Ex.: (1 2 +), ((1 2 +) 3 *)
    second = _parse_item(cursor)                      # Analisa o segundo operando
    op = cursor.consume(TokenType.OPERATOR).lexeme    # Consome o operador
    cursor.consume(TokenType.RPAREN)                  # Consome o ')'
    return BinOpNode(op=op, left=first, right=second) # Cria nó de operação binária


# =============================================================================
# _parse_tokens — ponto de entrada do parser
# Recebe a lista completa de tokens de UMA linha e retorna a raiz da AST.
# Valida que após a expressão não sobrou nenhum token (linha completa parseada).
# =============================================================================
def _parse_tokens(tokens: list[Token]):
    cursor = _TokenCursor(tokens)  # Cria cursor no início da lista

    # Analisa a expressão completa (deve cobrir todos os tokens)
    node = _parse_expr(cursor)

    # Se ainda houver tokens, a linha contém mais de uma expressão (erro de sintaxe)
    if cursor.peek() is not None:
        raise ValueError("Tokens excedentes apos o fim da expressao.")

    return node  # Retorna a raiz da AST representando a expressão completa


# =============================================================================
# AssemblyGenerator — converte AST em código Assembly ARMv7
#
# Processo em 2 fases:
#   Fase 1 (adicionar_expressao): tokens → AST → IR (lista de tuplas)
#   Fase 2 (gerar_programa): IR → texto Assembly completo
#
# A IR desacopla a análise semântica da geração de código.
# Exemplo de IR para (1 2 +):
#   [("PUSH_CONST", "const_0"), ("PUSH_CONST", "const_1"), ("BIN_OP", "+")]
#
# Registradores usados no Assembly gerado:
#   r10 — base da pilha de avaliação (eval_stack)
#   r11 — offset do topo da pilha (bytes desde r10; double = 8 bytes)
#   r4  — temporário para endereços de memória
#   d0  — registrador FP (operando atual / resultado)
#   d1  — segundo operando FP para operações binárias
#   r0, r1 — operandos inteiros para divisão e módulo
# =============================================================================
class AssemblyGenerator:

    def __init__(self) -> None:
        # Lista de listas: _expr_instrs[i] = lista de tuplas IR da expressão i
        self._expr_instrs: list[list[tuple[str, str | int | None]]] = []

        # Mapa de literal numérico → rótulo .data (deduplicação)
        # Ex.: se "3.14" aparece em 3 expressões, ainda usa um único const_0
        self._constants: dict[str, str] = {}

        # Conjunto de variáveis de memória referenciadas no programa
        # Cada uma precisa de uma entrada "mem_NOME: .double 0.0" na seção .data
        self._memories: set[str] = set()

    # _const_label registra um literal numérico e retorna seu rótulo no .data.
    # Se o literal já foi visto antes, reutiliza o rótulo existente.
    # Se é novo, cria const_0, const_1, const_2, etc.
    def _const_label(self, literal: str) -> str:
        if literal not in self._constants:
            label = f"const_{len(self._constants)}"  # Gera próximo rótulo sequencial
            self._constants[literal] = label          # Registra no mapa
        return self._constants[literal]

    # ==========================================================================
    # _emit_node — percorre a AST recursivamente e gera a lista de instruções IR
    # Recebe: node — qualquer nó da AST, line_index — índice da expressão atual (para RES)
    # Retorna: list de tuplas IR
    # Ordem pós-fixada (post-order): operandos primeiro, operação depois
    # ==========================================================================
    def _emit_node(self, node, line_index: int) -> list[tuple[str, str | int | None]]:

        # Número: empilha a constante numérica na pilha de avaliação
        if isinstance(node, NumberNode):
            return [("PUSH_CONST", self._const_label(node.literal))]

        # Leitura de memória: carrega o valor da variável e empilha
        if isinstance(node, MemLoadNode):
            self._memories.add(node.name)  # Garante que mem_NOME aparece no .data
            return [("LOAD_MEM", node.name)]

        # Resultado anterior: calcula o índice absoluto da linha alvo e carrega
        if isinstance(node, ResNode):
            # line_index é o índice da expressão ATUAL (0-based)
            # Para offset=0: queremos line_index-1 (expressão imediatamente anterior)
            target = line_index - 1 - node.offset
            if target < 0:
                raise ValueError(
                    f"RES invalido: nao existe resultado para deslocamento {node.offset}."
                )
            return [("LOAD_RES", target)]  # target é o índice do result_N no .data

        # Armazenamento em memória: emite IR do valor + instrução de armazenamento
        if isinstance(node, MemStoreNode):
            self._memories.add(node.name)                   # Registra a variável
            instrs = self._emit_node(node.value, line_index) # Emite o valor
            instrs.append(("STORE_MEM", node.name))          # Depois armazena
            return instrs

        # Operação binária: emite esquerda, depois direita, depois a operação
        # A ordem garante que quando BIN_OP executar, topo=direita e abaixo=esquerda
        if isinstance(node, BinOpNode):
            instrs = []
            instrs.extend(self._emit_node(node.left, line_index))   # Empilha esquerda
            instrs.extend(self._emit_node(node.right, line_index))  # Empilha direita
            instrs.append(("BIN_OP", node.op))                       # Executa operação
            return instrs

        # Tipo de nó não reconhecido: bug interno
        raise ValueError("No de AST desconhecido.")

    # ==========================================================================
    # adicionar_expressao — ponto de entrada chamado por main.py para cada linha
    # Recebe: tokens (list[Token]), numero_linha (int — para mensagens de erro)
    # Converte tokens → AST → IR e acumula em _expr_instrs
    # ==========================================================================
    def adicionar_expressao(self, tokens: list[Token], numero_linha: int) -> None:
        if not tokens:
            return  # Linha vazia: ignorar silenciosamente

        # Converte tokens em AST via parser
        node = _parse_tokens(tokens)

        # line_index é a posição desta expressão no programa (0 = primeira, 1 = segunda, etc.)
        line_index = len(self._expr_instrs)

        # Percorre a AST e gera a lista de instruções IR
        instrs = self._emit_node(node, line_index)

        if not instrs:
            raise ValueError(f"Linha {numero_linha}: expressao vazia apos analise.")

        # Acumula as instruções desta linha
        self._expr_instrs.append(instrs)

    # ==========================================================================
    # _asm_for_instruction — traduz UMA tupla IR em linhas de Assembly
    # Recebe: instr — tupla como ("PUSH_CONST", "const_0") ou ("BIN_OP", "+")
    # Retorna: list[str] — linhas Assembly indentadas com 4 espaços
    # ==========================================================================
    def _asm_for_instruction(self, instr: tuple[str, str | int | None]) -> list[str]:
        kind, value = instr

        # PUSH_CONST: carrega o endereço da constante, lê o double e empilha
        if kind == "PUSH_CONST":
            return [
                f"    ldr r4, ={value}",    # r4 = endereço da constante no .data
                "    vldr d0, [r4]",         # d0 = valor double na memória apontada por r4
                "    bl push_d0",            # empilha d0 na pilha de avaliação
            ]

        # LOAD_MEM: lê variável de memória e empilha
        if kind == "LOAD_MEM":
            return [
                f"    ldr r4, =mem_{value}", # r4 = endereço da variável no .data
                "    vldr d0, [r4]",          # d0 = valor atual da variável
                "    bl push_d0",             # empilha d0
            ]

        # LOAD_RES: lê resultado de expressão anterior e empilha
        if kind == "LOAD_RES":
            return [
                f"    ldr r4, =result_{value}", # r4 = endereço do result_N no .data
                "    vldr d0, [r4]",              # d0 = resultado salvo
                "    bl push_d0",                 # empilha d0
            ]

        # STORE_MEM: desempilha o valor calculado e armazena na variável de memória
        # Após armazenar, PUSH de volta para manter o valor no topo (o armazenamento
        # também é o "resultado" desta expressão)
        if kind == "STORE_MEM":
            return [
                "    bl pop_to_d0",              # desempilha o valor para d0
                f"    ldr r4, =mem_{value}",     # r4 = endereço da variável
                "    vstr d0, [r4]",              # armazena d0 na variável
                "    bl push_d0",                 # empilha de volta (valor é o resultado)
            ]

        # BIN_OP: operação binária — desempilha dois operandos, opera, empilha resultado
        if kind == "BIN_OP":
            op = str(value)
            if op == "+":
                return self._binary_op(["vadd.f64 d0, d1, d0"])  # d0 = d1 + d0 (FP 64 bits)
            if op == "-":
                return self._binary_op(["vsub.f64 d0, d1, d0"])  # d0 = d1 - d0 (FP 64 bits)
            if op == "*":
                return self._binary_op(["vmul.f64 d0, d1, d0"])  # d0 = d1 * d0 (FP 64 bits)
            if op == "/":
                return self._binary_op(["vdiv.f64 d0, d1, d0"])  # d0 = d1 / d0 (FP 64 bits)
            if op == "//":
                # Divisão inteira: rotina op_int_div converte para int e divide por subtração
                return self._binary_op(["bl op_int_div"])
            if op == "%":
                # Módulo: rotina op_int_mod converte para int e calcula resto por subtração
                return self._binary_op(["bl op_int_mod"])
            if op == "^":
                # Potência: rotina op_pow_int faz multiplicação iterativa
                return self._binary_op(["bl op_pow_int"])
            raise ValueError(f"Operador nao suportado na geracao: {op}")

        raise ValueError(f"Instrucao desconhecida: {kind}")

    # _binary_op monta o padrão padrão para toda operação binária:
    #   1. Desempilha d0 (segundo operando — topo da pilha)
    #   2. Desempilha d1 (primeiro operando — abaixo do topo)
    #   3. Executa a operação (passada como parâmetro)
    #   4. Empilha o resultado (sempre em d0)
    @staticmethod
    def _binary_op(operation_lines: list[str]) -> list[str]:
        lines = [
            "    bl pop_to_d0",  # d0 = operando direito (topo)
            "    bl pop_to_d1",  # d1 = operando esquerdo (abaixo do topo)
        ]
        # Garante que as linhas da operação têm a indentação correta
        lines.extend([f"    {line}" if not line.startswith("    ") else line for line in operation_lines])
        lines.append("    bl push_d0")  # empilha o resultado que ficou em d0
        return lines

    # ==========================================================================
    # gerar_programa — serializa todo o Assembly em uma única string
    # Retorna: str — conteúdo completo do arquivo .s pronto para gravar no disco
    #
    # Estrutura do arquivo gerado:
    #   1. Diretivas de montagem (.syntax, .cpu, .fpu)
    #   2. Seção .text com _start (inicializa r10 e r11)
    #   3. Bloco line_N: para cada expressão (IR traduzida para Assembly)
    #   4. Rótulo end_program (loop infinito — fim normal do programa)
    #   5. Sub-rotinas de pilha: push_d0, pop_to_d0, pop_to_d1
    #   6. Sub-rotinas de operação: op_int_div, op_int_mod, op_pow_int
    #   7. Rotinas de divisão/módulo inteiro: int_divide_signed, int_mod_signed
    #   8. runtime_error (loop infinito — chamado em divisão por zero ou stack vazio)
    #   9. Seção .data: eval_stack, const_one, constantes, variáveis, resultados
    # ==========================================================================
    def gerar_programa(self) -> str:
        text: list[str] = []

        # Diretivas de configuração do montador (GNU assembler)
        # .syntax unified: aceita tanto ARM quanto Thumb em um mesmo arquivo
        # .cpu cortex-a9: o modelo de CPU do CPULATOR (ARMv7-A)
        # .fpu vfpv3: unidade de ponto flutuante VFPv3 (suporta doubles)
        # .global _start: torna _start visível para o linker (ponto de entrada)
        text.extend(
            [
                ".syntax unified",
                ".cpu cortex-a9",
                ".fpu vfpv3",
                ".global _start",
                "",
                ".text",
                "_start:",
                "    ldr r10, =eval_stack",  # r10 = endereço base da pilha de avaliação
                "    mov r11, #0",            # r11 = 0 (pilha vazia; cresce para cima em bytes)
                "",
            ]
        )

        # Emite um bloco Assembly para cada expressão acumulada
        for idx, instrs in enumerate(self._expr_instrs):
            text.append(f"line_{idx}:")  # Rótulo da linha (line_0, line_1, ...)

            # Traduz cada instrução IR para linhas Assembly
            for instr in instrs:
                text.extend(self._asm_for_instruction(instr))

            # Ao fim de cada expressão: desempilha o resultado final e salva em result_N
            # reset r11=0 limpa a pilha para a próxima expressão
            text.extend(
                [
                    "    bl pop_to_d0",           # Desempilha o resultado final para d0
                    f"    ldr r4, =result_{idx}", # r4 = endereço de result_N no .data
                    "    vstr d0, [r4]",           # Armazena d0 em result_N
                    "    mov r11, #0",             # Zera o offset (pilha vazia para próxima linha)
                    "",
                ]
            )

        # Sub-rotinas e seção de dados (sempre iguais; só o .data varia por programa)
        text.extend(
            [
                # Fim do programa: loop infinito (o simulador para quando detecta isso)
                "end_program:",
                "    b end_program",
                "",

                # push_d0: empilha d0 na pilha de avaliação
                # vstr armazena d0 em mem[r10 + r11]; depois incrementa r11 em 8 (tamanho double)
                "push_d0:",
                "    vstr d0, [r10, r11]",
                "    add r11, r11, #8",
                "    bx lr",
                "",

                # pop_to_d0: desempilha o topo da pilha para d0
                # Verifica se a pilha não está vazia (r11 > 0); decrementa r11 e carrega d0
                "pop_to_d0:",
                "    cmp r11, #0",
                "    beq runtime_error",
                "    sub r11, r11, #8",
                "    vldr d0, [r10, r11]",
                "    bx lr",
                "",

                # pop_to_d1: igual ao pop_to_d0 mas carrega em d1 (segundo operando)
                "pop_to_d1:",
                "    cmp r11, #0",
                "    beq runtime_error",
                "    sub r11, r11, #8",
                "    vldr d1, [r10, r11]",
                "    bx lr",
                "",

                # op_int_div: divisão inteira // em ponto flutuante
                # Converte d1 e d0 para inteiros (s2, s3 → r0, r1), chama int_divide_signed,
                # converte o resultado inteiro de volta para double em d0
                "op_int_div:",
                "    vcvt.s32.f64 s2, d1",
                "    vcvt.s32.f64 s3, d0",
                "    vmov r0, s2",
                "    vmov r1, s3",
                "    bl int_divide_signed",
                "    vmov s0, r0",
                "    vcvt.f64.s32 d0, s0",
                "    bx lr",
                "",

                # op_int_mod: módulo % em ponto flutuante (mesma lógica de op_int_div)
                "op_int_mod:",
                "    vcvt.s32.f64 s2, d1",
                "    vcvt.s32.f64 s3, d0",
                "    vmov r0, s2",
                "    vmov r1, s3",
                "    bl int_mod_signed",
                "    vmov s0, r0",
                "    vcvt.f64.s32 d0, s0",
                "    bx lr",
                "",

                # op_pow_int: potência ^ com expoente inteiro
                # Converte d0 (expoente) para int em r0, inicializa resultado=1.0,
                # e faz multiplicação iterativa: d0 *= d2 (base) por r0 vezes
                "op_pow_int:",
                "    vcvt.s32.f64 s1, d0",
                "    vmov r0, s1",
                "    cmp r0, #0",
                "    blt runtime_error",
                "    ldr r4, =const_one",
                "    vldr d0, [r4]",
                "    vmov.f64 d2, d1",
                "pow_loop:",
                "    cmp r0, #0",
                "    beq pow_done",
                "    vmul.f64 d0, d0, d2",
                "    sub r0, r0, #1",
                "    b pow_loop",
                "pow_done:",
                "    bx lr",
                "",

                # int_divide_signed: divisão inteira com sinal por subtração sucessiva
                # ARMv7 Cortex-A9 não tem instrução SDIV nativa no modo usado pelo CPULATOR.
                # Algoritmo: abs(a) // abs(b) por subtrações repetidas; aplica sinal ao final.
                # r2 = flag de sinal (XOR dos sinais de a e b)
                "int_divide_signed:",
                "    cmp r1, #0",
                "    beq runtime_error",
                "    mov r2, #0",
                "    cmp r0, #0",
                "    bge div_a_ok",
                "    rsb r0, r0, #0",
                "    eor r2, r2, #1",
                "div_a_ok:",
                "    cmp r1, #0",
                "    bge div_b_ok",
                "    rsb r1, r1, #0",
                "    eor r2, r2, #1",
                "div_b_ok:",
                "    mov r3, #0",
                "div_loop:",
                "    cmp r0, r1",
                "    blt div_done",
                "    sub r0, r0, r1",
                "    add r3, r3, #1",
                "    b div_loop",
                "div_done:",
                "    mov r0, r3",
                "    cmp r2, #0",
                "    beq div_exit",
                "    rsb r0, r0, #0",
                "div_exit:",
                "    bx lr",
                "",

                # int_mod_signed: módulo inteiro com sinal por subtração sucessiva
                # Mesma lógica de int_divide_signed, mas retorna o restante
                "int_mod_signed:",
                "    cmp r1, #0",
                "    beq runtime_error",
                "    mov r2, #0",
                "    cmp r0, #0",
                "    bge mod_a_ok",
                "    rsb r0, r0, #0",
                "    mov r2, #1",
                "mod_a_ok:",
                "    cmp r1, #0",
                "    bge mod_b_ok",
                "    rsb r1, r1, #0",
                "mod_b_ok:",
                "mod_loop:",
                "    cmp r0, r1",
                "    blt mod_done",
                "    sub r0, r0, r1",
                "    b mod_loop",
                "mod_done:",
                "    cmp r2, #0",
                "    beq mod_exit",
                "    rsb r0, r0, #0",
                "mod_exit:",
                "    bx lr",
                "",

                # runtime_error: loop infinito que sinaliza erro em tempo de execução
                # (divisão por zero, pilha vazia, expoente negativo)
                "runtime_error:",
                "    b runtime_error",
                "",

                # Seção .data: variáveis e constantes do programa
                ".data",
                # eval_stack: 8192 bytes = 1024 doubles (espaço para a pilha de avaliação)
                "eval_stack: .space 8192",
                # const_one: 1.0 usada como valor inicial do acumulador em op_pow_int
                "const_one: .double 1.0",
            ]
        )

        # Gera uma entrada .data para cada constante numérica usada nas expressões
        # Ex.: se o programa usa 3.14, gera "const_0: .double 3.14"
        for literal, label in self._constants.items():
            text.append(f"{label}: .double {literal}")

        # Gera uma entrada .data para cada variável de memória usada no programa
        # Inicializada com 0.0 (default antes de qualquer armazenamento)
        for mem_name in sorted(self._memories):
            text.append(f"mem_{mem_name}: .double 0.0")

        # Gera uma entrada .data para armazenar o resultado de cada expressão
        # Cada linha tem seu próprio result_N para que RES possa referenciar qualquer delas
        for idx in range(len(self._expr_instrs)):
            text.append(f"result_{idx}: .double 0.0")

        text.append("")  # Linha vazia final (boa prática em arquivos Assembly)
        return "\n".join(text)  # Junta todas as linhas em uma única string


# Alias público: parse_tokens é usado por executor.py para reutilizar o mesmo parser
parse_tokens = _parse_tokens

# Alias exigido pelo enunciado da disciplina (nome camelCase para a classe do gerador)
gerarAssembly = AssemblyGenerator
