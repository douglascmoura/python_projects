import os
import unicodedata

# ---------------------------------------------------------
# Funções Matemáticas usando *args
# ---------------------------------------------------------
def soma(*args):
    return sum(args)

def subtracao(*args):
    if not args: return 0
    res = args[0]
    for num in args[1:]: 
        res -= num
    return res

def divisao(*args):
    if not args: return 0
    res = args[0]
    for num in args[1:]:
        if num == 0:
            return "Erro: Divisão por zero!"
        res /= num
    return res

def multiplicacao(*args):
    if not args: return 0
    res = args[0]
    for num in args[1:]:
        res *= num
    return res

def exponenciacao(*args):
    if not args: return 0
    res = args[0]
    for num in args[1:]: 
        res **= num
    return res

# ---------------------------------------------------------
# Função Processadora usando *args e **kwargs
# ---------------------------------------------------------
def processar_calculo(funcao_matematica, *args, **kwargs):
    """Executa a função e aplica formatações adicionais via kwargs"""
    resultado = funcao_matematica(*args)
    
    """Se o resultado for um número e o usuário pediu para arredondar via kwargs"""
    if isinstance(resultado, (int, float)) and kwargs.get("arredondar", False):
        casas = kwargs.get("casas_decimais", 2)
        resultado = round(resultado, casas)
        
    return resultado

# ---------------------------------------------------------
# Configuração das Operações
# ---------------------------------------------------------
operacoes = {
    "1": {"nome": "Soma", "func": soma, "aliases": ["+", "soma", "adicao"]},
    "2": {"nome": "Subtração", "func": subtracao, "aliases": ["-", "subtracao", "menos"]},
    "3": {"nome": "Divisão", "func": divisao, "aliases": ["/", "divisao"]},
    "4": {"nome": "Multiplicação", "func": multiplicacao, "aliases": ["*", "multiplicacao", "vezes"]},
    "5": {"nome": "Exponenciação", "func": exponenciacao, "aliases": ["^", "**", "exponenciacao", "potencia"]}
}

def normalizar_texto(texto):
    """Remove acentos e deixa tudo minúsculo para facilitar a comparação"""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.strip().lower()

def identificar_operacao(entrada_usuario):
    """Verifica se a entrada bate com a chave, símbolo ou nome da operação"""
    entrada_norm = normalizar_texto(entrada_usuario)
    
    if entrada_norm in operacoes:
        return entrada_norm
        
    for chave, dados in operacoes.items():
        if entrada_norm in dados["aliases"]:
            return chave
    return None

# ---------------------------------------------------------
# Loop Principal da Calculadora
# ---------------------------------------------------------
ultimo_resultado = None

while True:
    # Limpa a tela
    os.system("cls" if os.name == "nt" else "clear")

    print("="*14 + "**"*2 + "="*14)
    if ultimo_resultado is not None:
        print(f" Histórico -> Último Resultado: {ultimo_resultado}")
        print("="*14 + "**"*2 + "="*14)

    # Exibe menu
    for chave, dados in operacoes.items():
        print(f"{chave} : {dados['nome']}")
    print("")
    
    # 1. Validação da Operação
    print("Escolha uma operação (Digite o número, símbolo ou nome):")
    op_input = input("> ")
    op_chave = identificar_operacao(op_input)

    if not op_chave:
        input("\n[!] Operação inválida! Pressione ENTER para tentar novamente.")
        continue

    op_dados = operacoes[op_chave]
    print(f"\nTrabalhando com: {op_dados['nome']}")

    # 2. Entrada de múltiplos argumentos e proteção contra Strings
    print("\nDigite os valores separados por espaço (ex: 10 5 2.5):")
    valores_str = input("> ").split()

    if not valores_str:
        input("\n[!] Nenhum valor digitado! Pressione ENTER para recomeçar.")
        continue

    valores_numericos = []
    erro_conversao = False
    
    for v in valores_str:
        try:
            # Substitui vírgula por ponto para evitar erros em padrão brasileiro
            valores_numericos.append(float(v.replace(',', '.')))
        except ValueError:
            erro_conversao = True
            break

    if erro_conversao:
        input("\n[AVISO] Você inseriu um texto ou caractere inválido. Por favor, insira apenas números. Pressione ENTER para recomeçar.")
        continue

    # 3. Execução usando *args e **kwargs
    resultado_atual = processar_calculo(
        op_dados["func"], 
        *valores_numericos, 
        arredondar=True, 
        casas_decimais=4
    )
    
    ultimo_resultado = resultado_atual

    # Pegamos o primeiro alias da operação, que configuramos para ser o símbolo (+, -, *, /, ^)
    simbolo_op = op_dados["aliases"][0] 
    
    # Formatamos os números para tirar o ".0" caso sejam inteiros, deixando a leitura mais limpa
    valores_formatados = [str(int(v)) if v.is_integer() else str(v) for v in valores_numericos]
    
    # Unimos os valores usando o símbolo da operação com espaços ao redor
    expressao_montada = f" {simbolo_op} ".join(valores_formatados)
    # --------------------------------------

    print("")
    print("="*14 + "**"*2 + "="*14)
    print("")
    print(f"EXPRESSÃO: {expressao_montada}")
    print("")
    print("="*14 + "**"*2 + "="*14)
    print(f"RESULTADO: {resultado_atual}")
    print("="*14 + "**"*2 + "="*14)
    print("")

    # 4. Verificação de Encerramento melhorada
    sair = False
    while True:
        print("Deseja fazer mais alguma operação?")
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
        print("\nEncerrando a calculadora. Até logo!")
        break





