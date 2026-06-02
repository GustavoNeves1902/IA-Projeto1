import sys
import heapq

grafo = {}
heuristicas = {}
ponto_inicial = None
ponto_final = None
orientado = False

def carregar_arquivo():
    global grafo, heuristicas, ponto_inicial, ponto_final, orientado
    grafo = {}
    heuristicas = {}

    print("\n--- Carregando Arquivo ---")
    nome_arquivo = input("Digite o nome do arquivo (ex: teste.txt): ")
    
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines() #lê as linhas e guarda em uma lista
            
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

    fronteira = []
    id = 0
    g_inicial = 0
    nos_gerados = 1
    h_inicial = heuristicas.get(ponto_inicial,0)
    f_inicial = g_inicial + h_inicial
    caminho_inicial = [ponto_inicial]

    heapq.heappush(fronteira, (f_inicial, id, ponto_inicial, g_inicial,caminho_inicial))
    
    melhor_g = {ponto_inicial: g_inicial}

    iteracao = 1
    nos_expandidos = 0
    sucesso = False

    while fronteira:
        itens_lista = [f"({no}: {g}+{heuristicas.get(no, 0)}={f})" for f, _, no,g, _ in sorted(fronteira)]
        str_lista = " ".join(itens_lista)

        print(f"\nIteração {iteracao}:")
        print(f"Lista: {str_lista}")
        print(f"Medida de desempenho: {nos_expandidos}")

        f_atual, _, atual, g_atual, caminho = heapq.heappop(fronteira)
        nos_expandidos += 1

        if atual == ponto_final:
            sucesso = True
            break
        
        vizinhos = grafo.get(atual, {})

        for vizinho, custo_aresta in vizinhos.items():
            novo_g = g_atual + custo_aresta

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
        print(f"Medida de desempenho (Nós Expandidos): {nos_expandidos}")
        print(f"Medida de desempenho (Nós Gerados): {nos_gerados}")
    else:
        print("Distância: Incompleta")
        print("Caminho: Nenhum caminho válido encontrado até o destino.")
        print(f"Medida de desempenho (Nós Expandidos): {nos_expandidos}")
        print(f"Medida de desempenho (Nós Gerados): {nos_gerados}")
    print("="*30)
    

def executar_busca_profundidade_backtracking():
    global grafo, ponto_inicial, ponto_final

    if not ponto_inicial or not ponto_final:
        print("\nErro! Carregue um arquivo antes de executar o algoritmo.")
        return
    print("\n--- Executando Busca em Profundidade com Backtracking ---")
    
    fronteira = [(ponto_inicial, 0 , [ponto_inicial])] #tupla: (nó_atual, distancia_acumulada, caminho_ate_aqui)
    
    visitados = set()
    
    iteracao = 1
    nos_expandidos = 0
    nos_gerados = 1
    sucesso = False
    distancia_final = 0
    caminho_final = []

    while fronteira:
        itens_lista = [f"({no}: {dist} + 0 = {dist})" for no, dist, _ in fronteira]
        str_lista = " ".join(itens_lista)

        print(f"\nIteração {iteracao}")
        print(f"Lista: {str_lista}")
        print(f"Medida de desempenho: {nos_expandidos}")

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
                custo_aresta = vizinhos[vizinho]
                nova_distancia = distancia + custo_aresta

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
        print(f"Medida de desempenho (Nós Expandidos): {nos_expandidos}")
        print(f"Medida de desempenho (Nós Gerados): {nos_gerados}")
    else:
        print("Distância: Incompleta")
        print("Caminho: Nenhum caminho válido encontrado até ao destino.")
        print(f"Medida de desempenho (Nós Expandidos): {nos_expandidos}")
        print(f"Medida de desempenho (Nós Gerados): {nos_gerados}")
    print("="*30)

        

def exibir_menu():
    while True:
        print("\n" + "="*40)
        print(" PROJETO 1 IA - SUPER MARIO WORLD")
        print("="*40)
        print("1. Carregar arquivo")
        print("2. Executar A*")
        print("3. Executar Busca em Profundidade com backtracking")
        print("4. Sair")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            carregar_arquivo()
        elif opcao == '2':
            executar_a_estrela()
        elif opcao == '3':
            executar_busca_profundidade_backtracking()
        elif opcao == '4':
            print("\nEncerrando o programa. Até logo!")
            sys.exit()
        else:
            print("\nOpção inválida! Digite um número de 1 a 4.")

if __name__ == "__main__":
    exibir_menu()