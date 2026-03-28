# Grupo 17 — Analisador Léxico RPN

## Informações Acadêmicas

| Campo | Detalhe |
|---|---|
| **Instituição** | PUCPR — Pontifícia Universidade Católica do Paraná |
| **Disciplina** | Construção de Interpretadores |
| **Professor** | Frank Alcantara |

### Alunos

| Nome | GitHub |
|---|---|
| Matheus Moreira | [@matheuseafm](https://github.com/matheuseafm) |

---

## Descrição do Projeto

Projeto da **Fase 1** da disciplina. O programa lê expressões em **notação polonesa reversa (RPN)** a partir de um arquivo de texto, realiza **análise léxica** por meio de um **Autômato Finito Determinístico (AFD)** — com estados implementados como funções — e gera código **Assembly ARMv7** compatível com o alvo **DEC1-SOC** (simulador CPULATOR).

### Requisitos atendidos

- Análise léxica **sem uso de regex**.
- AFD determinístico com estados em funções (`lexer_fsm.py`).
- Reconhecimento de:
  - parênteses `(` e `)`;
  - números inteiros e reais com ponto decimal;
  - operadores `+ - * / // % ^`;
  - comandos especiais `RES` e identificadores de memória em letras maiúsculas.
- Geração de Assembly ARMv7 (`assembly_generator.py`).
- Leitura de arquivo de entrada por argumento de linha de comando.
- Três arquivos de teste (`teste1.txt`, `teste2.txt`, `teste3.txt`) com 10+ linhas cada.

---

## Pré-requisitos

- **Python 3.10** ou superior.
- Nenhuma dependência externa é necessária; o projeto utiliza apenas a biblioteca padrão do Python.

---

## Estrutura do Projeto

```
Grupo17-AnalisadorLexico/
├── main.py                  # Ponto de entrada do programa
├── io_utils.py              # Leitura e escrita de arquivos
├── tokens.py                # Definição dos tipos de token
├── lexer_fsm.py             # Analisador léxico (AFD com funções de estado)
├── assembly_generator.py    # Parser estrutural mínimo + gerador Assembly ARMv7
├── tests/
│   ├── test_lexer.py        # Testes unitários do lexer
│   └── test_codegen.py      # Testes unitários do gerador de código
├── teste1.txt               # Arquivo de teste 1 (entrada)
├── teste2.txt               # Arquivo de teste 2 (entrada)
├── teste3.txt               # Arquivo de teste 3 (entrada)
└── README.md
```

---

## Formato da Linguagem de Entrada

Cada linha do arquivo de entrada contém uma expressão RPN:

| Construção | Sintaxe | Exemplo |
|---|---|---|
| Operação binária | `(A B op)` | `(1 2 +)` |
| Resultado anterior | `(N RES)` | `(0 RES)` |
| Armazenamento em memória | `(V MEM)` | `(42 TOTAL)` |
| Leitura de memória | `(MEM)` | `(TOTAL)` |
| Aninhamento | parênteses internos | `((1 2 +) (3 4 *) /)` |

Operadores suportados: `+`, `-`, `*`, `/`, `//`, `%`, `^`

---

## Como Compilar e Executar

> O projeto é inteiramente em Python e **não requer compilação**. Basta executar diretamente com o interpretador Python.

### Execução básica

Gere o Assembly a partir de um arquivo de entrada. O arquivo `.s` de saída terá o mesmo nome-base da entrada:

```bash
python main.py teste1.txt
```

Isso gera o arquivo `teste1.s`.

### Especificando o arquivo de saída

```bash
python main.py teste1.txt saida.s
```

### Uso geral

```
python main.py <arquivo_entrada.txt> [arquivo_saida.s]
```

| Argumento | Obrigatório | Descrição |
|---|---|---|
| `<arquivo_entrada.txt>` | Sim | Caminho do arquivo com as expressões RPN |
| `[arquivo_saida.s]` | Não | Caminho do arquivo Assembly de saída (padrão: `<nome_entrada>.s`) |

---

## Como Rodar os Testes

Os testes unitários utilizam o módulo `unittest` da biblioteca padrão. Para executar todos os testes:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Para executar um arquivo de teste específico:

```bash
python -m unittest tests.test_lexer
python -m unittest tests.test_codegen
```

---

## Validação no CPULATOR

Passo a passo para validar o Assembly gerado no simulador CPULATOR:

1. Gere o arquivo `.s`:
   ```bash
   python main.py teste1.txt
   ```
2. Abra o **CPULATOR** e selecione o modelo **ARMv7 DEC1-SOC (v16.1)**.
3. Carregue o arquivo `.s` gerado.
4. Monte e execute o programa.
5. Verifique que as instruções de cada linha foram emitidas corretamente:
   - Operadores reais: `+`, `-`, `*`, `/`
   - Operadores inteiros: `//`, `%`
   - Potência: `^` (com expoente inteiro)
   - Comandos especiais: `RES`, armazenamento e leitura de memória

---

## Observação Importante

O programa em Python **não executa** os cálculos da linguagem-alvo. Ele apenas:

1. Lê o código-fonte da linguagem de entrada;
2. Realiza a análise léxica (tokenização via AFD);
3. Gera o código Assembly para a arquitetura-alvo (ARMv7).

---

# Documentação Técnica

## Visão Geral da Arquitetura

O sistema é organizado em um pipeline de três estágios sequenciais:

```
 Arquivo .txt ──▶ Leitura (io_utils) ──▶ Análise Léxica (lexer_fsm)
                                              │
                                         Lista de Tokens
                                              │
                                              ▼
                                   Parsing + Geração (assembly_generator)
                                              │
                                         Código Assembly
                                              │
                                              ▼
                                       Arquivo .s (saída)
```

O fluxo completo, orquestrado por `main.py`, é:

1. **Leitura** — `io_utils.ler_arquivo()` lê o arquivo de entrada e retorna uma lista de strings (uma por linha).
2. **Tokenização** — Para cada linha não vazia, `lexer_fsm.parse_expressao()` executa o AFD e produz uma lista de `Token`.
3. **Parsing e geração** — `AssemblyGenerator.adicionar_expressao()` converte os tokens em uma AST (árvore sintática), emite instruções intermediárias e, ao final, `gerar_programa()` serializa tudo em Assembly ARMv7.

---

## Módulo `tokens.py` — Definição de Tokens

### Enum `TokenType`

Define os sete tipos de token reconhecidos pelo analisador léxico:

| TokenType      | Descrição                                   | Exemplos de lexema     |
|----------------|---------------------------------------------|------------------------|
| `LPAREN`       | Parêntese de abertura                       | `(`                    |
| `RPAREN`       | Parêntese de fechamento                     | `)`                    |
| `INT`          | Número inteiro                              | `42`, `0`, `7`         |
| `REAL`         | Número real (ponto decimal)                 | `3.14`, `0.5`          |
| `OPERATOR`     | Operador aritmético                         | `+`, `-`, `*`, `/`, `//`, `%`, `^` |
| `IDENTIFIER`   | Identificador de memória (letras maiúsculas)| `MEM`, `TOTAL`, `X`   |
| `RES`          | Comando especial de resultado anterior      | `RES`                  |

### Constante `OPERATORS`

Conjunto (`set`) contendo todos os operadores válidos: `{"+", "-", "*", "/", "//", "%", "^"}`.

### Dataclass `Token`

```python
@dataclass(frozen=True)
class Token:
    token_type: TokenType
    lexeme: str
```

Cada token é imutável (`frozen=True`) e armazena seu tipo e o lexema original extraído da entrada.

---

## Módulo `lexer_fsm.py` — Analisador Léxico (AFD)

### Princípio de Funcionamento

O analisador léxico é implementado como um **Autômato Finito Determinístico (AFD)** em que cada **estado é uma função Python**. Não é utilizada nenhuma expressão regular.

O padrão de execução é:

```python
state = _state_initial
while state is not None:
    state = state(ctx)
```

Cada função de estado recebe um `_FSMContext`, inspeciona o caractere atual, pode avançar a posição (`ctx.pos`), emitir tokens (`ctx.tokens.append(...)`) e retorna a **próxima função de estado** (ou `None` para finalizar).

### Classe `_FSMContext`

Mantém todo o estado mutável do autômato durante a análise de uma linha:

| Atributo         | Tipo             | Descrição                                  |
|------------------|------------------|--------------------------------------------|
| `line`           | `str`            | A linha de entrada sendo analisada         |
| `pos`            | `int`            | Posição atual do cursor na linha           |
| `paren_balance`  | `int`            | Contador de parênteses abertos/fechados    |
| `tokens`         | `list[Token]`    | Lista de tokens emitidos até o momento     |

O método `current_char()` retorna o caractere na posição atual ou `None` se o fim da linha foi atingido.

### Diagrama de Estados do AFD

```
         ┌──────────────────────────────────────────┐
         │              _state_initial               │
         │  (estado inicial e de retorno principal)  │
         └─────┬────────┬────────┬────────┬─────────┘
               │        │        │        │
          espaço    ( ou )   dígito   +-*/%^   letra
          ──▶ loop  ──▶ emite  ──▶        ──▶       ──▶
          (volta)   LPAREN/     │         │          │
                    RPAREN      ▼         ▼          ▼
                    (volta) _state_    _state_    _state_
                            number    operator   identifier
                              │          │          │
                              └──────────┴──────────┘
                                    volta a
                                _state_initial
```

### Funções de Estado

#### `_state_initial(ctx)`

Estado de despacho principal. Classifica o caractere atual e redireciona para o estado apropriado:

- **Espaço em branco** → avança `pos` e permanece em `_state_initial`.
- **`(`** → emite `LPAREN`, incrementa `paren_balance`, volta a `_state_initial`.
- **`)`** → emite `RPAREN`, decrementa `paren_balance` (erro se ficar negativo), volta a `_state_initial`.
- **Dígito** → transiciona para `_state_number`.
- **Caractere em `+-*/%^`** → transiciona para `_state_operator`.
- **Letra alfabética** → transiciona para `_state_identifier`.
- **Qualquer outro** → levanta `LexerError`.
- **`None` (fim da linha)** → retorna `None` (encerra o AFD).

#### `_state_number(ctx)`

Consome dígitos e no máximo um ponto decimal (`.`). Regras de erro:

- Dois pontos decimais → `LexerError` ("ponto decimal duplicado").
- Vírgula → `LexerError` ("use ponto como separador decimal").
- Lexema começando ou terminando com `.` → `LexerError` ("Numero malformado").

Ao final, emite um token `INT` (sem ponto) ou `REAL` (com ponto) e retorna `_state_initial`.

#### `_state_operator(ctx)`

Consome um ou dois caracteres para reconhecer operadores:

- Se o caractere é `/` e o próximo também é `/` → emite `//` (divisão inteira), avança 2 posições.
- Caso contrário, emite o operador de caractere único (`+`, `-`, `*`, `/`, `%`, `^`).

Retorna `_state_initial`.

#### `_state_identifier(ctx)`

Consome caracteres alfabéticos consecutivos formando um lexema:

- Se o lexema é `"RES"` → emite token `RES`.
- Se o lexema contém apenas letras maiúsculas → emite token `IDENTIFIER`.
- Caso contrário → `LexerError` ("use apenas letras maiusculas").

Retorna `_state_initial`.

### Função `parse_expressao(linha)`

Ponto de entrada público do módulo. Executa o AFD completo sobre `linha` e, ao final, valida:

1. Que `paren_balance == 0` (parênteses balanceados).
2. Que todos os operadores emitidos pertencem ao conjunto `OPERATORS`.

Retorna `list[Token]` ou levanta `LexerError`.

### Classe `LexerError`

Subclasse de `ValueError` usada para todos os erros léxicos, permitindo tratamento diferenciado no `main.py`.

---

## Módulo `assembly_generator.py` — Parser e Gerador de Código

Este módulo tem duas responsabilidades: (1) transformar a lista de tokens em uma **AST** (árvore sintática abstrata) e (2) emitir código **Assembly ARMv7**.

### Nós da AST

| Classe          | Atributos                | Descrição                                  |
|-----------------|--------------------------|--------------------------------------------|
| `NumberNode`    | `literal: str`, `is_int: bool` | Literal numérico (inteiro ou real)    |
| `MemLoadNode`   | `name: str`              | Leitura de variável de memória             |
| `MemStoreNode`  | `name: str`, `value`     | Armazenamento de valor em memória          |
| `ResNode`       | `offset: int`            | Referência ao resultado de uma linha anterior |
| `BinOpNode`     | `op: str`, `left`, `right` | Operação binária com dois operandos      |

### Parser — `_TokenCursor` e funções de parsing

O parser usa um cursor (`_TokenCursor`) que percorre a lista de tokens sequencialmente:

- `peek(ahead)` — observa o token na posição `index + ahead` sem consumi-lo.
- `consume(expected)` — consome e retorna o próximo token, opcionalmente validando o tipo.

#### `_parse_expr(cursor)` — Parsing de uma expressão entre parênteses

A lógica de decisão é:

1. Consome `LPAREN`.
2. **Lookahead de 2 tokens**: se o próximo é `IDENTIFIER` seguido de `RPAREN` → é uma leitura de memória → retorna `MemLoadNode`.
3. Caso contrário, faz parsing do primeiro item (`_parse_item`).
4. Inspeciona o token seguinte:
   - `RES` → valida que o primeiro item é inteiro não negativo → retorna `ResNode`.
   - `IDENTIFIER` → retorna `MemStoreNode` (armazenamento em memória).
   - Outro → faz parsing do segundo item e do operador → retorna `BinOpNode`.

#### `_parse_item(cursor)` — Parsing de um item (operando)

- `LPAREN` → chama `_parse_expr` recursivamente (expressão aninhada).
- `REAL` → retorna `NumberNode(is_int=False)`.
- `INT` → retorna `NumberNode(is_int=True)`.

### Classe `AssemblyGenerator`

#### Estado Interno

| Atributo           | Tipo                                     | Descrição                                           |
|--------------------|------------------------------------------|-----------------------------------------------------|
| `_expr_instrs`     | `list[list[tuple[str, ...]]]`            | Instruções intermediárias por expressão/linha        |
| `_constants`       | `dict[str, str]`                         | Mapa de literais numéricos para rótulos `.data`      |
| `_memories`        | `set[str]`                               | Nomes de variáveis de memória usadas                |

#### Representação Intermediária

Antes de gerar Assembly, o gerador produz instruções intermediárias (tuplas):

| Instrução         | Argumento      | Semântica                                     |
|-------------------|----------------|-----------------------------------------------|
| `PUSH_CONST`      | rótulo `.data` | Carrega constante numérica na pilha           |
| `LOAD_MEM`        | nome           | Carrega variável de memória na pilha          |
| `LOAD_RES`        | índice         | Carrega resultado de expressão anterior       |
| `STORE_MEM`       | nome           | Desempilha valor e armazena em memória        |
| `BIN_OP`          | operador       | Desempilha dois operandos, opera, empilha     |

#### Método `adicionar_expressao(tokens, numero_linha)`

1. Converte tokens em AST via `_parse_tokens`.
2. Percorre a AST recursivamente com `_emit_node`, gerando a lista de instruções intermediárias.
3. Armazena as instruções em `_expr_instrs`.

#### Método `gerar_programa()` — Geração Assembly

Produz o texto Assembly completo em quatro seções:

**1. Cabeçalho e inicialização (`.text`)**

```asm
.syntax unified
.cpu cortex-a9
.fpu vfpv3
.global _start

.text
_start:
    ldr r10, =eval_stack    @ r10 = base da pilha de avaliação
    mov r11, #0              @ r11 = offset do topo da pilha
```

**2. Código das expressões**

Para cada expressão `i`, emite um rótulo `line_i:` seguido das instruções. Ao final de cada expressão, desempilha o resultado e armazena em `result_i`.

**3. Sub-rotinas auxiliares**

| Sub-rotina             | Finalidade                                              |
|------------------------|---------------------------------------------------------|
| `push_d0`              | Empilha o valor de `d0` na pilha de avaliação           |
| `pop_to_d0`            | Desempilha o topo para `d0`                             |
| `pop_to_d1`            | Desempilha o topo para `d1`                             |
| `op_int_div`           | Divisão inteira (`//`) — converte para inteiro, divide  |
| `op_int_mod`           | Módulo (`%`) — converte para inteiro, calcula resto     |
| `op_pow_int`           | Potência (`^`) — multiplicação iterativa com expoente   |
| `int_divide_signed`    | Divisão inteira com sinal por subtração sucessiva       |
| `int_mod_signed`       | Módulo com sinal por subtração sucessiva                |
| `runtime_error`        | Loop infinito em caso de erro de execução               |

**4. Seção de dados (`.data`)**

```asm
.data
eval_stack: .space 8192       @ Pilha de avaliação (1024 doubles)
const_one: .double 1.0        @ Constante 1.0 (usada por op_pow_int)
const_0: .double 3.14         @ Constantes numéricas do programa
mem_TOTAL: .double 0.0        @ Variáveis de memória
result_0: .double 0.0         @ Resultados por expressão
```

#### Mapeamento de Operadores para Assembly

| Operador | Instrução Assembly gerada     | Tipo         |
|----------|-------------------------------|--------------|
| `+`      | `vadd.f64 d0, d1, d0`        | Ponto flutuante |
| `-`      | `vsub.f64 d0, d1, d0`        | Ponto flutuante |
| `*`      | `vmul.f64 d0, d1, d0`        | Ponto flutuante |
| `/`      | `vdiv.f64 d0, d1, d0`        | Ponto flutuante |
| `//`     | `bl op_int_div`               | Inteiro      |
| `%`      | `bl op_int_mod`               | Inteiro      |
| `^`      | `bl op_pow_int`               | Inteiro (expoente) |

Todas as operações binárias seguem o padrão: desempilham dois operandos (`pop_to_d0`, `pop_to_d1`), executam a operação e empilham o resultado (`push_d0`).

#### Convenção de Registradores

| Registrador | Uso no programa gerado                          |
|-------------|--------------------------------------------------|
| `r10`       | Ponteiro base da pilha de avaliação (`eval_stack`) |
| `r11`       | Offset do topo da pilha (em bytes)               |
| `r4`        | Registrador temporário para endereços            |
| `r0`, `r1`  | Operandos inteiros para divisão/módulo           |
| `d0`        | Registrador FP de dupla precisão (operando/resultado) |
| `d1`        | Segundo operando FP de dupla precisão            |
| `d2`        | Base da potência em `op_pow_int`                 |

---

## Módulo `io_utils.py` — Entrada e Saída

Duas funções utilitárias simples:

- **`ler_arquivo(nome_arquivo) → list[str]`** — Lê o arquivo em UTF-8 e retorna uma lista de linhas. Levanta `FileNotFoundError` se o arquivo não existir ou `IsADirectoryError` se o caminho não for um arquivo regular.
- **`escrever_arquivo(nome_arquivo, conteudo)`** — Escreve o conteúdo (string) em um arquivo em UTF-8, sobrescrevendo caso já exista.

---

## Módulo `main.py` — Ponto de Entrada

A função `main(argv)` coordena todo o pipeline:

1. Valida os argumentos de linha de comando (mínimo 1 arquivo de entrada).
2. Determina o nome de saída: se não fornecido, substitui a extensão por `.s`.
3. Lê as linhas do arquivo via `ler_arquivo`.
4. Itera sobre cada linha não vazia:
   - Chama `parse_expressao` (análise léxica).
   - Chama `gerador.adicionar_expressao` (parsing + geração intermediária).
5. Chama `gerador.gerar_programa()` para serializar o Assembly.
6. Escreve o resultado via `escrever_arquivo`.

Retorna `0` em sucesso ou `1` em caso de erro (mensagem impressa no `stdout`).

---

## Testes Automatizados

### `tests/test_lexer.py`

| Teste                                  | O que valida                                                    |
|----------------------------------------|-----------------------------------------------------------------|
| `test_entrada_valida_tokens_basicos`   | Tokenização de `(3.14 2.0 +)` — verifica lexemas e tipos       |
| `test_entrada_valida_comandos_especiais`| Tokens para `RES`, armazenamento e leitura de memória          |
| `test_numero_malformado`               | `LexerError` para ponto duplo (`3.14.5`) e vírgula (`3,45`)    |
| `test_operador_invalido`               | `LexerError` para operador não reconhecido (`&`)                |
| `test_parenteses_desbalanceados`       | `LexerError` para parênteses não fechados                       |

### `tests/test_codegen.py`

| Teste                                         | O que valida                                                            |
|------------------------------------------------|-------------------------------------------------------------------------|
| `test_gera_assembly_com_operadores_e_comandos` | Geração completa com 8 expressões cobrindo todos os operadores e comandos |
| `test_res_invalido_lanca_erro`                 | `ValueError` quando `RES` referencia resultado inexistente              |

---

## Tratamento de Erros

O sistema utiliza exceções tipadas para comunicar erros ao longo do pipeline:

| Exceção              | Módulo               | Situação                                                  |
|----------------------|----------------------|-----------------------------------------------------------|
| `LexerError`         | `lexer_fsm`          | Token inválido, número malformado, parênteses desbalanceados |
| `ValueError`         | `assembly_generator`  | AST inválida, `RES` fora de alcance, expressão vazia       |
| `FileNotFoundError`  | `io_utils`           | Arquivo de entrada não encontrado                          |
| `IsADirectoryError`  | `io_utils`           | Caminho aponta para diretório em vez de arquivo            |

O `main.py` captura `LexerError` e `ValueError` por linha, imprime a mensagem com o número da linha e encerra com código `1`.
