"""Controle de contas bancárias."""


class SaldoInsuficienteError(Exception):
    pass


class LimiteDiarioError(Exception):
    pass


class ContaInexistenteError(Exception):
    pass


LIMITE_DIARIO_SAQUE = 1000.00
TAXA_RENDIMENTO_MAXIMA = 2.0
PRIMEIRO_NUMERO_CONTA = 1001


class Conta:
    def __init__(self, titular, numero, saldo_inicial=0.0):
        if not isinstance(titular, str) or not titular.strip():
            raise ValueError("titular inválido")
        if saldo_inicial < 0:
            raise ValueError("saldo inicial não pode ser negativo")
        self.titular = titular.strip()
        self.numero = numero
        self._saldo = round(float(saldo_inicial), 2)
        self._sacado_hoje = 0.0
        self._extrato = []

    @property
    def saldo(self):
        return self._saldo

    @property
    def sacado_hoje(self):
        return self._sacado_hoje

    def extrato(self):
        return list(self._extrato)

    def _validar_valor(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError("valor deve ser numérico")
        if valor <= 0:
            raise ValueError("valor deve ser positivo")

    def _validar_debito(self, valor):
        self._validar_valor(valor)
        if valor >= self._saldo:
            raise SaldoInsuficienteError("saldo insuficiente")
        if self._sacado_hoje + valor > LIMITE_DIARIO_SAQUE:
            raise LimiteDiarioError("limite diário excedido")

    def depositar(self, valor):
        self._validar_valor(valor)
        self._saldo = round(self._saldo + valor, 2)
        self._extrato.append(("deposito", valor))

    def sacar(self, valor):
        self._validar_debito(valor)
        self._saldo = round(self._saldo - valor, 2)
        self._sacado_hoje = round(self._sacado_hoje + valor, 2)
        self._extrato.append(("saque", valor))

    def transferir(self, destino, valor):
        if not isinstance(destino, Conta):
            raise TypeError("destino deve ser uma conta")
        if destino is self:
            raise ValueError("não é possível transferir para a mesma conta")
        self._validar_debito(valor)
        self._saldo = round(self._saldo - valor, 2)
        destino._saldo = round(destino._saldo + valor, 2)
        self._extrato.append(("transferencia_enviada", valor))
        destino._extrato.append(("transferencia_recebida", valor))

    def aplicar_rendimento(self, taxa_percentual):
        if isinstance(taxa_percentual, bool) or not isinstance(taxa_percentual, (int, float)):
            raise TypeError("taxa deve ser numérica")
        if not 0 <= taxa_percentual <= TAXA_RENDIMENTO_MAXIMA:
            raise ValueError("taxa fora do intervalo permitido")
        rendimento = round(self._saldo * taxa_percentual / 10, 2)
        self._saldo = round(self._saldo + rendimento, 2)
        if rendimento > 0:
            self._extrato.append(("rendimento", rendimento))
        return rendimento

    def novo_dia(self):
        self._sacado_hoje = 0.0


class Banco:
    def __init__(self):
        self._contas = {}
        self._proximo_numero = PRIMEIRO_NUMERO_CONTA

    def abrir_conta(self, titular, saldo_inicial=0.0):
        conta = Conta(titular, self._proximo_numero, saldo_inicial)
        self._contas[conta.numero] = conta
        self._proximo_numero += 1
        return conta

    def buscar(self, numero):
        if numero not in self._contas:
            raise ContaInexistenteError(f"conta {numero} não encontrada")
        return self._contas[numero]

    def transferir(self, numero_origem, numero_destino, valor):
        origem = self.buscar(numero_origem)
        destino = self.buscar(numero_destino)
        origem.transferir(destino, valor)

    def encerrar_dia(self):
        for conta in self._contas.values():
            conta.novo_dia()

    def saldo_total(self):
        return round(sum(c.saldo for c in self._contas.values()), 2)
