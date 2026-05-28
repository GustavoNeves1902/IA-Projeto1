# Projeto 1 — Algoritmos de Busca em Grafos

**Disciplina:** Inteligência Artificial | **Curso:** Ciência da Computação — UNIOESTE 2026

Implementação de algoritmos de busca aplicados ao mapa do jogo *Super Mario World*, encontrando o caminho entre dois pontos do mapa.

---

## Requisitos

- Python **3.6+**
- Nenhuma biblioteca externa — apenas módulos da biblioteca padrão (`heapq`, `re`, `csv`)

---

## Como executar

```bash
python main.py
```

O programa inicia um menu interativo no terminal.

---

## Menu

```
1. Carregar arquivo de entrada
2. Executar algoritmo no arquivo carregado
3. Executar em lote (pasta de arquivos)
4. Exibir sumário dos resultados
5. Salvar resultados em CSV
6. Sair
```

**Opção 2 — Executar algoritmo:** após carregar um arquivo, escolha entre:
- `1` A* (Melhor Solução)
- `2` Busca em Profundidade com Backtracking (Pior Solução)
- `3` A* com Limite de Distância *(Bônus)*

**Opção 3 — Lote:** informe uma pasta; o programa processa todos os `.txt` encontrados, pergunta quais algoritmos rodar e gera os resultados prontos para exportar.

---

## Formato do arquivo de entrada

```prolog
ponto_inicial(a0).
ponto_final(f0).
orientado(s).          % s = orientado | n = não-orientado

pode_ir(a0,b0,95).     % aresta de a0 para b0 com custo 95
pode_ir(a0,c0,44).

h(a0,f0,58).           % heurística: distância em linha reta de a0 até f0
h(c0,f0,34).
```

> Linhas com `%` são comentários e são ignoradas.  
> O parser aceita **maiúsculas, minúsculas e espaços** em qualquer combinação — `PODE_IR( A0 , B0 , 95 ).` é válido.

---

## Algoritmos

| Algoritmo | Estrutura | Heurística | Garante ótimo? |
|---|---|---|---|
| **A\*** | Fila de prioridade | `f(n) = g(n) + h(n)` | Sim |
| **DFS com Backtracking** | Pilha (LIFO) | Não usa (`h = 0`) | Não |
| **A\* com Limite** *(bônus)* | Fila de prioridade | `f(n) = g(n) + h(n)` | Sim, dentro do limite |

**Medida de desempenho adotada:** número de nós expandidos — quanto menor, melhor.

O DFS explora em profundidade sem heurística e pode encontrar caminhos subótimos; o A* usa a distância em linha reta como estimativa e sempre encontra o menor custo.

A cada iteração o programa exibe o estado atual da estrutura de controle:

```
Iteração 2:
Fila de Prioridade: (c0: 44 + 34 = 78) (b0: 95 + 24 = 119) (d0: 98 + 37 = 135)
Nós expandidos: 2
```

---

## Saída CSV

Ao salvar (opção 5), é gerado um `.csv` com as colunas:

| arquivo | algoritmo | ponto_inicial | ponto_final | solucao_encontrada | custo | caminho | nos_expandidos | iteracoes | tempo_ms |
|---|---|---|---|---|---|---|---|---|---|

Executar em lote sobre uma pasta e salvar produz uma tabela comparativa direta entre os algoritmos.

---

## Estrutura de arquivos

```
IA-Projeto1/
├── algoritmos.py      # Parser + classes AEstrela, BuscaProfundidadeBacktracking, AEstrelaComLimite
├── main.py            # Menu interativo e runner de experimentos
├── teste.txt          # Exemplo do enunciado
├── teste2.txt         # Grafo não-orientado
└── exemplos/          # Pasta com casos de teste adicionais
```
