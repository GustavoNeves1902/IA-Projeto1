# Projeto 1 IA - Busca

Este projeto implementa algoritmos de busca em grafos para encontrar caminhos no mapa do jogo Super Mario World, utilizando os algoritmos **A* (A-Estrela)** e **Busca em Profundidade (DFS)**. 

---

## 🛠️ Requisitos e Bibliotecas

**não é necessário instalar nenhuma biblioteca de terceiros (externa) via `pip`!** 

O projeto foi desenvolvido inteiramente utilizando a **Biblioteca Padrão do Python (Python Standard Library)**.

### Módulos Nativos Utilizados:
*   `sys`: Usado para manipulação do sistema e encerramento do programa.
*   `heapq`: Usado para a estrutura de Min-Heap (Fila de Prioridade) eficiente exigida pelo algoritmo A*.

### Requisito do Sistema:
*   **Python 3.6** ou superior instalado.

---

## 🚀 Como Executar o Projeto

1. Abra o terminal na pasta do projeto:
   ```bash
   cd "/Users/gustavoneves/Desktop/Faculdade/4 ano/IA/Projeto 1"
   ```

2. Execute o arquivo `main.py` utilizando o interpretador do Python 3:
   ```bash
   python3 main.py
   ```

3. No menu interativo, escolha a opção desejada:
   *   **1:** Para carregar um arquivo de mapa (ex: `teste.txt`).
   *   **2:** Para executar a busca utilizando o algoritmo **A***.
   *   **3:** Para executar a **Busca em Profundidade**.
   *   **4:** Para sair.

---

## 📂 Formato do Arquivo de Entrada (Grafo)

O programa lê a estrutura do mapa a partir de arquivos de texto (como o `teste.txt` incluso). O arquivo deve seguir a seguinte estrutura:

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
*   Exibe o passo a passo de cada iteração, o estado da fronteira de busca, o caminho percorrido e a medida de desempenho (nós expandidos).

### 2. Busca em Profundidade (DFS - Depth-First Search)
*   Busca não informada que explora sistematicamente os caminhos mais profundos primeiro.
*   Possui detecção interna de loops para evitar ciclos infinitos no grafo.
*   Exibe o caminho encontrado e os nós expandidos durante a execução.
