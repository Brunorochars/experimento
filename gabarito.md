# Gabarito dos defeitos semeados

**Uso restrito do grupo. Não enviar aos assistentes.**

## Correspondência das entradas

| Programa | Versão correta | Versão defeituosa |
|---|---|---|
| Controle bancário | `banco_B.txt` | `banco_A.txt` |
| Carrinho de compras | `carrinho_A.txt` | `carrinho_B.txt` |
| Sistema de reservas | `reservas_B.txt` | `reservas_A.txt` |
| Gerenciamento de notas | `notas_B.txt` | `notas_A.txt` |

## Defeitos

### Controle bancário (`banco`)

#### D01 — Valor-limite

- **Localização:** `banco.py`, Conta._validar_debito, linha 52 da versão defeituosa
- **Requisito violado:** RB03
- **Código correto:** `if valor > self._saldo:`
- **Código defeituoso:** `if valor >= self._saldo:`
- **Comportamento esperado:** Saque (ou transferência) de valor igual ao saldo é aceito e deixa o saldo em zero.
- **Comportamento observado:** Saque de valor igual ao saldo lança SaldoInsuficienteError.
- **Teste que demonstra:** `test_saque_de_todo_o_saldo`

#### D02 — Cálculo

- **Localização:** `banco.py`, Conta.aplicar_rendimento, linha 84 da versão defeituosa
- **Requisito violado:** RB07
- **Código correto:** `rendimento = round(self._saldo * taxa_percentual / 100, 2)`
- **Código defeituoso:** `rendimento = round(self._saldo * taxa_percentual / 10, 2)`
- **Comportamento esperado:** Saldo 1000 com taxa 1% rende 10,00 (saldo final 1010,00).
- **Comportamento observado:** Rende 100,00 (saldo final 1100,00): o percentual é dividido por 10 em vez de 100.
- **Teste que demonstra:** `test_rendimento`

#### D03 — Atualização de dados

- **Localização:** `banco.py`, Conta.transferir, linha 64, 74 da versão defeituosa
- **Requisito violado:** RB04, RB06
- **Código correto:** `self._saldo = round(self._saldo - valor, 2) / self._sacado_hoje = round(self._sacado_hoje + valor, 2) / destino._saldo`
- **Código defeituoso:** `self._saldo = round(self._saldo - valor, 2) / destino._saldo`
- **Comportamento esperado:** A transferência enviada é somada ao total debitado no dia; após transferir 800, um saque de 300 lança LimiteDiarioError.
- **Comportamento observado:** Transferências não atualizam sacado_hoje; o saque de 300 é aceito e o limite diário pode ser ultrapassado.
- **Teste que demonstra:** `test_transferencia_conta_no_limite_diario, test_transferencia`

### Carrinho de compras (`carrinho`)

#### D04 — Condição

- **Localização:** `carrinho.py`, Carrinho.adicionar, linha 57 da versão defeituosa
- **Requisito violado:** RC04
- **Código correto:** `if atual + quantidade > produto.estoque:`
- **Código defeituoso:** `if quantidade > produto.estoque:`
- **Comportamento esperado:** Com estoque 3 e 2 unidades no carrinho, adicionar mais 2 lança EstoqueInsuficienteError.
- **Comportamento observado:** A verificação ignora a quantidade já no carrinho; o item fica com 4 unidades, acima do estoque.
- **Teste que demonstra:** `test_estoque_considera_quantidade_ja_no_carrinho`

#### D05 — Validação de entrada

- **Localização:** `carrinho.py`, Carrinho.adicionar, linha 54 da versão defeituosa
- **Requisito violado:** RC03
- **Código correto:** `if quantidade < 1:`
- **Código defeituoso:** `if quantidade < 0:`
- **Comportamento esperado:** adicionar(codigo, 0) lança ValueError e o carrinho não é alterado.
- **Comportamento observado:** Quantidade 0 é aceita e o produto entra no carrinho com quantidade 0.
- **Teste que demonstra:** `test_adicionar_quantidade_invalida[0]`

#### D06 — Cálculo

- **Localização:** `carrinho.py`, Carrinho.total, linha 108 da versão defeituosa
- **Requisito violado:** RC10
- **Código correto:** `valor = subtotal * (1 - percentual / 100) - desconto_cupom`
- **Código defeituoso:** `valor = (subtotal - desconto_cupom) * (1 - percentual / 100)`
- **Comportamento esperado:** Subtotal 600 (10%) com DESC20: 600 × 0,9 − 20 = 520,00.
- **Comportamento observado:** O cupom é abatido antes do percentual: (600 − 20) × 0,9 = 522,00.
- **Teste que demonstra:** `test_cupom_desc20_apos_desconto_progressivo`

