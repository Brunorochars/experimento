"""Gerenciamento de notas de uma turma."""


class AlunoInexistenteError(Exception):
    pass


class AlunoDuplicadoError(Exception):
    pass


class NotaInvalidaError(Exception):
    pass


class ExameNaoPermitidoError(Exception):
    pass


PESOS = {"P1": 0.35, "P2": 0.30, "T": 0.35}
MEDIA_APROVACAO = 7.0
MEDIA_MINIMA_EXAME = 5.0
MEDIA_FINAL_APROVACAO = 5.0
FREQUENCIA_MINIMA = 75.0


class Aluno:
    def __init__(self, matricula, nome):
        self.matricula = matricula
        self.nome = nome
        self.notas = {}
        self.frequencia = None
        self.exame = None


class Turma:
    def __init__(self):
        self._alunos = {}

    def adicionar_aluno(self, matricula, nome):
        if matricula in self._alunos:
            raise AlunoDuplicadoError(f"matrícula {matricula} já cadastrada")
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("nome inválido")
        self._alunos[matricula] = Aluno(matricula, nome.strip())

    def _aluno(self, matricula):
        if matricula not in self._alunos:
            raise AlunoInexistenteError(f"matrícula {matricula} não encontrada")
        return self._alunos[matricula]

    def _validar_nota(self, nota):
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota deve ser numérica")
        if nota < 0:
            raise NotaInvalidaError("nota fora do intervalo")

    def lancar_nota(self, matricula, avaliacao, nota):
        aluno = self._aluno(matricula)
        if avaliacao not in PESOS:
            raise NotaInvalidaError(f"avaliação {avaliacao} inexistente")
        self._validar_nota(nota)
        aluno.notas[avaliacao] = float(nota)

    def registrar_frequencia(self, matricula, percentual):
        aluno = self._aluno(matricula)
        if not 0 <= percentual <= 100:
            raise ValueError("frequência fora do intervalo")
        aluno.frequencia = float(percentual)

    def media(self, matricula):
        aluno = self._aluno(matricula)
        soma = sum(aluno.notas.get(av, 0.0) * peso for av, peso in PESOS.items())
        return round(soma, 2)

    def situacao(self, matricula):
        aluno = self._aluno(matricula)
        if aluno.frequencia is None:
            return "Pendente"
        if aluno.frequencia <= FREQUENCIA_MINIMA:
            return "Reprovado por frequência"
        media = self.media(matricula)
        if media >= MEDIA_APROVACAO:
            return "Aprovado"
        if media < MEDIA_MINIMA_EXAME:
            return "Reprovado"
        if aluno.exame is None:
            return "Exame"
        if self.media_final(matricula) >= MEDIA_FINAL_APROVACAO:
            return "Aprovado"
        return "Reprovado"

    def lancar_exame(self, matricula, nota):
        aluno = self._aluno(matricula)
        if self.situacao(matricula) != "Exame":
            raise ExameNaoPermitidoError("aluno não está em exame")
        self._validar_nota(nota)
        aluno.exame = float(nota)

    def media_final(self, matricula):
        aluno = self._aluno(matricula)
        media = self.media(matricula)
        if aluno.exame is None:
            return media
        return round((media + aluno.exame) / 2, 2)

    def ranking(self):
        medias = [(m, self.media(m)) for m in self._alunos]
        return sorted(medias, key=lambda item: (-item[1], item[0]))
