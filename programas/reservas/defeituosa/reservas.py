"""Sistema de reservas de salas."""

from datetime import date


class ReservaInvalidaError(Exception):
    pass


class ConflitoDeHorarioError(Exception):
    pass


class ReservaInexistenteError(Exception):
    pass


HORA_ABERTURA = 8
HORA_FECHAMENTO = 22
DURACAO_MAXIMA = 4


class Reserva:
    def __init__(self, id_reserva, sala, data, inicio, fim, participantes, responsavel):
        self.id = id_reserva
        self.sala = sala
        self.data = data
        self.inicio = inicio
        self.fim = fim
        self.participantes = participantes
        self.responsavel = responsavel
        self.ativa = True


class SistemaReservas:
    def __init__(self, salas, hoje):
        for nome, capacidade in salas.items():
            if capacidade < 1:
                raise ValueError(f"capacidade inválida para {nome}")
        self._salas = dict(salas)
        self._hoje = hoje
        self._reservas = {}
        self._proximo_id = 1

    def _validar(self, sala, data, inicio, fim, participantes, responsavel):
        if sala not in self._salas:
            raise ReservaInvalidaError(f"sala {sala} não existe")
        if not isinstance(data, date) or data < self._hoje:
            raise ReservaInvalidaError("data inválida")
        if not all(isinstance(h, int) and not isinstance(h, bool) for h in (inicio, fim)):
            raise ReservaInvalidaError("horários devem ser inteiros")
        if inicio < HORA_ABERTURA or fim > HORA_FECHAMENTO:
            raise ReservaInvalidaError("fora do horário de funcionamento")
        if inicio >= fim:
            raise ReservaInvalidaError("início deve ser anterior ao fim")
        if fim - inicio > DURACAO_MAXIMA:
            raise ReservaInvalidaError("duração máxima excedida")
        if participantes < 1:
            raise ReservaInvalidaError("número de participantes inválido")
        if not isinstance(responsavel, str) or not responsavel.strip():
            raise ReservaInvalidaError("responsável obrigatório")

    def _conflita(self, sala, data, inicio, fim):
        for r in self._reservas.values():
            if r.sala == sala and r.data == data:
                if inicio <= r.fim and fim >= r.inicio:
                    return True
        return False

    def reservar(self, sala, data, inicio, fim, participantes, responsavel):
        self._validar(sala, data, inicio, fim, participantes, responsavel)
        if self._conflita(sala, data, inicio, fim):
            raise ConflitoDeHorarioError("horário já reservado")
        reserva = Reserva(self._proximo_id, sala, data, inicio, fim,
                          participantes, responsavel.strip())
        self._reservas[reserva.id] = reserva
        self._proximo_id += 1
        return reserva.id

    def cancelar(self, id_reserva):
        reserva = self._reservas.get(id_reserva)
        if reserva is None:
            raise ReservaInexistenteError(f"reserva {id_reserva} não existe")
        if not reserva.ativa:
            raise ReservaInvalidaError("reserva já cancelada")
        reserva.ativa = False

    def buscar(self, id_reserva):
        reserva = self._reservas.get(id_reserva)
        if reserva is None:
            raise ReservaInexistenteError(f"reserva {id_reserva} não existe")
        return reserva

    def listar(self, sala, data):
        ativas = [r for r in self._reservas.values()
                  if r.ativa and r.sala == sala and r.data == data]
        return sorted(ativas, key=lambda r: r.inicio)

    def horarios_livres(self, sala, data):
        if sala not in self._salas:
            raise ReservaInvalidaError(f"sala {sala} não existe")
        ocupadas = set()
        for r in self.listar(sala, data):
            ocupadas.update(range(r.inicio, r.fim))
        return [h for h in range(HORA_ABERTURA, HORA_FECHAMENTO) if h not in ocupadas]

    def ocupacao(self, sala, data):
        total = HORA_FECHAMENTO - HORA_ABERTURA
        livres = len(self.horarios_livres(sala, data))
        return round((total - livres) / total * 100, 1)
