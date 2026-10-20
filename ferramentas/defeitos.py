"""Definição dos 12 defeitos semeados (gabarito em formato de dados).

Cada defeito é uma substituição exata de um trecho da versão correta.
NÃO envie este arquivo aos assistentes.
"""

DEFEITOS = [
    # ---------------- Controle bancário ----------------
    {
        "codigo": "D01", "programa": "banco", "arquivo": "banco.py",
        "categoria": "Valor-limite", "requisito": "RB03",
        "metodo": "Conta._validar_debito",
        "original": "        if valor > self._saldo:\n",
        "defeituoso": "        if valor >= self._saldo:\n",
        "esperado": "Saque (ou transferência) de valor igual ao saldo é aceito e deixa o saldo em zero.",
        "observado": "Saque de valor igual ao saldo lança SaldoInsuficienteError.",
        "teste": "test_saque_de_todo_o_saldo",
    },
    {
        "codigo": "D02", "programa": "banco", "arquivo": "banco.py",
        "categoria": "Cálculo", "requisito": "RB07",
        "metodo": "Conta.aplicar_rendimento",
        "original": "        rendimento = round(self._saldo * taxa_percentual / 100, 2)\n",
        "defeituoso": "        rendimento = round(self._saldo * taxa_percentual / 10, 2)\n",
        "esperado": "Saldo 1000 com taxa 1% rende 10,00 (saldo final 1010,00).",
        "observado": "Rende 100,00 (saldo final 1100,00): o percentual é dividido por 10 em vez de 100.",
        "teste": "test_rendimento",
    },
    {
        "codigo": "D03", "programa": "banco", "arquivo": "banco.py",
        "categoria": "Atualização de dados", "requisito": "RB04, RB06",
        "metodo": "Conta.transferir",
        "original": (
            "        self._saldo = round(self._saldo - valor, 2)\n"
            "        self._sacado_hoje = round(self._sacado_hoje + valor, 2)\n"
            "        destino._saldo"
        ),
        "defeituoso": (
            "        self._saldo = round(self._saldo - valor, 2)\n"
            "        destino._saldo"
        ),
        "esperado": "A transferência enviada é somada ao total debitado no dia; após transferir 800, um saque de 300 lança LimiteDiarioError.",
        "observado": "Transferências não atualizam sacado_hoje; o saque de 300 é aceito e o limite diário pode ser ultrapassado.",
        "teste": "test_transferencia_conta_no_limite_diario, test_transferencia",
    },
    # ---------------- Carrinho de compras ----------------
    {
        "codigo": "D04", "programa": "carrinho", "arquivo": "carrinho.py",
        "categoria": "Condição", "requisito": "RC04",
        "metodo": "Carrinho.adicionar",
        "original": "        if atual + quantidade > produto.estoque:\n",
        "defeituoso": "        if quantidade > produto.estoque:\n",
        "esperado": "Com estoque 3 e 2 unidades no carrinho, adicionar mais 2 lança EstoqueInsuficienteError.",
        "observado": "A verificação ignora a quantidade já no carrinho; o item fica com 4 unidades, acima do estoque.",
        "teste": "test_estoque_considera_quantidade_ja_no_carrinho",
    },
    {
        "codigo": "D05", "programa": "carrinho", "arquivo": "carrinho.py",
        "categoria": "Validação de entrada", "requisito": "RC03",
        "metodo": "Carrinho.adicionar",
        "original": "        if quantidade < 1:\n",
        "defeituoso": "        if quantidade < 0:\n",
        "esperado": "adicionar(codigo, 0) lança ValueError e o carrinho não é alterado.",
        "observado": "Quantidade 0 é aceita e o produto entra no carrinho com quantidade 0.",
        "teste": "test_adicionar_quantidade_invalida[0]",
    },
    {
        "codigo": "D06", "programa": "carrinho", "arquivo": "carrinho.py",
        "categoria": "Cálculo", "requisito": "RC10",
        "metodo": "Carrinho.total",
        "original": "        valor = subtotal * (1 - percentual / 100) - desconto_cupom\n",
        "defeituoso": "        valor = (subtotal - desconto_cupom) * (1 - percentual / 100)\n",
        "esperado": "Subtotal 600 (10%) com DESC20: 600 × 0,9 − 20 = 520,00.",
        "observado": "O cupom é abatido antes do percentual: (600 − 20) × 0,9 = 522,00.",
        "teste": "test_cupom_desc20_apos_desconto_progressivo",
    },
    # ---------------- Sistema de reservas ----------------
    {
        "codigo": "D07", "programa": "reservas", "arquivo": "reservas.py",
        "categoria": "Valor-limite", "requisito": "RR04",
        "metodo": "SistemaReservas._conflita",
        "original": "                if inicio < r.fim and fim > r.inicio:\n",
        "defeituoso": "                if inicio <= r.fim and fim >= r.inicio:\n",
        "esperado": "Reserva 12–14 é aceita quando já existe 10–12 na mesma sala e data.",
        "observado": "Reservas encostadas são tratadas como sobrepostas e lançam ConflitoDeHorarioError.",
        "teste": "test_reservas_encostadas_nao_conflitam",
    },
    {
        "codigo": "D08", "programa": "reservas", "arquivo": "reservas.py",
        "categoria": "Validação de entrada", "requisito": "RR03",
        "metodo": "SistemaReservas._validar",
        "original": "        if participantes < 1 or participantes > self._salas[sala]:\n",
        "defeituoso": "        if participantes < 1:\n",
        "esperado": "Reserva com 7 participantes na sala de capacidade 6 lança ReservaInvalidaError.",
        "observado": "A capacidade da sala não é verificada; a reserva é criada.",
        "teste": "test_participantes_acima_da_capacidade",
    },
    {
        "codigo": "D09", "programa": "reservas", "arquivo": "reservas.py",
        "categoria": "Condição", "requisito": "RR04, RR05",
        "metodo": "SistemaReservas._conflita",
        "original": "            if r.ativa and r.sala == sala and r.data == data:\n",
        "defeituoso": "            if r.sala == sala and r.data == data:\n",
        "esperado": "Após cancelar a reserva 10–12, uma nova reserva 10–12 na mesma sala e data é aceita.",
        "observado": "Reservas canceladas continuam bloqueando o horário (ConflitoDeHorarioError), embora horarios_livres o mostre livre.",
        "teste": "test_cancelar_libera_horario",
    },
    # ---------------- Gerenciamento de notas ----------------
    {
        "codigo": "D10", "programa": "notas", "arquivo": "notas.py",
        "categoria": "Cálculo", "requisito": "RN05",
        "metodo": "constante PESOS (usada em Turma.media)",
        "original": 'PESOS = {"P1": 0.35, "P2": 0.35, "T": 0.30}\n',
        "defeituoso": 'PESOS = {"P1": 0.35, "P2": 0.30, "T": 0.35}\n',
        "esperado": "P1=0, P2=10, T=0 resulta em média 3,5; P1=0, P2=0, T=10 resulta em 3,0.",
        "observado": "Os pesos de P2 e T estão trocados: as médias resultam 3,0 e 3,5.",
        "teste": "test_media_pesos_das_provas, test_media_peso_do_trabalho, test_media_avaliacao_faltante_conta_zero",
    },
    {
        "codigo": "D11", "programa": "notas", "arquivo": "notas.py",
        "categoria": "Validação de entrada", "requisito": "RN03, RN07",
        "metodo": "Turma._validar_nota",
        "original": "        if nota < 0 or nota > 10:\n",
        "defeituoso": "        if nota < 0:\n",
        "esperado": "Nota 10,5 (ou 11) lança NotaInvalidaError, também no exame.",
        "observado": "Notas acima de 10 são aceitas.",
        "teste": "test_nota_fora_do_intervalo[10.5], test_nota_fora_do_intervalo[11]",
    },
    {
        "codigo": "D12", "programa": "notas", "arquivo": "notas.py",
        "categoria": "Valor-limite", "requisito": "RN06",
        "metodo": "Turma.situacao",
        "original": "        if aluno.frequencia < FREQUENCIA_MINIMA:\n",
        "defeituoso": "        if aluno.frequencia <= FREQUENCIA_MINIMA:\n",
        "esperado": "Aluno com frequência exatamente 75% e média 8 está \"Aprovado\".",
        "observado": "Frequência de exatamente 75% resulta em \"Reprovado por frequência\".",
        "teste": "test_frequencia_exatamente_75_nao_reprova",
    },
]
