import pytest

from notas import (
    AlunoDuplicadoError,
    AlunoInexistenteError,
    ExameNaoPermitidoError,
    NotaInvalidaError,
    Turma,
)


def turma_com_aluno(p1=None, p2=None, t=None, freq=None, matricula="001"):
    turma = Turma()
    turma.adicionar_aluno(matricula, "Ana")
    for av, nota in (("P1", p1), ("P2", p2), ("T", t)):
        if nota is not None:
            turma.lancar_nota(matricula, av, nota)
    if freq is not None:
        turma.registrar_frequencia(matricula, freq)
    return turma


# RN01 / RN02
def test_aluno_duplicado():
    turma = turma_com_aluno()
    with pytest.raises(AlunoDuplicadoError):
        turma.adicionar_aluno("001", "Bia")


def test_nome_invalido():
    turma = Turma()
    with pytest.raises(ValueError):
        turma.adicionar_aluno("002", "  ")


def test_aluno_inexistente():
    turma = Turma()
    with pytest.raises(AlunoInexistenteError):
        turma.lancar_nota("999", "P1", 5)
    with pytest.raises(AlunoInexistenteError):
        turma.media("999")


# RN03 / RN04
def test_avaliacao_inexistente():
    turma = turma_com_aluno()
    with pytest.raises(NotaInvalidaError):
        turma.lancar_nota("001", "P3", 5)


@pytest.mark.parametrize("nota", [0, 10, 7.5])
def test_nota_nos_limites(nota):
    turma = turma_com_aluno()
    turma.lancar_nota("001", "P1", nota)


@pytest.mark.parametrize("nota", [-0.5, 10.5, 11])
def test_nota_fora_do_intervalo(nota):
    turma = turma_com_aluno()
    with pytest.raises(NotaInvalidaError):
        turma.lancar_nota("001", "P1", nota)


def test_nota_nao_numerica():
    turma = turma_com_aluno()
    with pytest.raises(TypeError):
        turma.lancar_nota("001", "P1", "8")


def test_relancar_substitui_nota():
    turma = turma_com_aluno(p1=4, p2=4, t=4)
    turma.lancar_nota("001", "P1", 10)
    assert turma.media("001") == 6.1


@pytest.mark.parametrize("freq", [-1, 100.1])
def test_frequencia_invalida(freq):
    turma = turma_com_aluno()
    with pytest.raises(ValueError):
        turma.registrar_frequencia("001", freq)


# RN05
def test_media_notas_iguais():
    assert turma_com_aluno(p1=8, p2=8, t=8).media("001") == 8


def test_media_pesos_das_provas():
    assert turma_com_aluno(p1=0, p2=10, t=0).media("001") == 3.5
    assert turma_com_aluno(p1=10, p2=0, t=0).media("001") == 3.5


def test_media_peso_do_trabalho():
    assert turma_com_aluno(p1=0, p2=0, t=10).media("001") == 3.0


def test_media_avaliacao_faltante_conta_zero():
    assert turma_com_aluno(p1=10, p2=10).media("001") == 7.0


# RN06
def test_situacao_pendente():
    assert turma_com_aluno(p1=9, p2=9, t=9).situacao("001") == "Pendente"


def test_reprovado_por_frequencia():
    assert turma_com_aluno(p1=9, p2=9, t=9, freq=74.9).situacao("001") == "Reprovado por frequência"


def test_frequencia_exatamente_75_nao_reprova():
    assert turma_com_aluno(p1=8, p2=8, t=8, freq=75).situacao("001") == "Aprovado"


@pytest.mark.parametrize(
    "notas, esperado",
    [((7, 7, 7), "Aprovado"), ((4, 4, 4), "Reprovado"), ((6, 6, 6), "Exame"), ((5, 5, 5), "Exame")],
)
def test_situacao_por_media(notas, esperado):
    p1, p2, t = notas
    assert turma_com_aluno(p1=p1, p2=p2, t=t, freq=90).situacao("001") == esperado


# RN07 / RN08
def test_exame_aprova():
    turma = turma_com_aluno(p1=6, p2=6, t=6, freq=90)
    turma.lancar_exame("001", 4)
    assert turma.media_final("001") == 5.0
    assert turma.situacao("001") == "Aprovado"


def test_exame_reprova():
    turma = turma_com_aluno(p1=6, p2=6, t=6, freq=90)
    turma.lancar_exame("001", 3)
    assert turma.media_final("001") == 4.5
    assert turma.situacao("001") == "Reprovado"


def test_exame_nao_permitido():
    turma = turma_com_aluno(p1=8, p2=8, t=8, freq=90)
    with pytest.raises(ExameNaoPermitidoError):
        turma.lancar_exame("001", 5)


def test_media_final_sem_exame():
    assert turma_com_aluno(p1=8, p2=8, t=8).media_final("001") == 8


# RN09
def test_ranking():
    turma = Turma()
    for matricula, nota in (("003", 6), ("001", 8), ("002", 6)):
        turma.adicionar_aluno(matricula, "Aluno")
        for av in ("P1", "P2", "T"):
            turma.lancar_nota(matricula, av, nota)
    assert turma.ranking() == [("001", 8.0), ("002", 6.0), ("003", 6.0)]
