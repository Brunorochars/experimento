# Material do experimento — Alucinações de LLMs como revisores de código

Material da Seção 4 do artigo (AL0342, Squad 07): quatro programas Python, cada um com versão correta e versão com três defeitos semeados, testes pytest, gabarito, entradas prontas para os assistentes e ordem das 96 revisões.

## Estrutura

```
programas/<programa>/
    requisitos.md        requisitos escritos (vão para o assistente)
    correta/<prog>.py    versão correta, passa em todos os testes
    defeituosa/<prog>.py versão com 3 defeitos (gerada a partir da correta)
    tests/test_<prog>.py testes pytest (NÃO vão para o assistente)
entradas/                 8 textos prontos para colar (prompt + requisitos + código)
gabarito.md               12 defeitos: código, local, esperado, observado, teste (NÃO enviar)
ordem_execucoes.csv       96 revisões em ordem alternada, com campos de registro (Seção 4.3)
ferramentas/
    defeitos.py               definição dos defeitos (fonte do gabarito)
    preparar_experimento.py   gera defeituosas, entradas, gabarito e ordem
    verificar_defeitos.py     confere testes, independência dos defeitos e tamanho
conftest.py               opção --versao do pytest
```

| Programa | Linhas | Defeitos |
|---|---|---|
| Controle bancário (`banco`) | 121 | D01 valor-limite · D02 cálculo · D03 atualização de dados |
| Carrinho de compras (`carrinho`) | 120 | D04 condição · D05 validação de entrada · D06 cálculo |
| Sistema de reservas (`reservas`) | 110 | D07 valor-limite · D08 validação de entrada · D09 condição |
| Gerenciamento de notas (`notas`) | 109 | D10 cálculo · D11 validação de entrada · D12 valor-limite |

As duas versões de cada programa diferem **apenas** nas linhas dos defeitos. Cada defeito, aplicado sozinho, faz falhar só os testes listados no gabarito, o que atende ao critério de que um defeito não interfira no efeito de outro (Seção 4.2).

## Conferir o material

```bash
pip install pytest
pytest programas --versao=correta      # 113 testes passam
pytest programas --versao=defeituosa   # 16 testes falham, todos ligados aos 12 defeitos
python ferramentas/verificar_defeitos.py
```

Se alterar algum programa ou defeito, edite `correta/` ou `ferramentas/defeitos.py` e rode `python ferramentas/preparar_experimento.py` para regenerar tudo.

## Procedimento (Seção 4.4)

1. Siga `ordem_execucoes.csv`. Cada linha é uma revisão; dentro de cada rodada (assistente × execução) a ordem dos programas e versões é sorteada.
2. Abra **uma conversa nova** para cada linha, sem histórico nem memória de conversas anteriores.
3. Copie e cole o conteúdo inteiro do arquivo de `entradas/` indicado. Não acrescente nada: os assistentes não podem saber se a versão é correta nem quantos defeitos existem. Os nomes `A`/`B` são neutros; a correspondência está só no gabarito.
4. Salve a resposta completa em `respostas/<id_resposta>.md` e preencha no CSV data, modelo, interface, tipo de acesso e configurações. Se a ferramenta não informar o modelo, anote isso em observações.
5. Nunca envie `tests/`, `gabarito.md`, `ferramentas/` ou o CSV aos assistentes.

**Piloto (Seção 4.1):** antes da rodada principal, rode 2 programas × 2 assistentes para testar requisitos, prompt e gabarito. Se algo mudar, descarte as respostas do piloto.

## Classificação (Seções 4.5 a 4.7)

- Para a anotação cega, entregue aos dois avaliadores apenas os arquivos `respostas/Rxxx.md` (o id não revela o assistente), com código, requisitos, testes e gabarito. Após o consenso, cruze os ids com o CSV.
- Cada apontamento recebe Sim/Não em: defeito verdadeiro identificado (com o código Dxx), falso alarme, alucinação e comentário correto. Falso alarme e alucinação são registrados de forma independente.
- Um apontamento conta como **defeito encontrado** quando indica o defeito do gabarito e sua localização aproximada (trecho ou linha), mesmo que a explicação contenha alucinação.
- Nas versões corretas, qualquer apontamento de defeito funcional é falso alarme.
- Defeitos não mencionados em uma execução vão para a parte de "defeitos não encontrados".
- Toda decisão cita evidência: linha do código, requisito ou teste.
