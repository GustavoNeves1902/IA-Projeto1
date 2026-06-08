# Projeto 1 IA - Busca

Este projeto implementa algoritmos de busca em grafos para encontrar caminhos no mapa do jogo Super Mario World, utilizando os algoritmos **A* (A-Estrela)**, **Busca em Profundidade com Backtracking (DFS)** e **A* Limitado**.

---

## 🛠️ Requisitos e Bibliotecas

**Não é necessário instalar nenhuma biblioteca de terceiros (externa) via `pip`!**

O projeto foi desenvolvido inteiramente utilizando a **Biblioteca Padrão do Python (Python Standard Library)**.

### Módulos Nativos Utilizados:
*   `sys`: Usado para manipulação do sistema e encerramento do programa.
*   `heapq`: Usado para a estrutura de Min-Heap (Fila de Prioridade) eficiente exigida pelo algoritmo A*.
*   `csv`: Usado para guardar os resultados de cada execução no ficheiro `resultados.csv`.
*   `os`: Usado para verificar a existência do ficheiro CSV antes de escrever o cabeçalho.

### Requisito do Sistema:
*   **Python 3.6** ou superior instalado.

---

## 🚀 Como Executar o Projeto

1. Abra o terminal na pasta do projeto:
   ```bash
   cd "IA-Projeto1"
   ```

2. Execute o arquivo `main.py` utilizando o interpretador do Python 3:
   ```bash
   python3 main.py
   ```

3. No menu interativo, escolha a opção desejada:
   *   **1:** Carregar um arquivo de mapa (ex: `teste.txt`, `teste2.txt`, ...).
   *   **2:** Executar a **Busca em Profundidade com Backtracking**.
   *   **3:** Executar o **A* (A-Estrela)**.
   *   **4:** *(BÔNUS)* Executar o **A* Limitado** (com distância máxima configurável).
   *   **5:** Sair do programa.

> ⚠️ **Atenção:** É obrigatório carregar um arquivo (opção 1) antes de executar qualquer algoritmo de busca.

---

## 📂 Formato do Arquivo de Entrada (Grafo)

O programa lê a estrutura do mapa a partir de arquivos de texto (como os incluídos no projeto). O arquivo deve seguir a seguinte estrutura:

*   **Ponto Inicial:** `ponto_inicial(no_origem).`
*   **Ponto Final:** `ponto_final(no_destino).`
*   **Orientação:** `orientado(s).` (sim) ou `orientado(n).` (não)
*   **Arestas/Conexões:** `pode_ir(origem, destino, custo).`
*   **Heurísticas (distância em linha reta até o objetivo):** `h(no, destino, valor_h).`

> 💡 **Nota:** Linhas que começam com `%` são tratadas como comentários e ignoradas pelo interpretador do programa.

---

## 🧠 Algoritmos Implementados

### 1. Algoritmo A* (A-Estrela)
*   Busca informada que utiliza a função de avaliação:
    $$f(n) = g(n) + h(n)$$
    Onde $g(n)$ é o custo real acumulado da origem até o nó $n$, e $h(n)$ é a estimativa heurística (distância em linha reta) do nó $n$ até o objetivo final.
*   Garante encontrar o caminho de custo mínimo caso a heurística seja admissível.
*   Exibe o passo a passo de cada iteração, o estado da fronteira de busca, o caminho percorrido e a medida de desempenho (nós expandidos e gerados).

### 2. Busca em Profundidade com Backtracking (DFS - Depth-First Search)
*   Busca não informada que explora sistematicamente os caminhos mais profundos primeiro.
*   Utiliza mecanismo de backtracking armazenando o caminho para retroceder caso alcance um caminho sem saída.
*   Possui detecção interna de loops para evitar ciclos infinitos no grafo.
*   Exibe o caminho encontrado e os nós expandidos durante a execução.

### 3. A* Limitado *(BÔNUS)*
*   Variante do A* que aceita uma **distância máxima** definida pelo utilizador.
*   Em cada iteração, exibe a **distância disponível** — o orçamento restante após os movimentos já realizados:
    *   **Iteração 1:** distância disponível = limite (ainda não houve movimento).
    *   **Iterações seguintes:** distância disponível = `limite - custo_acumulado_do_nó_anterior`.
*   Caminhos cujo valor $f(n)$ exceda o limite são automaticamente descartados.
*   Inclui verificação antecipada: se a heurística do nó inicial já ultrapassar o limite, a execução termina imediatamente.

---

## 📊 Resultados

Cada execução de um algoritmo é automaticamente registada no ficheiro `resultados.csv` com as seguintes colunas:

| Coluna | Descrição |
|---|---|
| `Arquivo .TXT` | Nome do ficheiro de mapa utilizado |
| `Algoritmo` | Nome do algoritmo executado |
| `Iterações` | Número total de iterações realizadas |
| `Nós Expandidos` | Quantidade de nós expandidos |
| `Nós Gerados` | Quantidade de nós gerados |
