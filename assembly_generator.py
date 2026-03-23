from __future__ import annotations

from dataclasses import dataclass

from tokens import Token, TokenType


@dataclass(frozen=True)
class NumberNode:
    literal: str
    is_int: bool


@dataclass(frozen=True)
class MemLoadNode:
    name: str


@dataclass(frozen=True)
class MemStoreNode:
    name: str
    value: object


@dataclass(frozen=True)
class ResNode:
    offset: int


@dataclass(frozen=True)
class BinOpNode:
    op: str
    left: object
    right: object


class _TokenCursor:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def peek(self, ahead: int = 0) -> Token | None:
        idx = self.index + ahead
        if idx >= len(self.tokens):
            return None
        return self.tokens[idx]

    def consume(self, expected: TokenType | None = None) -> Token:
        token = self.peek()
        if token is None:
            raise ValueError("Fim inesperado de tokens.")
        if expected is not None and token.token_type != expected:
            raise ValueError(f"Esperado token {expected}, encontrado {token.token_type}.")
        self.index += 1
        return token


def _parse_item(cursor: _TokenCursor):
    token = cursor.peek()
    if token is None:
        raise ValueError("Item esperado, mas fim de tokens encontrado.")
    if token.token_type == TokenType.LPAREN:
        return _parse_expr(cursor)
    if token.token_type == TokenType.REAL:
        cursor.consume(TokenType.REAL)
        return NumberNode(token.lexeme, is_int=False)
    if token.token_type == TokenType.INT:
        cursor.consume(TokenType.INT)
        return NumberNode(token.lexeme, is_int=True)
    raise ValueError(f"Item invalido no contexto: {token.lexeme}.")


def _parse_expr(cursor: _TokenCursor):
    cursor.consume(TokenType.LPAREN)

    maybe_ident = cursor.peek()
    maybe_rparen = cursor.peek(1)
    if (
        maybe_ident is not None
        and maybe_rparen is not None
        and maybe_ident.token_type == TokenType.IDENTIFIER
        and maybe_rparen.token_type == TokenType.RPAREN
    ):
        name = cursor.consume(TokenType.IDENTIFIER).lexeme
        cursor.consume(TokenType.RPAREN)
        return MemLoadNode(name)

    first = _parse_item(cursor)
    next_token = cursor.peek()
    if next_token is None:
        raise ValueError("Expressao incompleta.")

    if next_token.token_type == TokenType.RES:
        if not isinstance(first, NumberNode) or not first.is_int:
            raise ValueError("Comando RES exige inteiro nao negativo no formato (N RES).")
        offset = int(first.literal)
        if offset < 0:
            raise ValueError("Comando RES exige inteiro nao negativo.")
        cursor.consume(TokenType.RES)
        cursor.consume(TokenType.RPAREN)
        return ResNode(offset=offset)

    if next_token.token_type == TokenType.IDENTIFIER:
        mem_name = cursor.consume(TokenType.IDENTIFIER).lexeme
        cursor.consume(TokenType.RPAREN)
        return MemStoreNode(name=mem_name, value=first)

    second = _parse_item(cursor)
    op = cursor.consume(TokenType.OPERATOR).lexeme
    cursor.consume(TokenType.RPAREN)
    return BinOpNode(op=op, left=first, right=second)


def _parse_tokens(tokens: list[Token]):
    cursor = _TokenCursor(tokens)
    node = _parse_expr(cursor)
    if cursor.peek() is not None:
        raise ValueError("Tokens excedentes apos o fim da expressao.")
    return node


