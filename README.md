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
