import os
import random
import unicodedata

# ---------------------------------------------------------
# Funções de Suporte
# ---------------------------------------------------------
def normalizar_texto(texto):
    """Remove acentos e deixa tudo minúsculo para facilitar a comparação"""
    texto = unicodedata.normalize('NFD', str(texto))
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.strip().lower()

# ---------------------------------------------------------
# Configuração do Jogo
# ---------------------------------------------------------
# Dicionário de opções com emojis e aliases (apelidos) aceitos
opcoes = {
    "1": {"nome": "Pedra", "emoji": "🪨", "aliases": ["1", "pedra"]},
    "2": {"nome": "Papel", "emoji": "📄", "aliases": ["2", "papel"]},
    "3": {"nome": "Tesoura", "emoji": "✂️", "aliases": ["3", "tesoura"]}
}

# Dicionário de regras (Quem vence de quem? A Chave vence o Valor)
regras_vitoria = {
    "Pedra": "Tesoura",
    "Papel": "Pedra",
    "Tesoura": "Papel"
}

def identificar_jogada(entrada_usuario):
    """Verifica se a entrada bate com o número ou nome da jogada"""
    entrada_norm = normalizar_texto(entrada_usuario)
    for chave, dados in opcoes.items():
        if entrada_norm in dados["aliases"]:
            return chave # Retorna a chave (1, 2 ou 3)
    return None

def determinar_vencedor(jogada_player, jogada_computer):
    """Compara as jogadas e retorna o resultado"""
    nome_player = opcoes[jogada_player]["nome"]
    nome_computer = opcoes[jogada_computer]["nome"]

    if nome_player == nome_computer:
        return "empate"
    elif regras_vitoria[nome_player] == nome_computer:
        return "jogador"
    else:
        return "computador"

# ---------------------------------------------------------
# Loop Principal do Jogo
# ---------------------------------------------------------
placar_player = 0
placar_computer = 0
placar_empate = 0

while True:
    # Limpa a tela
    os.system("cls" if os.name == "nt" else "clear")

    print("=="*12 + "**"*2 + "=="*12)
    print("")
    print(" - PEDRA - 🪨 - PAPEL - 📄 - TESOURA - ✂️ - ")
    print("")
    print("=="*12 + "**"*2 + "=="*12)
    
    # Exibe o Placar
    print(f"\n🏆 PLACAR -> Você: {placar_player} | Computador: {placar_computer} | Empates: {placar_empate}\n")

    # Exibe o Menu
    for chave, dados in opcoes.items():
        print(f"[{chave}] {dados['nome']} {dados['emoji']}")

    # 1. Entrada do Jogador
    print("\nEscolha sua jogada (Digite o número ou o nome): ")
    escolha_input = input("> ")
    jogada_player = identificar_jogada(escolha_input)

    if not jogada_player:
        input("\n[!] Jogada inválida! Pressione ENTER para tentar novamente.")
        continue

    # 2. Jogada do Computador
    jogada_computer = random.choice(list(opcoes.keys()))

    # 3. Determina o Vencedor
    resultado = determinar_vencedor(jogada_player, jogada_computer)

    # 4. Atualiza o Placar e define a mensagem
    if resultado == "empate":
        placar_empate += 1
        mensagem_resultado = "Deu EMPATE! 😐"
    elif resultado == "jogador":
        placar_player += 1
        mensagem_resultado = "VOCÊ GANHOU! 🎉🎉🎉"
    else:
        placar_computer += 1
        mensagem_resultado = "VOCÊ PERDEU! 💀💀💀"

    # 5. Exibe os Resultados
    emoji_p = opcoes[jogada_player]['emoji']
    emoji_c = opcoes[jogada_computer]['emoji']
    nome_p = opcoes[jogada_player]['nome']
    nome_c = opcoes[jogada_computer]['nome']

    print("\n" + "="*20 + "**"*2 + "="*20)
    print(f"🥊 VOCÊ: {nome_p} {emoji_p}  VS  {emoji_c}  {nome_c} :COMPUTADOR")
    print(f"RESULTADO: {mensagem_resultado}")
    print("="*20 + "**"*2 + "="*20 + "\n")

    # 6. Verificação de Encerramento
    sair = False
    while True:
        print("Deseja jogar novamente?")
        print(" -> Digite '1', 'sair' ou 'leave' para ENCERRAR.")
        print(" -> Digite '2', 'continuar' ou 'next' para CONTINUAR.")
        
        comando = normalizar_texto(input("> "))
        
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
        print(f"Placar Final -> Você: {placar_player} | PC: {placar_computer}")
        print("="*32 + "\n")
        break