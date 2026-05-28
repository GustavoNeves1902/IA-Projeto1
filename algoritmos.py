"""
Projeto 1 – Inteligência Artificial – UNIOESTE 2026
Disciplina: Inteligência Artificial | Curso: Ciência da Computação

Implementação dos algoritmos de busca aplicados ao mapa de Super Mario World:
  - A* (Melhor Solução): busca informada com heurística admissível
  - Busca em Profundidade com Backtracking (Pior Solução): busca não informada
  - A* com Limite de Distância (Bônus): A* com poda por orçamento máximo

Medida de desempenho adotada: Nós expandidos.
Quanto menor o número de nós expandidos, melhor o desempenho do algoritmo,
pois indica que menos estados foram processados para chegar à solução.
"""

from __future__ import annotations

import heapq
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Parser de arquivo de entrada
# ---------------------------------------------------------------------------

def carregar_arquivo(caminho: str) -> dict:
    """
    Lê e analisa um arquivo de entrada no formato Prolog-like definido pelo projeto.

    Formato esperado (comentários com % são ignorados):
        ponto_inicial(a0).
        ponto_final(f0).
        orientado(s).          # s = orientado, n = não-orientado
        pode_ir(a0,b0,95).
        h(a0,f0,58).

    Returns:
        dict com chaves: grafo, heuristicas, ponto_inicial, ponto_final, orientado
    """
    grafo: dict[str, dict[str, int]] = {}
    heuristicas: dict[str, int] = {}
    ponto_inicial: Optional[str] = None
    ponto_final: Optional[str] = None
    orientado: bool = True
    arestas: list[tuple[str, str, int]] = []

    # Flags comuns: ignora maiúsculas/minúsculas em palavras-chave
    F = re.IGNORECASE

    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha_limpa = linha.split("%")[0].strip()
            if not linha_limpa:
                continue

            # \s* absorve espaços dentro dos parênteses e em torno das vírgulas
            m = re.match(r"ponto_inicial\(\s*(\w+)\s*\)\.", linha_limpa, F)
            if m:
                ponto_inicial = m.group(1).lower()
                continue

            m = re.match(r"ponto_final\(\s*(\w+)\s*\)\.", linha_limpa, F)
            if m:
                ponto_final = m.group(1).lower()
                continue

            m = re.match(r"orientado\(\s*([sn])\s*\)\.", linha_limpa, F)
            if m:
                orientado = m.group(1).lower() == "s"
                continue

            m = re.match(
                r"pode_ir\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\d+)\s*\)\.", linha_limpa, F
            )
            if m:
                arestas.append((m.group(1).lower(), m.group(2).lower(), int(m.group(3))))
                continue

            m = re.match(
                r"h\(\s*(\w+)\s*,\s*\w+\s*,\s*(\d+)\s*\)\.", linha_limpa, F
            )
            if m:
                heuristicas[m.group(1).lower()] = int(m.group(2))

    for origem, destino, custo in arestas:
        grafo.setdefault(origem, {})[destino] = custo
        if not orientado:
            grafo.setdefault(destino, {})[origem] = custo

    if ponto_inicial is None or ponto_final is None:
        raise ValueError(
            f"Arquivo '{caminho}' não contém ponto_inicial ou ponto_final válidos."
        )

    return {
        "grafo": grafo,
        "heuristicas": heuristicas,
        "ponto_inicial": ponto_inicial,
        "ponto_final": ponto_final,
        "orientado": orientado,
    }


# ---------------------------------------------------------------------------
# Resultado de busca
# ---------------------------------------------------------------------------

@dataclass
class ResultadoBusca:
    """Encapsula todos os dados de uma execução de busca."""
    algoritmo: str
    arquivo: str
    ponto_inicial: str
    ponto_final: str
    solucao_encontrada: bool
    custo: Optional[int]
    caminho: list[str]
    nos_expandidos: int
    iteracoes: int
    tempo_ms: float
    log: list[str] = field(default_factory=list, repr=False)


# ---------------------------------------------------------------------------
# Utilitário interno de saída
# ---------------------------------------------------------------------------

def _make_emitter(verbose: bool, log: list[str]):
    """Retorna função que grava em log e (opcionalmente) imprime no console."""
    def emit(txt: str):
        log.append(txt)
        if verbose:
            print(txt)
    return emit


