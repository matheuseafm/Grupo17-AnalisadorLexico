# Grupo17 - Analisador Lexico RPN

Projeto da Fase 1 para ler expressoes em notacao polonesa reversa (RPN), realizar analise lexica por AFD com estados implementados por funcoes e gerar Assembly ARMv7 compativel com o alvo DEC1-SOC (CPULATOR).

## Requisitos atendidos

- Analise lexica sem regex.
- AFD deterministico com estados em funcoes no arquivo `lexer_fsm.py`.
- Reconhecimento de:
  - parenteses `(` e `)`;
  - numeros inteiros e reais com ponto decimal;
  - operadores `+ - * / // % ^`;
  - comandos especiais `RES` e identificadores de memoria em maiusculas.
- Geracao de Assembly ARMv7 em `assembly_generator.py`.
- Leitura de arquivo de entrada por argumento de linha de comando.
- Tres arquivos de teste (`teste1.txt`, `teste2.txt`, `teste3.txt`) com 10+ linhas cada.

## Estrutura

- `main.py`: entrada do programa.
- `io_utils.py`: leitura/escrita de arquivo.
- `tokens.py`: tipos de token.
- `lexer_fsm.py`: analisador lexico por automato finito.
- `assembly_generator.py`: parser estrutural minimo + gerador Assembly.
- `tests/test_lexer.py`: testes do lexer.
- `tests/test_codegen.py`: testes do gerador.

## Formato da linguagem (entrada)

Cada linha contem uma expressao:

- Operacoes binarias: `(A B op)` com `op` em `+ - * / // % ^`
- Uso de resultado anterior: `(N RES)` onde `N` e inteiro nao negativo
- Armazenamento em memoria: `(V MEM)` onde `MEM` tem apenas letras maiusculas
- Leitura de memoria: `(MEM)`
- Aninhamento: permitido com parenteses, por exemplo `((1 2 +) (3 4 *) /)`

## Execucao

Gerar Assembly a partir de um arquivo:

```bash
python main.py teste1.txt
```

Com nome de saida explicito:

```bash
python main.py teste1.txt saida.s
```

## Testes automatizados

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Checklist para validacao no CPULATOR

- Gerar arquivo `.s` com `python main.py teste1.txt`.
- Abrir CPULATOR no modelo `ARMv7 DEC1-SOC (v16.1)`.
- Carregar o `.s` gerado.
- Montar/executar e verificar que as instrucoes de cada linha foram emitidas:
  - operadores reais (`+ - * /`);
  - operadores inteiros (`// %`);
  - potencia (`^` com expoente inteiro);
  - comandos especiais (`RES`, armazenamento e leitura de memoria).

## Observacao importante

O programa em Python nao executa os calculos da linguagem-alvo. Ele apenas:

1. Le o codigo fonte da linguagem;
2. Faz analise lexica;
3. Gera Assembly para a arquitetura alvo.