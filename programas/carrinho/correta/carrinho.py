"""Carrinho de compras."""


class ProdutoInexistenteError(Exception):
    pass


class EstoqueInsuficienteError(Exception):
    pass


class CupomInvalidoError(Exception):
    pass


class CarrinhoVazioError(Exception):
    pass


FRETE_PADRAO = 25.00
VALOR_FRETE_GRATIS = 300.00
CUPONS_VALIDOS = {"DESC20", "FRETEGRATIS"}
VALOR_CUPOM_DESC20 = 20.00
VALOR_MINIMO_DESC20 = 100.00


class Produto:
    def __init__(self, codigo, nome, preco, estoque):
        if preco <= 0:
            raise ValueError("preço deve ser positivo")
        if estoque < 0:
            raise ValueError("estoque não pode ser negativo")
        self.codigo = codigo
        self.nome = nome
        self.preco = preco
        self.estoque = estoque


class Carrinho:
    def __init__(self, catalogo):
        self._catalogo = {p.codigo: p for p in catalogo}
        self._itens = {}
        self._cupom = None

    def _produto(self, codigo):
        if codigo not in self._catalogo:
            raise ProdutoInexistenteError(f"produto {codigo} não existe")
        return self._catalogo[codigo]

    def adicionar(self, codigo, quantidade=1):
        produto = self._produto(codigo)
        if isinstance(quantidade, bool) or not isinstance(quantidade, int):
            raise TypeError("quantidade deve ser inteira")
        if quantidade < 1:
            raise ValueError("quantidade inválida")
        atual = self._itens.get(codigo, 0)
        if atual + quantidade > produto.estoque:
            raise EstoqueInsuficienteError(f"estoque insuficiente para {codigo}")
        self._itens[codigo] = atual + quantidade

    def remover(self, codigo, quantidade=None):
        if codigo not in self._itens:
            raise ProdutoInexistenteError(f"produto {codigo} não está no carrinho")
        if quantidade is None:
            quantidade = self._itens[codigo]
        if quantidade < 1 or quantidade > self._itens[codigo]:
            raise ValueError("quantidade inválida")
        restante = self._itens[codigo] - quantidade
        if restante == 0:
            del self._itens[codigo]
        else:
            self._itens[codigo] = restante

    def itens(self):
        return dict(self._itens)

    def subtotal(self):
        total = sum(self._catalogo[c].preco * q for c, q in self._itens.items())
        return round(total, 2)

    def percentual_desconto(self):
        subtotal = self.subtotal()
        if subtotal >= 500:
            return 10
        if subtotal >= 200:
            return 5
        return 0

    def aplicar_cupom(self, codigo):
        codigo = codigo.strip().upper()
        if codigo not in CUPONS_VALIDOS:
            raise CupomInvalidoError(f"cupom {codigo} inválido")
        self._cupom = codigo

    def _frete(self, valor_com_desconto):
        if self._cupom == "FRETEGRATIS" or valor_com_desconto >= VALOR_FRETE_GRATIS:
            return 0.0
        return FRETE_PADRAO

    def total(self):
        subtotal = self.subtotal()
        if not self._itens:
            return 0.0
        percentual = self.percentual_desconto()
        desconto_cupom = 0.0
        if self._cupom == "DESC20" and subtotal >= VALOR_MINIMO_DESC20:
            desconto_cupom = VALOR_CUPOM_DESC20
        valor = subtotal * (1 - percentual / 100) - desconto_cupom
        valor = max(valor, 0.0)
        return round(valor + self._frete(valor), 2)

    def finalizar(self):
        if not self._itens:
            raise CarrinhoVazioError("carrinho vazio")
        total = self.total()
        for codigo, quantidade in self._itens.items():
            self._catalogo[codigo].estoque -= quantidade
        self._itens.clear()
        self._cupom = None
        return total