# ---------------------------------------------------------------------------
# A* — Melhor Solução
# ---------------------------------------------------------------------------

class AEstrela:
    """
    A* — Melhor Solução.

    Combina o custo acumulado g(n) com a heurística admissível h(n) — distância
    em linha reta ao destino — para priorizar os nós mais promissores na fila.
    Garante o caminho de menor custo quando h(n) nunca superestima o custo real.

    Estrutura de controle : Fila de Prioridade (min-heap por f = g + h).
    Medida de desempenho  : Nós expandidos (quanto menor, melhor).
    """

    NOME = "A*"
    ESTRUTURA = "Fila de Prioridade"

    def __init__(
        self,
        grafo: dict[str, dict[str, int]],
        heuristicas: dict[str, int],
        inicio: str,
        fim: str,
    ) -> None:
        self.grafo = grafo
        self.heuristicas = heuristicas
        self.inicio = inicio
        self.fim = fim

    def _h(self, no: str) -> int:
        return self.heuristicas.get(no, 0)

    def executar(self, verbose: bool = True) -> ResultadoBusca:
        log: list[str] = []
        emit = _make_emitter(verbose, log)

        emit("Início da execução")
        t0 = time.perf_counter()

        # Heap: (f, id_desempate, nó, g_acumulado, caminho)
        fronteira: list = []
        _id = 0
        heapq.heappush(
            fronteira,
            (self._h(self.inicio), _id, self.inicio, 0, [self.inicio]),
        )
        melhor_g: dict[str, int] = {self.inicio: 0}

        iteracao = 1
        nos_expandidos = 0
        sucesso = False
        custo_final: Optional[int] = None
        caminho_final: list[str] = []

        while fronteira:
            f_atual, _, atual, g_atual, caminho = heapq.heappop(fronteira)

            # Descarta entradas obsoletas (outro caminho melhor já foi encontrado)
            if g_atual > melhor_g.get(atual, float("inf")):
                continue

            nos_expandidos += 1

            if atual == self.fim:
                sucesso = True
                custo_final = g_atual
                caminho_final = caminho
                break

            for vizinho, custo in sorted(self.grafo.get(atual, {}).items()):
                novo_g = g_atual + custo
                if novo_g < melhor_g.get(vizinho, float("inf")):
                    melhor_g[vizinho] = novo_g
                    _id += 1
                    heapq.heappush(
                        fronteira,
                        (novo_g + self._h(vizinho), _id, vizinho, novo_g, caminho + [vizinho]),
                    )

            # Exibe estado da fila após esta expansão (melhor entrada por nó)
            melhor_no: dict[str, tuple[int, int]] = {}
            for f, _, no, g, _ in fronteira:
                if no not in melhor_no or g < melhor_no[no][1]:
                    melhor_no[no] = (f, g)

            if melhor_no:
                itens = sorted(melhor_no.items(), key=lambda kv: (kv[1][0], kv[0]))
                partes = [
                    f"({no}: {g} + {self._h(no)} = {f})"
                    for no, (f, g) in itens
                ]
                emit(f"\nIteração {iteracao}:")
                emit(f"{self.ESTRUTURA}: {' '.join(partes)}")
                emit(f"Nós expandidos: {nos_expandidos}")
                iteracao += 1

        tempo_ms = (time.perf_counter() - t0) * 1_000

        emit("\n" + "=" * 50)
        emit("Fim da execução")
        emit(f"Distância: {custo_final if sucesso else 'Não encontrada'}")
        emit(
            f"Caminho: {' – '.join(caminho_final)}"
            if sucesso
            else "Caminho: Nenhum caminho encontrado"
        )
        emit(f"Nós expandidos: {nos_expandidos}")
        emit(f"Tempo de execução: {tempo_ms:.3f} ms")
        emit("=" * 50)

        return ResultadoBusca(
            algoritmo=self.NOME,
            arquivo="",
            ponto_inicial=self.inicio,
            ponto_final=self.fim,
            solucao_encontrada=sucesso,
            custo=custo_final,
            caminho=caminho_final,
            nos_expandidos=nos_expandidos,
            iteracoes=iteracao - 1,
            tempo_ms=tempo_ms,
            log=log,
        )


