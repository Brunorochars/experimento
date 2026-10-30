"""Roda as revisões do Claude via Claude Code em modo não interativo (claude -p).

Cada revisão roda numa pasta temporária vazia e nova, sem ferramentas, sem CLAUDE.md
nem memória, e recebe pelo stdin só o conteúdo de entradas/<arquivo_entrada>.
Uma falha não é repetida: a linha fica em branco e a execução para.

Rode a partir da pasta do experimento:
    python ferramentas/rodar_claude.py R025          # uma ou mais revisões por id
    python ferramentas/rodar_claude.py --pendentes   # todas as do Claude com data vazia
"""

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "ordem_execucoes.csv"

ASSISTENTE = "Claude"
MODELO = "claude-opus-5-5"
SYSTEM_PROMPT = "Você é um assistente."
TIPO_DE_ACESSO = "Team (assinatura de organização)"
CONFIGURACOES = (
    "esforço médio; sem ferramentas; --safe-mode (sem CLAUDE.md/memória); "
    f'system prompt mínimo ("{SYSTEM_PROMPT}"); sem persistência de sessão'
)
OBSERVACOES = (
    "O Claude Code injeta no contexto um bloco de ambiente (pasta temporária, SO, data) "
    "e o e-mail do usuário"
)


def comando(claude):
    return [
        claude, "-p", "--safe-mode", "--tools", "", "--model", MODELO,
        "--effort", "medium", "--no-session-persistence",
        "--system-prompt", SYSTEM_PROMPT, "--output-format", "json",
    ]


def versao_cli(claude):
    saida = subprocess.run([claude, "--version"], capture_output=True, text=True, check=True)
    return saida.stdout.split()[0]


def revisar(claude, entrada):
    """Devolve (texto, modelos) ou levanta RuntimeError. Nunca tenta de novo."""
    with tempfile.TemporaryDirectory(prefix="revisao_") as pasta:
        proc = subprocess.run(comando(claude), input=entrada, cwd=pasta, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"código de saída {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')[:500]}")
    try:
        saida = json.loads(proc.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise RuntimeError(f"JSON inválido: {e}")
    if saida.get("is_error"):
        raise RuntimeError(f"is_error na saída: {saida.get('subtype')}")
    texto = saida.get("result") or ""
    if not texto.strip():
        raise RuntimeError("result vazio")
    modelos = sorted(saida.get("modelUsage", {}))
    if modelos != [MODELO]:
        raise RuntimeError(f"modelos inesperados em modelUsage: {modelos}")
    return texto, modelos


def ler_csv():
    with CSV.open(newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        return leitor.fieldnames, list(leitor)


def gravar_csv(campos, linhas):
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def selecionar(linhas, args):
    do_claude = [l for l in linhas if l["assistente"] == ASSISTENTE]
    if args == ["--pendentes"]:
        return [l for l in do_claude if not l["data"]]
    ids = set(args)
    escolhidas = [l for l in do_claude if l["id_resposta"] in ids]
    faltando = ids - {l["id_resposta"] for l in escolhidas}
    if faltando:
        raise SystemExit(f"ids que não são do {ASSISTENTE}: {', '.join(sorted(faltando))}")
    preenchidas = [l["id_resposta"] for l in escolhidas if l["data"]]
    if preenchidas:
        raise SystemExit(f"já preenchidas no CSV: {', '.join(preenchidas)}")
    return escolhidas


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if not TIPO_DE_ACESSO:
        raise SystemExit("defina TIPO_DE_ACESSO antes de rodar")
    claude = shutil.which("claude")
    if not claude:
        raise SystemExit("claude não encontrado no PATH")
    interface = f"Claude Code CLI {versao_cli(claude)} (claude -p), pasta vazia"

    campos, linhas = ler_csv()
    fila = selecionar(linhas, sys.argv[1:])
    print(f"{len(fila)} revisão(ões) na fila.")
    for linha in fila:
        rid = linha["id_resposta"]
        entrada = (RAIZ / "entradas" / linha["arquivo_entrada"]).read_bytes()
        print(f"{rid} ({linha['arquivo_entrada']})... ", end="", flush=True)
        try:
            texto, modelos = revisar(claude, entrada)
        except RuntimeError as e:
            print(f"FALHOU: {e}")
            raise SystemExit(f"Parado em {rid}; a linha ficou em branco e não foi repetida.")
        (RAIZ / linha["arquivo_resposta"]).write_text(texto, encoding="utf-8", newline="")
        linha.update({
            "data": date.today().isoformat(),
            "modelo": "; ".join(modelos),
            "interface": interface,
            "tipo_de_acesso": TIPO_DE_ACESSO,
            "configuracoes": CONFIGURACOES,
            "observacoes": OBSERVACOES,
        })
        gravar_csv(campos, linhas)
        print("ok")
