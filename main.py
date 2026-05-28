"""
Projeto 1 – Inteligência Artificial – UNIOESTE 2026
Runner de experimentos com interface interativa via terminal.

Execute:
    python main.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from algoritmos import (
    AEstrela,
    AEstrelaComLimite,
    BuscaProfundidadeBacktracking,
    ResultadoBusca,
    carregar_arquivo,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

ALGORITMOS = {
    "1": ("astar", "A* (Melhor Solução)"),
    "2": ("dfs",   "Busca em Profundidade com Backtracking (Pior Solução)"),
    "3": ("bonus", "A* com Limite de Distância (Bônus)"),
}

CSV_CAMPOS = [
    "arquivo", "algoritmo", "ponto_inicial", "ponto_final",
    "solucao_encontrada", "custo", "caminho",
    "nos_expandidos", "iteracoes", "tempo_ms",
]


# ---------------------------------------------------------------------------
# Helpers de entrada
# ---------------------------------------------------------------------------

def _input(prompt: str) -> str:
    """input() que trata Ctrl+C/EOF sem encerrar o programa."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        return ""


def _input_int(prompt: str) -> Optional[int]:
    """Lê um inteiro, retorna None se inválido."""
    try:
        return int(_input(prompt))
    except ValueError:
        return None


def _confirmar(prompt: str) -> bool:
    """Pergunta s/n, retorna True para 's'."""
    return _input(f"{prompt} [s/n]: ").lower() == "s"


# ---------------------------------------------------------------------------
# Execução de algoritmo
# ---------------------------------------------------------------------------