# ---------------------------------------------------------------------------
# Busca em Profundidade com Backtracking — Pior Solução
# ---------------------------------------------------------------------------

class BuscaProfundidadeBacktracking:
    """
    Busca em Profundidade com Backtracking — Pior Solução.

    Explora o grafo sistematicamente em profundidade, sem heurística (h = 0).
    Não garante o caminho de menor custo.

    O backtracking ocorre quando um ramo é esgotado: nenhum vizinho disponível
    no caminho atual. Nesse momento a pilha retorna ao estado anterior para
    explorar alternativas — comportamento visível no encolhimento da pilha.

    Diferença essencial frente ao DFS clássico: nós são marcados como visitados
    apenas no caminho atual (não globalmente), permitindo que o mesmo nó seja
    alcançado por rotas distintas em diferentes ramos da busca.

    Estrutura de controle : Pilha (LIFO).
    Medida de desempenho  : Nós expandidos (tende a ser maior que A*).
    """

    NOME = "Busca em Profundidade com Backtracking"
    ESTRUTURA = "Pilha"

    def __init__(
        self,
        grafo: dict[str, dict[str, int]],
        inicio: str,
        fim: str,
    ) -> None:
        self.grafo = grafo
        self.inicio = inicio
        self.fim = fim

    def executar(self, verbose: bool = True) -> ResultadoBusca:
        log: list[str] = []
        emit = _make_emitter(verbose, log)

        emit("Início da execução")
        t0 = time.perf_counter()

        # Entradas da pilha: (nó, custo_acumulado, caminho_atual)
        # O caminho_atual serve como conjunto de visitados do ramo corrente,
        # permitindo o backtracking correto ao liberar nós de ramos descartados.
        pilha: list[tuple[str, int, list[str]]] = [
            (self.inicio, 0, [self.inicio])
        ]

        iteracao = 1
        nos_expandidos = 0
        sucesso = False
        custo_final: Optional[int] = None
        caminho_final: list[str] = []

        while pilha:
            no, dist, caminho = pilha.pop()
            nos_expandidos += 1

            if no == self.fim:
                sucesso = True
                custo_final = dist
                caminho_final = caminho
                break

            # Empurra vizinhos na ordem reversa para que o primeiro
            # em ordem alfabética fique no topo da pilha.
            caminho_set = set(caminho)
            vizinhos = sorted(
                self.grafo.get(no, {}).items(),
                key=lambda kv: kv[0],
                reverse=True,
            )
            for vizinho, custo in vizinhos:
                if vizinho not in caminho_set:
                    pilha.append((vizinho, dist + custo, caminho + [vizinho]))

            # Exibe estado da pilha após esta expansão (topo primeiro)
            if pilha:
                partes = [
                    f"({n}: {d} + 0 = {d})" for n, d, _ in reversed(pilha)
                ]
                emit(f"\nIteração {iteracao}:")
                emit(f"{self.ESTRUTURA}: {' '.join(partes)}")
                emit(f"Nós expandidos: {nos_expandidos}")
                iteracao += 1

        tempo_ms = (time.perf_counter() - t0) * 1_000

        emit("\n" + "=" * 50)
        emit("Fim da execução")
        emit(f"Distância: {custo_final if sucesso else 'Não encontrada'}")
        emit(
            f"Caminho: {' – '.join(caminho_final)}"
            if sucesso
            else "Caminho: Nenhum caminho encontrado"
        )
        emit(f"Nós expandidos: {nos_expandidos}")
        emit(f"Tempo de execução: {tempo_ms:.3f} ms")
        emit("=" * 50)

        return ResultadoBusca(
            algoritmo=self.NOME,
            arquivo="",
            ponto_inicial=self.inicio,
            ponto_final=self.fim,
            solucao_encontrada=sucesso,
            custo=custo_final,
            caminho=caminho_final,
            nos_expandidos=nos_expandidos,
            iteracoes=iteracao - 1,
            tempo_ms=tempo_ms,
            log=log,
        )


# ---------------------------------------------------------------------------
# A* com Limite de Distância — Bônus
# ---------------------------------------------------------------------------

