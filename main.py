import sys
import heapq
import csv
import os

grafo = {}
heuristicas = {}
ponto_inicial = None
ponto_final = None
orientado = False
nome_arquivo_atual = "vazio"

def salvar_resultados(algoritmo, iteracoes, expandidos, gerados):
    global nome_arquivo_atual
    nome_csv = "resultados.csv"
    arquivo_existe = os.path.isfile(nome_csv)

    with open(nome_csv, mode='a', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo,delimiter=';')

        if not arquivo_existe:
            escritor.writerow(['Arquito .TXT', 'Algoritmo', 'Iterações', 'Nós Expandidos', 'Nós Gerados'])

        escritor.writerow([nome_arquivo_atual,algoritmo,iteracoes,expandidos,gerados])

def carregar_arquivo():
    global grafo, heuristicas, ponto_inicial, ponto_final, orientado,nome_arquivo_atual
    grafo = {}
    heuristicas = {}

    print("\n--- Carregando Arquivo ---")
    nome_arquivo = input("Digite o nome do arquivo (ex: teste.txt): ")
    
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines() #lê as linhas e guarda em uma lista

            nome_arquivo_atual = nome_arquivo
            
            for linha in linhas:
                #strip() remove os espaços em branco do início e do fim de uma string.
                linha_limpa = linha.split('%')[0].strip().lower()
            
                if not linha_limpa: #se ficar vazia
                    continue
                
                inicio = linha_limpa.find('(')
                fim = linha_limpa.find(')')

                conteudo = linha_limpa[inicio + 1 : fim].replace(" ", "")

                if linha_limpa.startswith("ponto_inicial"):
                    ponto_inicial = conteudo
                elif linha_limpa.startswith("ponto_final"):
                    ponto_final = conteudo
                elif linha_limpa.startswith("orientado"):
                    orientado = (conteudo == 's')
                elif linha_limpa.startswith("pode_ir"):
                    divisao = conteudo.split(',')
                    origem = divisao[0]
                    destino = divisao[1]
                    custo = int(divisao[2])

                    if origem not in grafo:
                        grafo[origem] = {}
                    
                    grafo[origem][destino] = custo

                    if not orientado:
                        if destino not in grafo:
                            grafo[destino] = {}
                        grafo[destino][origem] = custo

                elif linha_limpa.startswith("h"):
                    divisao = conteudo.split(',')
                    no_atual = divisao[0]
                    valor_h = int(divisao[2])
                    heuristicas[no_atual] = valor_h
        
            print(f"\nSucesso! Arquivo '{nome_arquivo}' lido e estruturado na memória.")
            print(f"\nPonto Inicial: {ponto_inicial} e Ponto Final: {ponto_final} | Orientado: {'Sim' if orientado else 'Não'}")

            
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado no diretório atual.")

def executar_a_estrela():
    global grafo, heuristicas, ponto_inicial, ponto_final

    if not ponto_inicial or not ponto_final:
        print("\nErro! Carregue um arquivo antes de executar o algoritmo.")
        return
    print("\n--- Executando A* ---")

    if ponto_inicial == ponto_final:
        print("Ponto inicial é o destino.")
        return

    fronteira = []
    id = 0
    nos_gerados = 1
    nos_expandidos = 1
    melhor_g = {ponto_inicial : 0}

    for vizinho, aresta in grafo.get(ponto_inicial, {}).items():
        g_vizinho = aresta
        f_vizinho = g_vizinho + heuristicas.get(vizinho, 0)
        melhor_g[vizinho] = g_vizinho

        caminho_inicial = [ponto_inicial, vizinho]
        id += 1
        heapq.heappush(fronteira, (f_vizinho, id, vizinho, g_vizinho,caminho_inicial))
        nos_gerados += 1
    

    iteracao = 1
    sucesso = False

    while fronteira:
        itens_lista = [f"({no}: {g}+{heuristicas.get(no, 0)}={f})" for f, _, no,g, _ in sorted(fronteira)]
        str_lista = " ".join(itens_lista)

        print(f"\nIteração {iteracao}:")
        print(f"Pilha: {str_lista}")
        print(f"Nós expandidos: {nos_expandidos}")
        print(f"Nós gerados: {nos_gerados}")

        f_atual, _, atual, g_atual, caminho = heapq.heappop(fronteira)
        

        if atual == ponto_final:
            sucesso = True
            break

        
        vizinhos = grafo.get(atual, {})
        nos_expandidos += 1

        for vizinho, aresta in vizinhos.items():
            novo_g = g_atual + aresta

            if vizinho not in melhor_g or novo_g < melhor_g[vizinho]:
                melhor_g[vizinho] = novo_g
                f_vizinho = novo_g + heuristicas.get(vizinho, 0) 

                novo_caminho = list(caminho)
                novo_caminho.append(vizinho)

                id+=1
                heapq.heappush(fronteira, (f_vizinho, id,vizinho, novo_g, novo_caminho))
                nos_gerados += 1

        iteracao += 1
    

    print("\n" + "="*30)
    print("Fim da execução")
    if sucesso:
        print(f"Distância: {g_atual}")
        print(f"Caminho: {' - '.join(caminho)}")
    else:
        print("Distância: Incompleta")
        print("Caminho: Nenhum caminho válido encontrado até o destino.")

    print(f"Nós Expandidos: {nos_expandidos}")
    print(f"Nós gerados: {nos_gerados}")
    salvar_resultados('A_estrela',iteracao, nos_expandidos, nos_gerados)
    print("="*30)
    

