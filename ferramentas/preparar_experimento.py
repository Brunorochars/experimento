"""Gera as versões defeituosas, as entradas dos assistentes, o gabarito e a ordem das execuções.

Rode a partir da pasta do experimento:
    python ferramentas/preparar_experimento.py
"""

import csv
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
from defeitos import DEFEITOS  # noqa: E402

PROGRAMAS = {
    "banco": "Controle bancário",
    "carrinho": "Carrinho de compras",
    "reservas": "Sistema de reservas",
    "notas": "Gerenciamento de notas",
}
ASSISTENTES = ["Codex", "Claude", "Antigravity", "GitHub Copilot"]
EXECUCOES = 3
SEMENTE = 2026

# Prompt padronizado (Seção 4.4 do artigo), sem alterações.
PROMPT = (
    "Atue como revisor de código. Analise os requisitos e o código Python apresentados "
    "e identifique possíveis defeitos funcionais que possam produzir um comportamento "
    "diferente do especificado. Para cada problema encontrado, informe: (1) a localização "
    "aproximada; (2) a descrição do problema; (3) a justificativa baseada no código e nos "
    "requisitos; e (4) uma possível correção. Não presuma requisitos que não estejam "
    "declarados. Caso não encontre defeitos, informe isso explicitamente."
)


def gerar_defeituosas():
    linhas_defeito = {}
    for prog in PROGRAMAS:
        defeitos = [d for d in DEFEITOS if d["programa"] == prog]
        arquivo = defeitos[0]["arquivo"]
        codigo = (RAIZ / "programas" / prog / "correta" / arquivo).read_text(encoding="utf-8")
        for d in defeitos:
            ocorrencias = codigo.count(d["original"])
            if ocorrencias != 1:
                raise SystemExit(f"{d['codigo']}: trecho original aparece {ocorrencias} vezes")
            codigo = codigo.replace(d["original"], d["defeituoso"])
        destino = RAIZ / "programas" / prog / "defeituosa" / arquivo
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(codigo, encoding="utf-8")
        linhas = codigo.splitlines()
        for d in defeitos:
            alvo = d["defeituoso"].splitlines()[0]
            linhas_defeito[d["codigo"]] = [i + 1 for i, l in enumerate(linhas) if l == alvo]
    return linhas_defeito


def gerar_entradas():
    """Cria um texto pronto para colar por programa e versão, com rótulo neutro (A/B)."""
    rnd = random.Random(SEMENTE)
    pasta = RAIZ / "entradas"
    pasta.mkdir(exist_ok=True)
    mapa = {}
    for prog in PROGRAMAS:
        rotulos = ["A", "B"]
        rnd.shuffle(rotulos)
        requisitos = (RAIZ / "programas" / prog / "requisitos.md").read_text(encoding="utf-8")
        for versao, rotulo in zip(["correta", "defeituosa"], rotulos):
            arquivo = next((RAIZ / "programas" / prog / versao).glob("*.py"))
            codigo = arquivo.read_text(encoding="utf-8")
            texto = (
                f"{PROMPT}\n\n"
                f"=== REQUISITOS ===\n\n{requisitos.strip()}\n\n"
                f"=== CÓDIGO ({arquivo.name}) ===\n\n```python\n{codigo.rstrip()}\n```\n"
            )
            nome = f"{prog}_{rotulo}.txt"
            (pasta / nome).write_text(texto, encoding="utf-8")
            mapa[(prog, versao)] = nome
    return mapa


def gerar_ordem(mapa):
    rnd = random.Random(SEMENTE + 1)
    entradas = [(prog, versao) for prog in PROGRAMAS for versao in ("correta", "defeituosa")]
    caminho = RAIZ / "ordem_execucoes.csv"
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "id_resposta", "assistente", "execucao", "ordem_na_rodada", "programa",
            "versao", "arquivo_entrada", "arquivo_resposta", "data", "modelo",
            "interface", "tipo_de_acesso", "configuracoes", "observacoes",
        ])
        n = 0
        for assistente in ASSISTENTES:
            for execucao in range(1, EXECUCOES + 1):
                ordem = entradas[:]
                rnd.shuffle(ordem)
                for i, (prog, versao) in enumerate(ordem, 1):
                    n += 1
                    rid = f"R{n:03d}"
                    w.writerow([
                        rid, assistente, execucao, i, prog, versao, mapa[(prog, versao)],
                        f"respostas/{rid}.md", "", "", "", "", "", "",
                    ])
    return n


def gerar_gabarito(linhas_defeito, mapa):
    out = [
        "# Gabarito dos defeitos semeados",
        "",
        "**Uso restrito do grupo. Não enviar aos assistentes.**",
        "",
        "## Correspondência das entradas",
        "",
        "| Programa | Versão correta | Versão defeituosa |",
        "|---|---|---|",
    ]
    for prog, nome in PROGRAMAS.items():
        out.append(f"| {nome} | `{mapa[(prog, 'correta')]}` | `{mapa[(prog, 'defeituosa')]}` |")
    out += ["", "## Defeitos", ""]
    for prog, nome in PROGRAMAS.items():
        out += [f"### {nome} (`{prog}`)", ""]
        for d in [x for x in DEFEITOS if x["programa"] == prog]:
            linhas = ", ".join(str(n) for n in linhas_defeito[d["codigo"]])
            original = d["original"].strip().splitlines()
            defeituoso = d["defeituoso"].strip().splitlines()
            out += [
                f"#### {d['codigo']} — {d['categoria']}",
                "",
                f"- **Localização:** `{d['arquivo']}`, {d['metodo']}, linha {linhas} da versão defeituosa",
                f"- **Requisito violado:** {d['requisito']}",
                f"- **Código correto:** `{' / '.join(l.strip() for l in original)}`",
                f"- **Código defeituoso:** `{' / '.join(l.strip() for l in defeituoso)}`",
                f"- **Comportamento esperado:** {d['esperado']}",
                f"- **Comportamento observado:** {d['observado']}",
                f"- **Teste que demonstra:** `{d['teste']}`",
                "",
            ]
    (RAIZ / "gabarito.md").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    linhas = gerar_defeituosas()
    mapa = gerar_entradas()
    total = gerar_ordem(mapa)
    gerar_gabarito(linhas, mapa)
    print(f"Versões defeituosas, 8 entradas, gabarito e {total} execuções gerados.")