class AEstrelaComLimite:
    """
    A* com Limite de Distância — Bônus.

    Variação do A* que descarta qualquer caminho cujo custo acumulado g(n)
    excede um limite máximo informado pelo usuário. Modela o cenário em que o
    jogador possui energia ou distância máxima disponível para percorrer.

    Caminhos que ultrapassariam o limite são podados antes de entrar na fila,
    e uma mensagem de descarte é exibida a cada iteração em que isso ocorre.

    Estrutura de controle : Fila de Prioridade (min-heap por f = g + h).
    Medida de desempenho  : Nós expandidos.
    """

    NOME = "A* com Limite de Distância"
    ESTRUTURA = "Fila de Prioridade"

    def __init__(
        self,
        grafo: dict[str, dict[str, int]],
        heuristicas: dict[str, int],
        inicio: str,
        fim: str,
    ) -> None:
        self.grafo = grafo
        self.heuristicas = heuristicas
        self.inicio = inicio
        self.fim = fim

    def _h(self, no: str) -> int:
        return self.heuristicas.get(no, 0)

    def executar(self, limite: int, verbose: bool = True) -> ResultadoBusca:
        log: list[str] = []
        emit = _make_emitter(verbose, log)

        emit("Início da execução")
        t0 = time.perf_counter()

        fronteira: list = []
        _id = 0
        heapq.heappush(
            fronteira,
            (self._h(self.inicio), _id, self.inicio, 0, [self.inicio]),
        )
        melhor_g: dict[str, int] = {self.inicio: 0}

        iteracao = 1
        nos_expandidos = 0
        sucesso = False
        custo_final: Optional[int] = None
        caminho_final: list[str] = []

        while fronteira:
            f_atual, _, atual, g_atual, caminho = heapq.heappop(fronteira)

            if g_atual > melhor_g.get(atual, float("inf")):
                continue

            nos_expandidos += 1
            dist_disponivel = limite - g_atual

            if atual == self.fim:
                sucesso = True
                custo_final = g_atual
                caminho_final = caminho
                break

            descartados = 0
            for vizinho, custo in sorted(self.grafo.get(atual, {}).items()):
                novo_g = g_atual + custo
                if novo_g > limite:
                    descartados += 1
                    continue
                if novo_g < melhor_g.get(vizinho, float("inf")):
                    melhor_g[vizinho] = novo_g
                    _id += 1
                    heapq.heappush(
                        fronteira,
                        (novo_g + self._h(vizinho), _id, vizinho, novo_g, caminho + [vizinho]),
                    )

            melhor_no: dict[str, tuple[int, int]] = {}
            for f, _, no, g, _ in fronteira:
                if no not in melhor_no or g < melhor_no[no][1]:
                    melhor_no[no] = (f, g)

            if melhor_no:
                itens = sorted(melhor_no.items(), key=lambda kv: (kv[1][0], kv[0]))
                partes = [
                    f"({no}: {g} + {self._h(no)} = {f})"
                    for no, (f, g) in itens
                ]
                emit(f"\nIteração {iteracao}:")
                emit(f"{self.ESTRUTURA}: {' '.join(partes)}")
                emit(f"Nós expandidos: {nos_expandidos}")
                if descartados:
                    emit(
                        f"Distância disponível 0 – "
                        f"{descartados} caminho(s) descartado(s) (excederam limite={limite})"
                    )
                else:
                    emit(f"Distância disponível: {dist_disponivel}")
                iteracao += 1

        tempo_ms = (time.perf_counter() - t0) * 1_000

        emit("\n" + "=" * 50)
        emit("Fim da execução")
        emit(
            f"Distância: {custo_final if sucesso else 'Não encontrada dentro do limite'}"
        )
        emit(
            f"Caminho: {' – '.join(caminho_final)}"
            if sucesso
            else "Caminho: Nenhum caminho encontrado dentro do limite"
        )
        emit(f"Nós expandidos: {nos_expandidos}")
        emit(f"Tempo de execução: {tempo_ms:.3f} ms")
        emit("=" * 50)

        return ResultadoBusca(
            algoritmo=f"{self.NOME} (limite={limite})",
            arquivo="",
            ponto_inicial=self.inicio,
            ponto_final=self.fim,
            solucao_encontrada=sucesso,
            custo=custo_final,
            caminho=caminho_final,
            nos_expandidos=nos_expandidos,
            iteracoes=iteracao - 1,
            tempo_ms=tempo_ms,
            log=log,
        )
