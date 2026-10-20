# Requisitos — Controle bancário (`banco.py`)

Valores monetários são números (`int` ou `float`) em reais. Todo saldo resultante de uma operação é arredondado para 2 casas decimais.

## Conta

- **RB01** — Uma conta é criada com titular, número e saldo inicial (padrão 0). O titular deve ser um texto não vazio (espaços nas extremidades são removidos); caso contrário, lança `ValueError`. O saldo inicial não pode ser negativo (`ValueError`).
- **RB02** — `depositar(valor)`: o valor deve ser numérico (`TypeError` caso contrário; valores booleanos não são aceitos) e maior que zero (`ValueError`). O valor é somado ao saldo e a operação é registrada no extrato como `("deposito", valor)`.
- **RB03 — `sacar(valor)`: o valor segue as mesmas regras de validação do depósito. O saque é permitido quando o valor é menor ou igual** ao saldo disponível; a conta pode ficar com saldo exatamente zero. Se o valor for maior que o saldo, lança `SaldoInsuficienteError`.
- **RB04 — Limite diário: a soma de todos os débitos do dia (saques e transferências enviadas**) não pode ultrapassar R$ 1.000,00. É permitido atingir exatamente esse valor. Um débito que faria a soma ultrapassar o limite lança `LimiteDiarioError` e não altera a conta.
- **RB05** — Um saque bem-sucedido reduz o saldo, soma o valor ao total debitado no dia e é registrado como `("saque", valor)`.
- **RB06** — `transferir(destino, valor)`: o destino deve ser uma `Conta` (`TypeError`) diferente da conta de origem (`ValueError`). A origem segue as mesmas regras do saque (RB03 e RB04). Em caso de sucesso, o valor sai da origem, entra no destino, é somado ao total debitado no dia da origem e é registrado no extrato da origem como `("transferencia_enviada", valor)` e no do destino como `("transferencia_recebida", valor)`. Se a transferência for recusada, nenhuma das contas é alterada.
- **RB07** — `aplicar_rendimento(taxa_percentual)`: a taxa é um percentual entre 0 e 2, inclusive (`ValueError` fora desse intervalo; `TypeError` se não for numérica). O rendimento é `saldo × taxa_percentual / 100`, arredondado para 2 casas, e é somado ao saldo. Quando o rendimento é maior que zero, é registrado como `("rendimento", rendimento)`. O método retorna o rendimento.
- **RB08** — `extrato()` retorna uma cópia da lista de operações, na ordem em que ocorreram.
- **RB09** — `novo_dia()` zera o total debitado no dia.

## Banco

- **RB10** — `abrir_conta(titular, saldo_inicial)` cria uma conta com número sequencial, começando em 1001.
- **RB11** — `buscar(numero)` retorna a conta; se não existir, lança `ContaInexistenteError`.
- **RB12** — `transferir(numero_origem, numero_destino, valor)` localiza as duas contas e realiza a transferência conforme RB06.
- **RB13** — `encerrar_dia()` aplica `novo_dia()` a todas as contas.
- **RB14** — `saldo_total()` retorna a soma dos saldos de todas as contas, arredondada para 2 casas.
