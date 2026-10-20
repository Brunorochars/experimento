# Requisitos — Gerenciamento de notas (`notas.py`)

## Alunos

- **RN01** — `adicionar_aluno(matricula, nome)`: matrícula já cadastrada lança `AlunoDuplicadoError`; nome deve ser texto não vazio (`ValueError`; espaços nas extremidades são removidos).
- **RN02** — Qualquer operação com matrícula não cadastrada lança `AlunoInexistenteError`.

## Notas e frequência

- **RN03** — `lancar_nota(matricula, avaliacao, nota)`: as avaliações são `P1`, `P2` e `T` (trabalho); outra avaliação lança `NotaInvalidaError`. A nota deve ser numérica (`TypeError`; booleanos não são aceitos) e estar entre 0 e 10, inclusive (`NotaInvalidaError` fora desse intervalo). Lançar novamente substitui a nota anterior.
- **RN04** — `registrar_frequencia(matricula, percentual)`: percentual entre 0 e 100, inclusive (`ValueError` fora do intervalo).

## Média e situação

- **RN05 — `media(matricula)` é a média ponderada: P1 com peso 35%, P2 com peso 35% e T com peso 30%**. Avaliação sem nota lançada conta como 0. O resultado é arredondado para 2 casas.
- **RN06** — `situacao(matricula)`, avaliada nesta ordem:
  1. sem frequência registrada → `"Pendente"`;
  2. frequência menor que 75% → `"Reprovado por frequência"` (75% exatos não reprovam por frequência);
  3. média ≥ 7,0 → `"Aprovado"`;
  4. média < 5,0 → `"Reprovado"`;
  5. média entre 5,0 (inclusive) e 7,0 sem nota de exame → `"Exame"`;
  6. com nota de exame: média final ≥ 5,0 → `"Aprovado"`, senão `"Reprovado"`.
- **RN07** — `lancar_exame(matricula, nota)`: só é permitido quando a situação do aluno é `"Exame"` (caso contrário, `ExameNaoPermitidoError`). A nota segue a mesma validação de RN03.
- **RN08** — `media_final(matricula)`: sem exame, é igual à média; com exame, é `(média + exame) / 2`, arredondada para 2 casas.
- **RN09** — `ranking()` retorna a lista de pares `(matricula, media)` de todos os alunos, em ordem decrescente de média; empates são ordenados pela matrícula em ordem crescente.
