from datetime import date

import pytest

from reservas import (
    ConflitoDeHorarioError,
    ReservaInexistenteError,
    ReservaInvalidaError,
    SistemaReservas,
)

HOJE = date(2026, 11, 2)
AMANHA = date(2026, 11, 3)


def novo_sistema():
    return SistemaReservas({"Azul": 6, "Verde": 12}, HOJE)


# RR01
def test_capacidade_invalida():
    with pytest.raises(ValueError):
        SistemaReservas({"Azul": 0}, HOJE)


# RR02
def test_ids_sequenciais():
    s = novo_sistema()
    assert s.reservar("Azul", HOJE, 8, 10, 3, "Ana") == 1
    assert s.reservar("Verde", HOJE, 8, 10, 3, "Bia") == 2


def test_reserva_salva_dados():
    s = novo_sistema()
    rid = s.reservar("Azul", AMANHA, 14, 16, 4, "  Ana ")
    r = s.buscar(rid)
    assert (r.sala, r.data, r.inicio, r.fim, r.participantes) == ("Azul", AMANHA, 14, 16, 4)
    assert r.responsavel == "Ana"
    assert r.ativa


# RR03
@pytest.mark.parametrize(
    "sala, data, inicio, fim, participantes, responsavel",
    [
        ("Roxa", HOJE, 8, 10, 2, "Ana"),
        ("Azul", date(2026, 11, 1), 8, 10, 2, "Ana"),
        ("Azul", HOJE, 7, 9, 2, "Ana"),
        ("Azul", HOJE, 20, 23, 2, "Ana"),
        ("Azul", HOJE, 10, 10, 2, "Ana"),
        ("Azul", HOJE, 12, 10, 2, "Ana"),
        ("Azul", HOJE, 8, 13, 2, "Ana"),
        ("Azul", HOJE, 8, 10, 0, "Ana"),
        ("Azul", HOJE, 8, 10, 2, "   "),
        ("Azul", HOJE, 8.5, 10, 2, "Ana"),
    ],
)
def test_reserva_invalida(sala, data, inicio, fim, participantes, responsavel):
    s = novo_sistema()
    with pytest.raises(ReservaInvalidaError):
        s.reservar(sala, data, inicio, fim, participantes, responsavel)


def test_limites_validos_de_horario_e_duracao():
    s = novo_sistema()
    s.reservar("Azul", HOJE, 8, 12, 1, "Ana")
    s.reservar("Azul", HOJE, 18, 22, 1, "Bia")
    assert len(s.listar("Azul", HOJE)) == 2


def test_participantes_igual_a_capacidade():
    s = novo_sistema()
    s.reservar("Azul", HOJE, 8, 9, 6, "Ana")


def test_participantes_acima_da_capacidade():
    s = novo_sistema()
    with pytest.raises(ReservaInvalidaError):
        s.reservar("Azul", HOJE, 8, 9, 7, "Ana")


# RR04
def test_conflito_sobreposicao():
    s = novo_sistema()
    s.reservar("Azul", HOJE, 10, 12, 2, "Ana")
    with pytest.raises(ConflitoDeHorarioError):
        s.reservar("Azul", HOJE, 11, 13, 2, "Bia")
    with pytest.raises(ConflitoDeHorarioError):
        s.reservar("Azul", HOJE, 9, 11, 2, "Bia")
    with pytest.raises(ConflitoDeHorarioError):
        s.reservar("Azul", HOJE, 10, 11, 2, "Bia")


def test_reservas_encostadas_nao_conflitam():
    s = novo_sistema()
    s.reservar("Azul", HOJE, 10, 12, 2, "Ana")
    s.reservar("Azul", HOJE, 12, 14, 2, "Bia")
    s.reservar("Azul", HOJE, 8, 10, 2, "Caio")
    assert [r.inicio for r in s.listar("Azul", HOJE)] == [8, 10, 12]


def test_sem_conflito_em_outra_sala_ou_data():
    s = novo_sistema()
    s.reservar("Azul", HOJE, 10, 12, 2, "Ana")
    s.reservar("Verde", HOJE, 10, 12, 2, "Bia")
    s.reservar("Azul", AMANHA, 10, 12, 2, "Caio")


# RR05 / RR06
def test_cancelar_libera_horario():
    s = novo_sistema()
    rid = s.reservar("Azul", HOJE, 10, 12, 2, "Ana")
    s.cancelar(rid)
    assert s.buscar(rid).ativa is False
    s.reservar("Azul", HOJE, 10, 12, 2, "Bia")


def test_cancelar_invalido():
    s = novo_sistema()
    rid = s.reservar("Azul", HOJE, 10, 12, 2, "Ana")
    with pytest.raises(ReservaInexistenteError):
        s.cancelar(99)
    s.cancelar(rid)
    with pytest.raises(ReservaInvalidaError):
        s.cancelar(rid)


def test_buscar_inexistente():
    s = novo_sistema()
    with pytest.raises(ReservaInexistenteError):
        s.buscar(1)


# RR07 / RR08 / RR09
def test_listar_ignora_canceladas_e_ordena():
    s = novo_sistema()
    a = s.reservar("Azul", HOJE, 15, 16, 2, "Ana")
    s.reservar("Azul", HOJE, 9, 10, 2, "Bia")
    s.cancelar(a)
    assert [r.inicio for r in s.listar("Azul", HOJE)] == [9]


def test_horarios_livres_e_ocupacao():
    s = novo_sistema()
    s.reservar("Azul", HOJE, 8, 10, 2, "Ana")
    s.reservar("Azul", HOJE, 20, 22, 2, "Bia")
    assert s.horarios_livres("Azul", HOJE) == list(range(10, 20))
    assert s.ocupacao("Azul", HOJE) == 28.6


def test_horarios_livres_sala_inexistente():
    s = novo_sistema()
    with pytest.raises(ReservaInvalidaError):
        s.horarios_livres("Roxa", HOJE)