def executar_busca_profundidade_backtracking():
    global grafo, ponto_inicial, ponto_final

    if not ponto_inicial or not ponto_final:
        print("\nErro! Carregue um arquivo antes de executar o algoritmo.")
        return
    print("\n--- Executando Busca em Profundidade com Backtracking ---")

    if ponto_inicial == ponto_final:
        print("\nPonto inicial é o ponto final.")
        return
    
    fronteira = [] #tupla: (nó_atual, distancia_acumulada, caminho_ate_aqui)
    
    visitados = set()
    
    iteracao = 1
    nos_expandidos = 1
    nos_gerados = 1
    sucesso = False
    distancia_final = 0
    caminho_final = []

    visitados.add(ponto_inicial)

    vizinhos = grafo.get(ponto_inicial, {})

    vizinhos_validos = [v for v in vizinhos.keys()]
    vizinhos_validos.reverse()

    for vizinho in vizinhos_validos:
        aresta = vizinhos[vizinho]
        caminho_inicial = [ponto_inicial, vizinho]

        fronteira.append((vizinho, aresta, caminho_inicial))
        nos_gerados += 1

    while fronteira:
        itens_lista = [f"({no}: {dist} + 0 = {dist})" for no, dist, _ in fronteira]
        str_lista = " ".join(itens_lista)

        print(f"\nIteração {iteracao}")
        print(f"Pilha: {str_lista}")
        print(f"Nós expandidos: {nos_expandidos}")
        print(f"Nós gerados: {nos_gerados}")

        atual, distancia, caminho = fronteira.pop()
        

        if atual == ponto_final:
            sucesso = True
            distancia_final = distancia
            caminho_final = caminho
            break

        if atual not in visitados:
            visitados.add(atual)
            nos_expandidos +=1
            vizinhos = grafo.get(atual, {})
            vizinhos_validos = [v for v in vizinhos.keys() if v not in visitados]
            vizinhos_validos.reverse()

            for vizinho in vizinhos_validos:
                aresta = vizinhos[vizinho]
                nova_distancia = distancia + aresta

                novo_caminho = list(caminho)
                novo_caminho.append(vizinho)

                fronteira.append((vizinho, nova_distancia, novo_caminho))
                nos_gerados += 1

        iteracao += 1

    print("\n" + "="*30)
    print("Fim da execução")
    if sucesso:
        print(f"Distância: {distancia_final}")
        print(f"Caminho: {' - '.join(caminho_final)}")
        print(f"Quantidade de iterações: {iteracao}")
        print(f"Medida de desempenho (Nós Expandidos): {nos_expandidos}")
        print(f"Medida de desempenho (Nós Gerados): {nos_gerados}")
    else:
        print("Distância: Incompleta")
        print("Nenhum caminho válido encontrado até ao destino.")
        
    salvar_resultados('DFS-backtracking',iteracao, nos_expandidos, nos_gerados)
    print("="*30)


