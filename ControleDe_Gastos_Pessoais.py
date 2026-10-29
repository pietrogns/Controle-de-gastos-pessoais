import json
import os
from datetime import datetime

# O arquivo JSON fica na mesma pasta do programa
ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "movimentacoes.json")
FORMATO_DATA = "%d/%m/%Y %H:%M"


#Funções apenas para o arquivo JSON
def carregar_dados():
    """Carrega as movimentações do arquivo JSON. Cria o arquivo se não existir."""
    if not os.path.exists(ARQUIVO):
        salvar_dados([])
        print("Arquivo de dados não encontrado. Um novo arquivo foi criado.")
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, list):
            raise ValueError("Formato inválido")
        return dados
    except (json.JSONDecodeError, ValueError):
        print("Erro: o arquivo de dados está corrompido. Iniciando com lista vazia.")
        return []


def salvar_dados(movimentacoes):
    """Salva a lista de movimentações no arquivo JSON."""
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(movimentacoes, arquivo, ensure_ascii=False, indent=4)


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def gerar_id(movimentacoes):
    """Gera um novo identificador numérico (maior id existente + 1)."""
    if not movimentacoes:
        return 1
    return max(mov["id"] for mov in movimentacoes) + 1


def formatar_moeda(valor):
    """Formata um número no padrão brasileiro: R$ 1.234,56"""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def ler_descricao():
    """Lê a descrição, não permitindo texto vazio."""
    while True:
        descricao = input("Descrição: ").strip()
        if descricao:
            return descricao
        print("Erro: a descrição não pode ficar vazia.")


def ler_valor():
    """Lê o valor, aceitando vírgula ou ponto e rejeitando valores <= 0."""
    while True:
        entrada = input("Valor (R$): ").strip().replace(",", ".")
        try:
            valor = float(entrada)
        except ValueError:
            print("Erro: digite um número válido (ex.: 150.50).")
            continue

        if valor <= 0:
            print("Erro: o valor deve ser maior que zero.")
        else:
            return round(valor, 2)


def ler_data():
    """
    Lê a data/hora da movimentação.
    Se o usuário apenas pressionar Enter, usa a data e hora atuais.
    """
    while True:
        entrada = input("Data/Hora (dd/mm/aaaa hh:mm) [Enter = agora]: ").strip()
        if entrada == "":
            return datetime.now().strftime(FORMATO_DATA)
        try:
            data = datetime.strptime(entrada, FORMATO_DATA)
            return data.strftime(FORMATO_DATA)
        except ValueError:
            print("Erro: formato inválido. Use dd/mm/aaaa hh:mm (ex.: 30/09/2026 20:44).")


def calcular_totais(movimentacoes):
    """Retorna (total_receitas, total_despesas, saldo)."""
    total_receitas = 0.0
    total_despesas = 0.0

    for mov in movimentacoes:
        if mov["tipo"] == "Receita":
            total_receitas += mov["valor"]
        elif mov["tipo"] == "Despesa":
            total_despesas += mov["valor"]

    saldo = total_receitas - total_despesas
    return total_receitas, total_despesas, saldo


# ---------------------------------------------------------------------------
# Operações do menu
# ---------------------------------------------------------------------------
def adicionar_movimentacao(movimentacoes, tipo):
    """Adiciona uma receita ou despesa e salva no arquivo."""
    print(f"\n--- Adicionar {tipo} ---")
    descricao = ler_descricao()
    valor = ler_valor()
    data = ler_data()

    movimentacao = {
        "id": gerar_id(movimentacoes),
        "descricao": descricao,
        "valor": valor,
        "tipo": tipo,
        "data": data,
    }

    movimentacoes.append(movimentacao)
    salvar_dados(movimentacoes)
    print(f"\n{tipo} '{descricao}' de {formatar_moeda(valor)} "
          f"registrada com sucesso (ID {movimentacao['id']})!")


