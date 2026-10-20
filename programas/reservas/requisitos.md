# Requisitos — Sistema de reservas de salas (`reservas.py`)

Horários são horas inteiras de 0 a 24. Uma reserva das 10 às 12 ocupa o intervalo [10, 12): começa às 10 e termina às 12.

## Sistema

- **RR01** — O sistema é criado com um dicionário `{nome_da_sala: capacidade}` e com a data de hoje. Toda capacidade deve ser maior ou igual a 1 (`ValueError`).
- **RR02** — `reservar(sala, data, inicio, fim, participantes, responsavel)` cria uma reserva ativa e retorna seu identificador. Os identificadores são inteiros sequenciais começando em 1.
- **RR03** — Validações da reserva (todas lançam `ReservaInvalidaError`):
  - a sala deve existir;
  - a data deve ser um `date` igual ou posterior à data de hoje do sistema;
  - início e fim devem ser inteiros;
  - o funcionamento é das 8h às 22h: o início não pode ser antes das 8 e o fim não pode ser depois das 22;
  - o início deve ser anterior ao fim;
  - a duração (fim − início) é de no máximo 4 horas;
  - o número de participantes deve ser no mínimo 1 e no máximo a capacidade da sala;
  - o responsável deve ser um texto não vazio (espaços nas extremidades são removidos ao salvar).
- **RR04 — Duas reservas ativas da mesma sala, na mesma data, não podem ter intervalos sobrepostos; nesse caso lança `ConflitoDeHorarioError`. Reservas encostadas** não se sobrepõem: se uma termina às 10, outra pode começar às 10.
- **RR05 — `cancelar(id)`: id inexistente lança `ReservaInexistenteError`; reserva já cancelada lança `ReservaInvalidaError`. A reserva cancelada deixa de estar ativa e libera o horário** para novas reservas.
- **RR06** — `buscar(id)` retorna a reserva (ativa ou cancelada); id inexistente lança `ReservaInexistenteError`.
- **RR07** — `listar(sala, data)` retorna as reservas ativas da sala na data, ordenadas pelo horário de início.
- **RR08** — `horarios_livres(sala, data)` retorna a lista das horas de início de 8 a 21 que não estão ocupadas por reservas ativas. Sala inexistente lança `ReservaInvalidaError`.
- **RR09** — `ocupacao(sala, data)` retorna o percentual de horas ocupadas no dia (das 14 horas de funcionamento), arredondado para 1 casa decimal.