### Sistema de reservas (`reservas`)

#### D07 — Valor-limite

- **Localização:** `reservas.py`, SistemaReservas._conflita, linha 66 da versão defeituosa
- **Requisito violado:** RR04
- **Código correto:** `if inicio < r.fim and fim > r.inicio:`
- **Código defeituoso:** `if inicio <= r.fim and fim >= r.inicio:`
- **Comportamento esperado:** Reserva 12–14 é aceita quando já existe 10–12 na mesma sala e data.
- **Comportamento observado:** Reservas encostadas são tratadas como sobrepostas e lançam ConflitoDeHorarioError.
- **Teste que demonstra:** `test_reservas_encostadas_nao_conflitam`

#### D08 — Validação de entrada

- **Localização:** `reservas.py`, SistemaReservas._validar, linha 58 da versão defeituosa
- **Requisito violado:** RR03
- **Código correto:** `if participantes < 1 or participantes > self._salas[sala]:`
- **Código defeituoso:** `if participantes < 1:`
- **Comportamento esperado:** Reserva com 7 participantes na sala de capacidade 6 lança ReservaInvalidaError.
- **Comportamento observado:** A capacidade da sala não é verificada; a reserva é criada.
- **Teste que demonstra:** `test_participantes_acima_da_capacidade`

#### D09 — Condição

- **Localização:** `reservas.py`, SistemaReservas._conflita, linha 65 da versão defeituosa
- **Requisito violado:** RR04, RR05
- **Código correto:** `if r.ativa and r.sala == sala and r.data == data:`
- **Código defeituoso:** `if r.sala == sala and r.data == data:`
- **Comportamento esperado:** Após cancelar a reserva 10–12, uma nova reserva 10–12 na mesma sala e data é aceita.
- **Comportamento observado:** Reservas canceladas continuam bloqueando o horário (ConflitoDeHorarioError), embora horarios_livres o mostre livre.
- **Teste que demonstra:** `test_cancelar_libera_horario`

### Gerenciamento de notas (`notas`)

#### D10 — Cálculo

- **Localização:** `notas.py`, constante PESOS (usada em Turma.media), linha 20 da versão defeituosa
- **Requisito violado:** RN05
- **Código correto:** `PESOS = {"P1": 0.35, "P2": 0.35, "T": 0.30}`
- **Código defeituoso:** `PESOS = {"P1": 0.35, "P2": 0.30, "T": 0.35}`
- **Comportamento esperado:** P1=0, P2=10, T=0 resulta em média 3,5; P1=0, P2=0, T=10 resulta em 3,0.
- **Comportamento observado:** Os pesos de P2 e T estão trocados: as médias resultam 3,0 e 3,5.
- **Teste que demonstra:** `test_media_pesos_das_provas, test_media_peso_do_trabalho, test_media_avaliacao_faltante_conta_zero`

#### D11 — Validação de entrada

- **Localização:** `notas.py`, Turma._validar_nota, linha 55 da versão defeituosa
- **Requisito violado:** RN03, RN07
- **Código correto:** `if nota < 0 or nota > 10:`
- **Código defeituoso:** `if nota < 0:`
- **Comportamento esperado:** Nota 10,5 (ou 11) lança NotaInvalidaError, também no exame.
- **Comportamento observado:** Notas acima de 10 são aceitas.
- **Teste que demonstra:** `test_nota_fora_do_intervalo[10.5], test_nota_fora_do_intervalo[11]`

#### D12 — Valor-limite

- **Localização:** `notas.py`, Turma.situacao, linha 80 da versão defeituosa
- **Requisito violado:** RN06
- **Código correto:** `if aluno.frequencia < FREQUENCIA_MINIMA:`
- **Código defeituoso:** `if aluno.frequencia <= FREQUENCIA_MINIMA:`
- **Comportamento esperado:** Aluno com frequência exatamente 75% e média 8 está "Aprovado".
- **Comportamento observado:** Frequência de exatamente 75% resulta em "Reprovado por frequência".
- **Teste que demonstra:** `test_frequencia_exatamente_75_nao_reprova`