def executar_algoritmo(
    config: dict,
    chave: str,
    verbose: bool = True,
    limite: Optional[int] = None,
) -> ResultadoBusca:
    grafo  = config["grafo"]
    h      = config["heuristicas"]
    inicio = config["ponto_inicial"]
    fim    = config["ponto_final"]

    if chave == "astar":
        return AEstrela(grafo, h, inicio, fim).executar(verbose=verbose)

    if chave == "dfs":
        return BuscaProfundidadeBacktracking(grafo, inicio, fim).executar(verbose=verbose)

    if chave == "bonus":
        return AEstrelaComLimite(grafo, h, inicio, fim).executar(
            limite=limite or 0, verbose=verbose
        )

    raise ValueError(f"Algoritmo desconhecido: '{chave}'")


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def salvar_csv(resultados: list[ResultadoBusca], caminho: str) -> None:
    """Acrescenta resultados ao CSV (cria o arquivo com cabeçalho se não existir)."""
    p = Path(caminho)
    novo = not p.exists()
    with open(caminho, mode="a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_CAMPOS)
        if novo:
            w.writeheader()
        for r in resultados:
            w.writerow({
                "arquivo":            r.arquivo,
                "algoritmo":          r.algoritmo,
                "ponto_inicial":      r.ponto_inicial,
                "ponto_final":        r.ponto_final,
                "solucao_encontrada": r.solucao_encontrada,
                "custo":              r.custo if r.custo is not None else "",
                "caminho":            " – ".join(r.caminho) if r.caminho else "",
                "nos_expandidos":     r.nos_expandidos,
                "iteracoes":          r.iteracoes,
                "tempo_ms":           f"{r.tempo_ms:.3f}",
            })


# ---------------------------------------------------------------------------
# Sumário tabular
# ---------------------------------------------------------------------------

def imprimir_sumario(resultados: list[ResultadoBusca]) -> None:
    sep = "─" * 90
    print(f"\n{sep}")
    print(f"{'ARQUIVO':<22} {'ALGORITMO':<38} {'CUSTO':>7} {'NÓS':>6} {'ITER':>6} {'MS':>9}")
    print(sep)
    for r in resultados:
        custo = str(r.custo) if r.solucao_encontrada else "N/A"
        print(
            f"{r.arquivo:<22} {r.algoritmo[:36]:<38} "
            f"{custo:>7} {r.nos_expandidos:>6} {r.iteracoes:>6} {r.tempo_ms:>9.2f}"
        )
    print(sep)


# ---------------------------------------------------------------------------
# Submenus
# ---------------------------------------------------------------------------

def _submenu_algoritmo() -> Optional[tuple[str, str]]:
    """Exibe opções de algoritmo e retorna (chave, descricao) ou None."""
    print("\n  Escolha o algoritmo:")
    for num, (_, desc) in ALGORITMOS.items():
        print(f"    {num}. {desc}")
    print("    0. Voltar")
    op = _input("  Algoritmo: ")
    if op == "0" or op not in ALGORITMOS:
        return None
    return ALGORITMOS[op]  # (chave, descricao)


def _menu_carregar() -> Optional[dict]:
    """Solicita caminho de um arquivo e retorna o config carregado."""
    caminho = _input("Caminho do arquivo (.txt): ")
    if not caminho:
        return None
    try:
        config = carregar_arquivo(caminho)
        config["_arquivo"] = Path(caminho).name
        print(
            f"\n  Arquivo carregado!\n"
            f"  Início: {config['ponto_inicial']}  →  Fim: {config['ponto_final']}\n"
            f"  Nós: {len(config['grafo'])}  |  "
            f"Orientado: {'Sim' if config['orientado'] else 'Não'}"
        )
        return config
    except FileNotFoundError:
        print(f"  Arquivo não encontrado: '{caminho}'")
    except Exception as e:
        print(f"  Erro ao carregar: {e}")
    return None


def _menu_executar(config: dict, resultados: list[ResultadoBusca]) -> None:
    """Executa um algoritmo no arquivo carregado."""
    par = _submenu_algoritmo()
    if par is None:
        return
    chave, _ = par

    limite: Optional[int] = None
    if chave == "bonus":
        limite = _input_int("  Distância máxima: ")
        if limite is None:
            print("  Valor inválido.")
            return

    resultado = executar_algoritmo(config, chave, verbose=True, limite=limite)
    resultado.arquivo = config.get("_arquivo", "")
    resultados.append(resultado)


def _menu_lote(resultados: list[ResultadoBusca]) -> None:
    """Executa algoritmos em lote sobre todos os .txt de uma pasta."""
    caminho = _input("Caminho da pasta (ou arquivo .txt): ")
    if not caminho:
        return

    p = Path(caminho)
    if p.is_file():
        arquivos = [p]
    elif p.is_dir():
        arquivos = sorted(p.glob("*.txt"))
    else:
        print(f"  Caminho inválido: '{caminho}'")
        return

    if not arquivos:
        print("  Nenhum arquivo .txt encontrado.")
        return

    # Escolha dos algoritmos
    print("\n  Quais algoritmos executar?")
    print("    1. Todos  (A*, DFS, Bônus)")
    print("    2. Apenas A*")
    print("    3. Apenas DFS")
    print("    4. Apenas Bônus")
    op_alg = _input("  Opção: ")

    chaves_mapa = {
        "1": ["astar", "dfs", "bonus"],
        "2": ["astar"],
        "3": ["dfs"],
        "4": ["bonus"],
    }
    chaves = chaves_mapa.get(op_alg)
    if not chaves:
        print("  Opção inválida.")
        return

    limite: Optional[int] = None
    if "bonus" in chaves:
        limite = _input_int("  Distância máxima para o Bônus: ")
        if limite is None:
            print("  Valor inválido.")
            return

    verbose = _confirmar("  Exibir iterações detalhadas?")

    total = len(arquivos) * len(chaves)
    print(f"\n  Iniciando lote: {len(arquivos)} arquivo(s) × {len(chaves)} algoritmo(s) = {total} experimento(s)")
    executados = 0

    for arquivo in arquivos:
        print(f"\n  [Arquivo] {arquivo.name}")
        try:
            config = carregar_arquivo(str(arquivo))
            print(
                f"    Início: {config['ponto_inicial']} → Fim: {config['ponto_final']} | "
                f"Nós: {len(config['grafo'])} | "
                f"Orientado: {'Sim' if config['orientado'] else 'Não'}"
            )
        except Exception as e:
            print(f"    ERRO ao ler: {e}")
            continue

        for chave in chaves:
            executados += 1
            _, desc = next(v for v in ALGORITMOS.values() if v[0] == chave)
            print(f"    [{executados:>3}/{total}] {desc}...", end=" ", flush=True)
            try:
                resultado = executar_algoritmo(config, chave, verbose=verbose, limite=limite)
                resultado.arquivo = arquivo.name
                resultados.append(resultado)
                if resultado.solucao_encontrada:
                    print(f"Custo={resultado.custo} | Nós={resultado.nos_expandidos} | {resultado.tempo_ms:.2f}ms")
                else:
                    print(f"Sem solução | Nós={resultado.nos_expandidos}")
            except Exception as e:
                print(f"ERRO: {e}")

    print(f"\n  Lote concluído. {len(resultados)} resultado(s) acumulado(s).")


def _menu_salvar_csv(resultados: list[ResultadoBusca]) -> None:
    """Salva os resultados acumulados em CSV."""
    if not resultados:
        print("  Nenhum resultado acumulado. Execute algum algoritmo primeiro.")
        return
    nome = _input("Nome do arquivo CSV (Enter = resultados.csv): ") or "resultados.csv"
    salvar_csv(resultados, nome)
    print(f"  Salvo em: {Path(nome).resolve()}")
    imprimir_sumario(resultados)


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------

def menu_interativo() -> None:
    config: Optional[dict] = None
    resultados: list[ResultadoBusca] = []

    while True:
        print(f"\n{'='*54}")
        print("   PROJETO 1 IA — SUPER MARIO WORLD  |  UNIOESTE 2026")
        print(f"{'='*54}")
        print("  1. Carregar arquivo de entrada")
        print("  2. Executar algoritmo no arquivo carregado")
        print("  3. Executar em lote (pasta de arquivos)")
        print("  4. Exibir sumário dos resultados")
        print("  5. Salvar resultados em CSV")
        print("  6. Sair")
        if config:
            print(
                f"\n  Arquivo: {config.get('_arquivo', '?')}"
                f"  |  {config['ponto_inicial']} → {config['ponto_final']}"
                f"  |  {len(resultados)} resultado(s) acumulado(s)"
            )
        print(f"{'='*54}")

        opcao = _input("Opção: ")

        if opcao == "1":
            novo = _menu_carregar()
            if novo:
                config = novo
                resultados.clear()

        elif opcao == "2":
            if config is None:
                print("  Carregue um arquivo primeiro (opção 1).")
            else:
                _menu_executar(config, resultados)

        elif opcao == "3":
            _menu_lote(resultados)

        elif opcao == "4":
            if resultados:
                imprimir_sumario(resultados)
            else:
                print("  Nenhum resultado acumulado ainda.")

        elif opcao == "5":
            _menu_salvar_csv(resultados)

        elif opcao == "6":
            print("  Encerrando. Até logo!")
            break

        else:
            print("  Opção inválida. Digite um número entre 1 e 6.")


if __name__ == "__main__":
    menu_interativo()
