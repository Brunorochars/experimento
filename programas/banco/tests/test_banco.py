import pytest

from banco import (
    Banco,
    Conta,
    ContaInexistenteError,
    LimiteDiarioError,
    SaldoInsuficienteError,
)


# RB01
def test_criar_conta_valida():
    c = Conta("  Ana  ", 1, 50)
    assert c.titular == "Ana"
    assert c.saldo == 50


@pytest.mark.parametrize("titular", ["", "   ", None])
def test_titular_invalido(titular):
    with pytest.raises(ValueError):
        Conta(titular, 1)


def test_saldo_inicial_negativo():
    with pytest.raises(ValueError):
        Conta("Ana", 1, -1)


# RB02
def test_deposito():
    c = Conta("Ana", 1, 10)
    c.depositar(15.5)
    assert c.saldo == 25.5
    assert c.extrato() == [("deposito", 15.5)]


@pytest.mark.parametrize("valor", [0, -5])
def test_deposito_valor_nao_positivo(valor):
    c = Conta("Ana", 1)
    with pytest.raises(ValueError):
        c.depositar(valor)


def test_deposito_valor_nao_numerico():
    c = Conta("Ana", 1)
    with pytest.raises(TypeError):
        c.depositar("10")
    with pytest.raises(TypeError):
        c.depositar(True)


# RB03 / RB05
def test_saque_comum():
    c = Conta("Ana", 1, 200)
    c.sacar(50)
    assert c.saldo == 150
    assert c.sacado_hoje == 50
    assert c.extrato() == [("saque", 50)]


def test_saque_de_todo_o_saldo():
    c = Conta("Ana", 1, 100)
    c.sacar(100)
    assert c.saldo == 0


def test_saque_maior_que_saldo():
    c = Conta("Ana", 1, 100)
    with pytest.raises(SaldoInsuficienteError):
        c.sacar(100.01)
    assert c.saldo == 100


# RB04
def test_limite_diario_pode_ser_atingido_exatamente():
    c = Conta("Ana", 1, 5000)
    c.sacar(600)
    c.sacar(400)
    assert c.sacado_hoje == 1000


def test_limite_diario_excedido_por_saques():
    c = Conta("Ana", 1, 5000)
    c.sacar(900)
    with pytest.raises(LimiteDiarioError):
        c.sacar(101)
    assert c.saldo == 4100


def test_transferencia_conta_no_limite_diario():
    a = Conta("Ana", 1, 5000)
    b = Conta("Bia", 2)
    a.transferir(b, 800)
    with pytest.raises(LimiteDiarioError):
        a.sacar(300)
    assert a.saldo == 4200


# RB06
def test_transferencia():
    a = Conta("Ana", 1, 300)
    b = Conta("Bia", 2, 10)
    a.transferir(b, 120)
    assert a.saldo == 180
    assert b.saldo == 130
    assert a.sacado_hoje == 120
    assert a.extrato() == [("transferencia_enviada", 120)]
    assert b.extrato() == [("transferencia_recebida", 120)]


def test_transferencia_para_mesma_conta():
    a = Conta("Ana", 1, 300)
    with pytest.raises(ValueError):
        a.transferir(a, 10)


def test_transferencia_recusada_nao_altera_contas():
    a = Conta("Ana", 1, 50)
    b = Conta("Bia", 2, 10)
    with pytest.raises(SaldoInsuficienteError):
        a.transferir(b, 60)
    assert (a.saldo, b.saldo) == (50, 10)
    assert a.extrato() == [] and b.extrato() == []


# RB07
def test_rendimento():
    c = Conta("Ana", 1, 1000)
    rendimento = c.aplicar_rendimento(1)
    assert rendimento == 10
    assert c.saldo == 1010
    assert c.extrato() == [("rendimento", 10)]


def test_rendimento_taxa_zero_nao_registra():
    c = Conta("Ana", 1, 1000)
    assert c.aplicar_rendimento(0) == 0
    assert c.extrato() == []


@pytest.mark.parametrize("taxa", [-0.1, 2.01])
def test_rendimento_taxa_fora_do_intervalo(taxa):
    c = Conta("Ana", 1, 1000)
    with pytest.raises(ValueError):
        c.aplicar_rendimento(taxa)


# RB08 / RB09
def test_extrato_e_copia():
    c = Conta("Ana", 1, 10)
    c.depositar(5)
    c.extrato().clear()
    assert len(c.extrato()) == 1


def test_novo_dia_zera_limite():
    c = Conta("Ana", 1, 5000)
    c.sacar(1000)
    c.novo_dia()
    c.sacar(500)
    assert c.sacado_hoje == 500


# RB10 a RB14
def test_banco_numeracao_e_busca():
    banco = Banco()
    a = banco.abrir_conta("Ana", 100)
    b = banco.abrir_conta("Bia")
    assert (a.numero, b.numero) == (1001, 1002)
    assert banco.buscar(1002) is b
    with pytest.raises(ContaInexistenteError):
        banco.buscar(9999)


def test_banco_transferir_e_saldo_total():
    banco = Banco()
    banco.abrir_conta("Ana", 100)
    banco.abrir_conta("Bia", 50)
    banco.transferir(1001, 1002, 30)
    assert banco.buscar(1001).saldo == 70
    assert banco.buscar(1002).saldo == 80
    assert banco.saldo_total() == 150


def test_banco_encerrar_dia():
    banco = Banco()
    a = banco.abrir_conta("Ana", 3000)
    a.sacar(1000)
    banco.encerrar_dia()
    assert a.sacado_hoje == 0