def executar_a_estrela_limitado():
    global grafo, heuristicas, ponto_inicial,ponto_final, nome_arquivo_atual

    if not ponto_inicial or not ponto_final:
        print("\nErro! Carregue um arquivo antes de executar o algoritmo.")
        return
    print("\n--- Executando A* Limitado---")
    print("\nInício da execução")
    print("Qual a distância máxima?")

    try:
        limite = int(input())
    except ValueError:
        print("\nPor favor, digite um número inteiro.")
        return
    
    if ponto_inicial == ponto_final:
        print("\nO ponto inicial é igual ao destino!")
        return
    
    f_inicial = heuristicas.get(ponto_inicial, 0)
    if f_inicial > limite:
        print(f"\nA distância mínima em linha reta ({f_inicial}) do nó inicial até o destino já excede o limite ({limite}).")
        print("\n" + "="*30)
        print("Fim da execução")
        print("Distância: Incompleta")
        print("Caminho: Nenhum caminho válido encontrado até o destino.")
        print("Nós expandidos: 0")
        print("Nós gerados: 1")
        salvar_resultados('A_estrela_limitado', 0, 0, 1)
        print("="*30)
        return

    fronteira = []
    id = 0
    nos_gerados = 1
    nos_expandidos = 1
    melhor_g = {ponto_inicial: 0}

    for vizinho, aresta in grafo.get(ponto_inicial, {}).items():
        g_vizinho = aresta
        f_vizinho = g_vizinho + heuristicas.get(vizinho, 0)
        melhor_g[vizinho] = g_vizinho
        caminho_inicial = [ponto_inicial,vizinho]
        id += 1
        heapq.heappush(fronteira, (f_vizinho, id, vizinho, g_vizinho,caminho_inicial))
        nos_gerados += 1
    
    
    iteracao = 1
    sucesso = False
    g_anterior = 0  

    while fronteira:
        itens_lista = [f"({no}: {g} + {heuristicas.get(no, 0)} = {f})" for f, _, no,g, _ in sorted(fronteira)]
        str_lista = " ".join(itens_lista)

        
        distancia_disponivel = limite - g_anterior

        print(f"\nIteração {iteracao}:")
        print(f"Pilha: {str_lista}")
        print(f"nós expandidos: {nos_expandidos}")
        print(f"Nós gerados: {nos_gerados}")
        print(f"Distância disponível: {distancia_disponivel}")

        f_atual, _, atual, g_atual, caminho = heapq.heappop(fronteira)

        if f_atual > limite:
            print("Caminho descartado (excede o limite)\n")
            iteracao += 1
            continue

        if atual == ponto_final:
            sucesso = True
            break

        vizinhos = grafo.get(atual, {})
        nos_expandidos += 1

        for vizinho, aresta in vizinhos.items():
            novo_g = g_atual + aresta
            f_vizinho = novo_g + heuristicas.get(vizinho, 0)

            if vizinho not in melhor_g or novo_g < melhor_g[vizinho]:
                melhor_g[vizinho] = novo_g

                novo_caminho = list(caminho)
                novo_caminho.append(vizinho)

                id+=1
                heapq.heappush(fronteira, (f_vizinho, id,vizinho, novo_g, novo_caminho))
                nos_gerados += 1

        g_anterior = g_atual
        iteracao += 1
    

    print("\n" + "="*30)
    print("Fim da execução")
    if sucesso:
        print(f"Distância: {g_atual}")
        print(f"Caminho: {' - '.join(caminho)}")
    else:
        print("Distância: Incompleta")
        print("Caminho: Nenhum caminho válido encontrado até o destino.")

    print(f"Nós expandidos: {nos_expandidos}")
    print(f"Nós gerados: {nos_gerados}")
    salvar_resultados('A_estrela_limitado',iteracao, nos_expandidos, nos_gerados)
    print("="*30)


        

def exibir_menu():
    while True:
        print("\n" + "="*40)
        print(" PROJETO 1 IA - SUPER MARIO WORLD")
        print("="*40)
        print("1. Carregar arquivo")
        print("2. Executar Busca em Profundidade com backtracking")
        print("3. Executar A*")
        print("4. BÔNUS - Executar A* Limitado")
        print("5. Sair")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            carregar_arquivo()
        elif opcao == '2':
            executar_busca_profundidade_backtracking()
        elif opcao == '3':
            executar_a_estrela()
        elif opcao == '4':
            executar_a_estrela_limitado()
        elif opcao == '5':
            print("\nEncerrando o programa. Até logo!")
            sys.exit()
        else:
            print("\nOpção inválida! Digite um número de 1 a 5.")

if __name__ == "__main__":
    exibir_menu()