def listar_movimentacoes(movimentacoes):
    """Exibe todas as movimentações cadastradas."""
    print("\n--- Movimentações ---")
    if not movimentacoes:
        print("Nenhuma movimentação cadastrada.")
        return

    print(f"{'ID':<5}{'Data':<18}{'Tipo':<10}{'Valor':>16}  Descrição")
    print("-" * 70)
    for mov in movimentacoes:
        sinal = "+" if mov["tipo"] == "Receita" else "-"
        valor = f"{sinal} {formatar_moeda(mov['valor'])}"
        print(f"{mov['id']:<5}{mov['data']:<18}{mov['tipo']:<10}{valor:>16}  {mov['descricao']}")
    print("-" * 70)
    print(f"Total de movimentações: {len(movimentacoes)}")


def consultar_saldo(movimentacoes):
    """Exibe o saldo atual."""
    _, _, saldo = calcular_totais(movimentacoes)
    print("\n--- Saldo ---")
    print(f"Saldo disponível: {formatar_moeda(saldo)}")
    if saldo < 0:
        print("Atenção: seu saldo está negativo!")


def excluir_movimentacao(movimentacoes):
    """Exclui uma movimentação a partir do seu ID."""
    print("\n--- Excluir Movimentação ---")
    if not movimentacoes:
        print("Nenhuma movimentação cadastrada para excluir.")
        return

    listar_movimentacoes(movimentacoes)

    entrada = input("\nDigite o ID da movimentação a excluir: ").strip()
    if not entrada.isdigit():
        print("Erro: o ID deve ser um número inteiro positivo.")
        return

    id_excluir = int(entrada)
    for mov in movimentacoes:
        if mov["id"] == id_excluir:
            confirmacao = input(
                f"Confirma a exclusão de '{mov['descricao']}' "
                f"({formatar_moeda(mov['valor'])})? (s/n): "
            ).strip().lower()
            if confirmacao == "s":
                movimentacoes.remove(mov)
                salvar_dados(movimentacoes)
                print("Movimentação excluída com sucesso!")
            else:
                print("Exclusão cancelada.")
            return

    print(f"Erro: nenhuma movimentação encontrada com o ID {id_excluir}.")


def gerar_relatorio(movimentacoes):
    """Exibe um relatório financeiro resumido."""
    total_receitas, total_despesas, saldo = calcular_totais(movimentacoes)

    print("\n" + "=" * 40)
    print("        RELATÓRIO FINANCEIRO")
    print("=" * 40)
    print(f"Total de receitas : {formatar_moeda(total_receitas)}")
    print(f"Total de despesas : {formatar_moeda(total_despesas)}")
    print(f"Saldo atual       : {formatar_moeda(saldo)}")
    print(f"Movimentações     : {len(movimentacoes)}")
    print("=" * 40)


# ---------------------------------------------------------------------------
# Menu e programa principal
# ---------------------------------------------------------------------------
def exibir_menu():
    print("\n" + "=" * 40)
    print("   CONTROLE FINANCEIRO PESSOAL")
    print("=" * 40)
    print("1 - Adicionar Receita")
    print("2 - Adicionar Despesa")
    print("3 - Listar Movimentações")
    print("4 - Consultar Saldo")
    print("5 - Excluir Movimentação")
    print("6 - Gerar Relatório")
    print("7 - Sair")
    print("=" * 40)


def main():
    movimentacoes = carregar_dados()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            adicionar_movimentacao(movimentacoes, "Receita")
        elif opcao == "2":
            adicionar_movimentacao(movimentacoes, "Despesa")
        elif opcao == "3":
            listar_movimentacoes(movimentacoes)
        elif opcao == "4":
            consultar_saldo(movimentacoes)
        elif opcao == "5":
            excluir_movimentacao(movimentacoes)
        elif opcao == "6":
            gerar_relatorio(movimentacoes)
        elif opcao == "7":
            print("\nDados salvos. Encerrando o programa. Até logo!")
            break
        else:
            print("\nErro: opção inválida! Escolha um número de 1 a 7.")


if __name__ == "__main__":
    main()