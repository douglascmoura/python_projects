import os

# ---------------------------------------------------------
# Funções de Suporte do Jogo
# ---------------------------------------------------------
def imprimir_painel(painel):
    """Desenha o jogo da velha na tela de forma amigável"""
    print("\n")
    for i, linha in enumerate(painel):
        print(f"   {linha[0]}  |  {linha[1]}  |  {linha[2]} ")
        if i < 2:
            print(" ----- ----- -----")
    print("\n")

def mapear_jogada(numero):
    """Transforma um número de 1 a 9 em coordenadas (linha, coluna) da matriz"""
    numero -= 1 
    linha = numero // 3
    coluna = numero % 3
    return linha, coluna

def verificar_vencedor(painel, simbolo):
    """Verifica se o símbolo atual fechou uma linha, coluna ou diagonal"""
    for i in range(3):
        if painel[i][0] == painel[i][1] == painel[i][2] == simbolo: return True
    for j in range(3):
        if painel[0][j] == painel[1][j] == painel[2][j] == simbolo: return True
    if painel[0][0] == painel[1][1] == painel[2][2] == simbolo: return True
    if painel[0][2] == painel[1][1] == painel[2][0] == simbolo: return True
    return False

# ---------------------------------------------------------
# Configuração Inicial (Nomes e Placar)
# ---------------------------------------------------------
os.system("cls" if os.name == "nt" else "clear")
print("=="*5 + " BEM-VINDO AO JOGO DA VELHA " + "=="*5)

# Pede os nomes. O uso do 'or' garante que, se a string for vazia, ele pega o valor à direita.
print("\nDigite o nome do Jogador 1 (❎ ) [Pressione ENTER para 'Jogador 1']:")
nome_p1 = input("> ").strip() or "Jogador 1"

print("\nDigite o nome do Jogador 2 (⭕ ) [Pressione ENTER para 'Jogador 2']:")
nome_p2 = input("> ").strip() or "Jogador 2"

# Inicializa o placar geral
placar_p1 = 0
placar_p2 = 0
placar_empate = 0

# ---------------------------------------------------------
# Loop Principal (Permite jogar várias partidas)
# ---------------------------------------------------------
while True:
    painel = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    rodada = 1
    vencedor = None
    
    # Loop da Partida atual (máximo de 9 rodadas)
    while rodada <= 9:
        os.system("cls" if os.name == "nt" else "clear")
        
        print("=="*6 + " JOGO DA VELHA " + "=="*6)
        # Exibe o Placar Atualizado no topo da tela
        print(f"🏆 PLACAR -> {nome_p1} (❎ ): {placar_p1} | {nome_p2} (⭕ ): {placar_p2} | Empates: {placar_empate}")
        
        imprimir_painel(painel)
        
        # Define de quem é a vez
        jogador_atual = "❎ " if rodada % 2 != 0 else "⭕ "
        nome_jogador = nome_p1 if jogador_atual == "❎ " else nome_p2
        
        print(f"Vez de {nome_jogador} ({jogador_atual})")
        print("Escolha uma posição disponível (1-9):")
        
        entrada = input("> ").strip()
        
        # Validações
        if not entrada.isdigit() or not (1 <= int(entrada) <= 9):
            input("\n[!] Entrada inválida! Digite um número de 1 a 9. Pressione ENTER.")
            continue
            
        numero_jogado = int(entrada)
        linha, coluna = mapear_jogada(numero_jogado)
        
        if painel[linha][coluna] in ["❎ ", "⭕ "]:
            input("\n[!] Essa posição já está ocupada! Escolha outra. Pressione ENTER.")
            continue
            
        # Registra a jogada
        painel[linha][coluna] = jogador_atual
        
        # Verifica se houve vitória nesta jogada
        if verificar_vencedor(painel, jogador_atual):
            vencedor = nome_jogador
            # Atualiza o placar do vencedor
            if jogador_atual == "❎ ":
                placar_p1 += 1
            else:
                placar_p2 += 1
            break 
            
        rodada += 1

    # Se a partida acabar (sair do loop) e a variável vencedor continuar 'None', foi empate
    if not vencedor:
        placar_empate += 1

    # Fim da partida: Limpa a tela e mostra o resultado final
    os.system("cls" if os.name == "nt" else "clear")
    print("=="*6 + " FIM DE JOGO " + "=="*6)
    imprimir_painel(painel)
    
    if vencedor:
        print(f"🏆 PARABÉNS! {vencedor} VENCEU a partida! 🏆")
    else:
        print("😐 DEU VELHA! A partida terminou em empate. 😐")
        
    print("=="*21 + "\n")

    # ---------------------------------------------------------
    # Verificação de Encerramento
    # ---------------------------------------------------------
    sair = False
    while True:
        print("Deseja jogar novamente?")
        print(" -> Digite '1' para ENCERRAR.")
        print(" -> Digite '2' para CONTINUAR.")
        
        comando = input("> ").strip().lower()
        
        if comando in ['1', 'sair', 'leave']:
            sair = True
            break
        elif comando in ['2', 'continuar', 'next']:
            break
        else:
            print("[!] Comando não reconhecido. Tente novamente.\n")

    if sair:
        print("\n" + "="*32)
        print("🏁 FIM DE JOGO 🏁")
        print(f"Placar Final -> {nome_p1}: {placar_p1} | {nome_p2}: {placar_p2} | Empates: {placar_empate}")
        print("="*32 + "\n")
        break