class AssemblyGenerator:
    def __init__(self) -> None:
        self._expr_instrs: list[list[tuple[str, str | int | None]]] = []
        self._constants: dict[str, str] = {}
        self._memories: set[str] = set()

    def _const_label(self, literal: str) -> str:
        if literal not in self._constants:
            label = f"const_{len(self._constants)}"
            self._constants[literal] = label
        return self._constants[literal]

    def _emit_node(self, node, line_index: int) -> list[tuple[str, str | int | None]]:
        if isinstance(node, NumberNode):
            return [("PUSH_CONST", self._const_label(node.literal))]

        if isinstance(node, MemLoadNode):
            self._memories.add(node.name)
            return [("LOAD_MEM", node.name)]

        if isinstance(node, ResNode):
            target = line_index - 1 - node.offset
            if target < 0:
                raise ValueError(
                    f"RES invalido: nao existe resultado para deslocamento {node.offset}."
                )
            return [("LOAD_RES", target)]

        if isinstance(node, MemStoreNode):
            self._memories.add(node.name)
            instrs = self._emit_node(node.value, line_index)
            instrs.append(("STORE_MEM", node.name))
            return instrs

        if isinstance(node, BinOpNode):
            instrs = []
            instrs.extend(self._emit_node(node.left, line_index))
            instrs.extend(self._emit_node(node.right, line_index))
            instrs.append(("BIN_OP", node.op))
            return instrs

        raise ValueError("No de AST desconhecido.")

    def adicionar_expressao(self, tokens: list[Token], numero_linha: int) -> None:
        if not tokens:
            return
        node = _parse_tokens(tokens)
        line_index = len(self._expr_instrs)
        instrs = self._emit_node(node, line_index)
        if not instrs:
            raise ValueError(f"Linha {numero_linha}: expressao vazia apos analise.")
        self._expr_instrs.append(instrs)

    def _asm_for_instruction(self, instr: tuple[str, str | int | None]) -> list[str]:
        kind, value = instr
        if kind == "PUSH_CONST":
            return [
                f"    ldr r4, ={value}",
                "    vldr d0, [r4]",
                "    bl push_d0",
            ]
        if kind == "LOAD_MEM":
            return [
                f"    ldr r4, =mem_{value}",
                "    vldr d0, [r4]",
                "    bl push_d0",
            ]
        if kind == "LOAD_RES":
            return [
                f"    ldr r4, =result_{value}",
                "    vldr d0, [r4]",
                "    bl push_d0",
            ]
        if kind == "STORE_MEM":
            return [
                "    bl pop_to_d0",
                f"    ldr r4, =mem_{value}",
                "    vstr d0, [r4]",
                "    bl push_d0",
            ]
        if kind == "BIN_OP":
            op = str(value)
            if op == "+":
                return self._binary_op(["vadd.f64 d0, d1, d0"])
            if op == "-":
                return self._binary_op(["vsub.f64 d0, d1, d0"])
            if op == "*":
                return self._binary_op(["vmul.f64 d0, d1, d0"])
            if op == "/":
                return self._binary_op(["vdiv.f64 d0, d1, d0"])
            if op == "//":
                return self._binary_op(["bl op_int_div"])
            if op == "%":
                return self._binary_op(["bl op_int_mod"])
            if op == "^":
                return self._binary_op(["bl op_pow_int"])
            raise ValueError(f"Operador nao suportado na geracao: {op}")
        raise ValueError(f"Instrucao desconhecida: {kind}")

    @staticmethod
    def _binary_op(operation_lines: list[str]) -> list[str]:
        lines = [
            "    bl pop_to_d0",
            "    bl pop_to_d1",
        ]
        lines.extend([f"    {line}" if not line.startswith("    ") else line for line in operation_lines])
        lines.append("    bl push_d0")
        return lines

    def gerar_programa(self) -> str:
        text: list[str] = []
        text.extend(
            [
                ".syntax unified",
                ".cpu cortex-a9",
                ".fpu vfpv3",
                ".global _start",
                "",
                ".text",
                "_start:",
                "    ldr r10, =eval_stack",
                "    mov r11, #0",
                "",
            ]
        )

        for idx, instrs in enumerate(self._expr_instrs):
            text.append(f"line_{idx}:")
            for instr in instrs:
                text.extend(self._asm_for_instruction(instr))
            text.extend(
                [
                    "    bl pop_to_d0",
                    f"    ldr r4, =result_{idx}",
                    "    vstr d0, [r4]",
                    "    mov r11, #0",
                    "",
                ]
            )

        text.extend(
            [
                "end_program:",
                "    b end_program",
                "",
                "push_d0:",
                "    vstr d0, [r10, r11]",
                "    add r11, r11, #8",
                "    bx lr",
                "",
                "pop_to_d0:",
                "    cmp r11, #0",
                "    beq runtime_error",
                "    sub r11, r11, #8",
                "    vldr d0, [r10, r11]",
                "    bx lr",
                "",
                "pop_to_d1:",
                "    cmp r11, #0",
                "    beq runtime_error",
                "    sub r11, r11, #8",
                "    vldr d1, [r10, r11]",
                "    bx lr",
                "",
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
                "runtime_error:",
                "    b runtime_error",
                "",
                ".data",
                "eval_stack: .space 8192",
                "const_one: .double 1.0",
            ]
        )

        for literal, label in self._constants.items():
            text.append(f"{label}: .double {literal}")

        for mem_name in sorted(self._memories):
            text.append(f"mem_{mem_name}: .double 0.0")

        for idx in range(len(self._expr_instrs)):
            text.append(f"result_{idx}: .double 0.0")

        text.append("")
        return "\n".join(text)


# Alias pedido no enunciado
gerarAssembly = AssemblyGenerator

