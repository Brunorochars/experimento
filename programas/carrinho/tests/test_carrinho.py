import pytest

from carrinho import (
    Carrinho,
    CarrinhoVazioError,
    CupomInvalidoError,
    EstoqueInsuficienteError,
    Produto,
    ProdutoInexistenteError,
)


def novo_carrinho():
    catalogo = [
        Produto("A", "Caneca", 50.00, 10),
        Produto("B", "Camiseta", 100.00, 5),
        Produto("C", "Chaveiro", 10.00, 3),
    ]
    return Carrinho(catalogo), {p.codigo: p for p in catalogo}


# RC01
@pytest.mark.parametrize("preco, estoque", [(0, 1), (-1, 1), (10, -1)])
def test_produto_invalido(preco, estoque):
    with pytest.raises(ValueError):
        Produto("X", "Item", preco, estoque)


# RC03
def test_adicionar_soma_quantidades():
    c, _ = novo_carrinho()
    c.adicionar("A", 2)
    c.adicionar("A", 3)
    assert c.itens() == {"A": 5}


def test_adicionar_produto_inexistente():
    c, _ = novo_carrinho()
    with pytest.raises(ProdutoInexistenteError):
        c.adicionar("Z")


@pytest.mark.parametrize("quantidade", [0, -1])
def test_adicionar_quantidade_invalida(quantidade):
    c, _ = novo_carrinho()
    with pytest.raises(ValueError):
        c.adicionar("A", quantidade)
    assert c.itens() == {}


def test_adicionar_quantidade_nao_inteira():
    c, _ = novo_carrinho()
    with pytest.raises(TypeError):
        c.adicionar("A", 1.5)


# RC04
def test_adicionar_ate_o_estoque():
    c, _ = novo_carrinho()
    c.adicionar("C", 3)
    assert c.itens() == {"C": 3}


def test_estoque_considera_quantidade_ja_no_carrinho():
    c, _ = novo_carrinho()
    c.adicionar("C", 2)
    with pytest.raises(EstoqueInsuficienteError):
        c.adicionar("C", 2)
    assert c.itens() == {"C": 2}


def test_estoque_excedido_de_uma_vez():
    c, _ = novo_carrinho()
    with pytest.raises(EstoqueInsuficienteError):
        c.adicionar("C", 4)


# RC05 / RC06
def test_remover_parcial_e_total():
    c, _ = novo_carrinho()
    c.adicionar("A", 4)
    c.remover("A", 1)
    assert c.itens() == {"A": 3}
    c.remover("A", 3)
    assert c.itens() == {}


def test_remover_item_inteiro():
    c, _ = novo_carrinho()
    c.adicionar("B", 2)
    c.remover("B")
    assert c.itens() == {}


def test_remover_invalido():
    c, _ = novo_carrinho()
    with pytest.raises(ProdutoInexistenteError):
        c.remover("A")
    c.adicionar("A", 1)
    with pytest.raises(ValueError):
        c.remover("A", 2)


def test_itens_e_copia():
    c, _ = novo_carrinho()
    c.adicionar("A")
    c.itens().clear()
    assert c.itens() == {"A": 1}


# RC07 / RC08
def test_subtotal():
    c, _ = novo_carrinho()
    c.adicionar("A", 2)
    c.adicionar("C", 1)
    assert c.subtotal() == 110


@pytest.mark.parametrize(
    "qtd_a, esperado",
    [(3, 0), (4, 5), (9, 5), (10, 10)],
)
def test_percentual_desconto_por_faixa(qtd_a, esperado):
    c, _ = novo_carrinho()
    c.adicionar("A", qtd_a)
    assert c.percentual_desconto() == esperado


# RC09
def test_cupom_invalido():
    c, _ = novo_carrinho()
    with pytest.raises(CupomInvalidoError):
        c.aplicar_cupom("DESC50")


# RC10 / RC11 / RC12
def test_total_sem_desconto_com_frete():
    c, _ = novo_carrinho()
    c.adicionar("A", 2)
    assert c.total() == 125


def test_total_desconto_5_porcento_com_frete():
    c, _ = novo_carrinho()
    c.adicionar("B", 2)
    assert c.total() == 215


def test_total_frete_gratis_por_valor():
    c, _ = novo_carrinho()
    c.adicionar("A", 7)
    assert c.total() == 332.5


def test_cupom_desc20_apos_desconto_progressivo():
    c, _ = novo_carrinho()
    c.adicionar("A", 10)
    c.adicionar("B", 1)
    c.aplicar_cupom(" desc20 ")
    assert c.total() == 520


def test_cupom_desc20_sem_desconto_progressivo():
    c, _ = novo_carrinho()
    c.adicionar("A", 3)
    c.aplicar_cupom("DESC20")
    assert c.total() == 155


def test_cupom_desc20_abaixo_do_minimo():
    c, _ = novo_carrinho()
    c.adicionar("A", 1)
    c.aplicar_cupom("DESC20")
    assert c.total() == 75


def test_cupom_fretegratis():
    c, _ = novo_carrinho()
    c.adicionar("A", 1)
    c.aplicar_cupom("fretegratis")
    assert c.total() == 50


def test_total_carrinho_vazio():
    c, _ = novo_carrinho()
    assert c.total() == 0


# RC13
def test_finalizar():
    c, produtos = novo_carrinho()
    c.adicionar("A", 2)
    c.adicionar("C", 3)
    c.aplicar_cupom("FRETEGRATIS")
    assert c.finalizar() == 130
    assert produtos["A"].estoque == 8
    assert produtos["C"].estoque == 0
    assert c.itens() == {}
    assert c.total() == 0


def test_finalizar_vazio():
    c, _ = novo_carrinho()
    with pytest.raises(CarrinhoVazioError):
        c.finalizar()
