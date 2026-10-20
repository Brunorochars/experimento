# Requisitos — Carrinho de compras (`carrinho.py`)

Valores monetários em reais. O total é arredondado para 2 casas decimais.

## Produto

- **RC01** — Um produto tem código, nome, preço e estoque. O preço deve ser maior que zero e o estoque não pode ser negativo (`ValueError`).

## Carrinho

- **RC02** — O carrinho é criado a partir de uma lista de produtos (catálogo) e começa vazio e sem cupom.
- **RC03** — `adicionar(codigo, quantidade=1)`: o código deve existir no catálogo (`ProdutoInexistenteError`). A quantidade deve ser um inteiro (`TypeError`; booleanos não são aceitos) maior ou igual a 1 (`ValueError`). Adicionar um produto que já está no carrinho soma as quantidades.
- **RC04** — A quantidade **total** de um produto no carrinho (a que já estava mais a nova) não pode ser maior que o estoque do produto. Caso seja, lança `EstoqueInsuficienteError` e o carrinho não é alterado.
- **RC05** — `remover(codigo, quantidade=None)`: o produto deve estar no carrinho (`ProdutoInexistenteError`). Sem quantidade, remove o item inteiro. Com quantidade, ela deve estar entre 1 e a quantidade no carrinho (`ValueError`). Se a quantidade restante for zero, o item sai do carrinho.
- **RC06** — `itens()` retorna uma cópia do dicionário `{codigo: quantidade}`.
- **RC07** — `subtotal()` é a soma de `preço × quantidade` de todos os itens.
- **RC08** — Desconto progressivo sobre o subtotal: 10% se o subtotal for maior ou igual a R$ 500,00; 5% se for maior ou igual a R$ 200,00 e menor que R$ 500,00; 0% abaixo de R$ 200,00. `percentual_desconto()` retorna 10, 5 ou 0.
- **RC09** — `aplicar_cupom(codigo)`: o código é aceito sem diferenciar maiúsculas e minúsculas e ignorando espaços nas extremidades. Cupons válidos: `DESC20` e `FRETEGRATIS`. Código inválido lança `CupomInvalidoError`. Só um cupom vale por vez; aplicar outro substitui o anterior.
- **RC10** — Cupom `DESC20`: abate R$ 20,00 do valor **depois** de aplicado o desconto progressivo, desde que o subtotal seja de pelo menos R$ 100,00. Abaixo disso, o cupom não tem efeito.
- **RC11** — Frete: R$ 25,00, exceto quando o valor após os descontos (progressivo e cupom) for maior ou igual a R$ 300,00 ou quando o cupom `FRETEGRATIS` estiver aplicado; nesses casos o frete é zero.
- **RC12** — `total()` = subtotal − desconto progressivo − desconto do cupom + frete. O valor antes do frete nunca é negativo. Carrinho vazio tem total 0.
- **RC13** — `finalizar()`: carrinho vazio lança `CarrinhoVazioError`. Caso contrário, calcula o total, reduz o estoque de cada produto pela quantidade comprada, esvazia o carrinho, remove o cupom e retorna o total.
