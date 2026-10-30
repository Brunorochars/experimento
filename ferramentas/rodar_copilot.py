"""Roda as revisões do GitHub Copilot via Copilot CLI em modo não interativo (copilot -p).

Cada revisão roda numa pasta temporária vazia e nova, sem ferramentas e sem servidores
MCP, e recebe como prompt só o conteúdo de entradas/<arquivo_entrada>. No plano Copilot
Free o modelo não pode ser fixado (--model é recusado): o modo Auto escolhe, e o modelo
de cada revisão fica registrado no CSV e no log em registros/copilot/<id>.jsonl.
Uma falha não é repetida: a linha fica em branco e a execução para.

Rode a partir da pasta do experimento:
    python ferramentas/rodar_copilot.py R073          # uma ou mais revisões por id
    python ferramentas/rodar_copilot.py --pendentes   # todas as do Copilot com data vazia
"""

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "ordem_execucoes.csv"
REGISTROS = RAIZ / "registros" / "copilot"

ASSISTENTE = "GitHub Copilot"
TIPO_DE_ACESSO = "Copilot Free (conta individual do GitHub)"
CONFIGURACOES = (
    "modo Auto (único modelo disponível no plano: {modelo}); sem ferramentas; "
    "sem servidores MCP; memória desligada; sessão nova por revisão"
)
# O raciocínio criptografado e os eventos de streaming não são legíveis nem acrescentam
# nada à resposta final; sem eles o log cai de ~400 KB para ~20 KB por revisão.
CAMPOS_OPACOS = {"reasoningOpaque", "encryptedContent", "reasoningBlocks"}


def comando(copilot, pasta, entrada):
    return [
        copilot, "-C", pasta, "-p", entrada, "--available-tools", "--disable-builtin-mcps",
        "--no-auto-update", "--output-format", "json",
    ]


def versao_cli(copilot):
    saida = subprocess.run([copilot, "--version"], capture_output=True, text=True, check=True)
    return saida.stdout.split()[3].rstrip(".")


def reduzir(eventos):
    reduzidos = []
    for evento in eventos:
        if evento.get("ephemeral"):
            continue
        dados = {k: v for k, v in evento.get("data", {}).items() if k not in CAMPOS_OPACOS}
        reduzidos.append({**evento, "data": dados} if "data" in evento else evento)
    return reduzidos


def revisar(copilot, entrada):
    """Devolve (texto, modelo, eventos reduzidos) ou levanta RuntimeError. Nunca tenta de novo."""
    with tempfile.TemporaryDirectory(prefix="revisao_") as pasta:
        proc = subprocess.run(comando(copilot, pasta, entrada), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"código de saída {proc.returncode}: {proc.stderr[:500]}")
    try:
        eventos = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON inválido: {e}")
    mensagens = [e["data"] for e in eventos if e["type"] == "assistant.message"]
    texto = "\n\n".join(m["content"] for m in mensagens if m.get("content")).strip()
    if not texto:
        raise RuntimeError("resposta vazia")
    modelos = sorted({m["model"] for m in mensagens})
    if len(modelos) != 1:
        raise RuntimeError(f"mais de um modelo na mesma revisão: {modelos}")
    return texto + "\n", modelos[0], reduzir(eventos)


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
    do_copilot = [l for l in linhas if l["assistente"] == ASSISTENTE]
    if args == ["--pendentes"]:
        return [l for l in do_copilot if not l["data"]]
    ids = set(args)
    escolhidas = [l for l in do_copilot if l["id_resposta"] in ids]
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
    copilot = shutil.which("copilot")
    if not copilot:
        raise SystemExit("copilot não encontrado no PATH")
    interface = f"GitHub Copilot CLI {versao_cli(copilot)} (copilot -p), pasta vazia"
    REGISTROS.mkdir(parents=True, exist_ok=True)

    campos, linhas = ler_csv()
    fila = selecionar(linhas, sys.argv[1:])
    print(f"{len(fila)} revisão(ões) na fila.")
    for linha in fila:
        rid = linha["id_resposta"]
        entrada = (RAIZ / "entradas" / linha["arquivo_entrada"]).read_text(encoding="utf-8")
        inicio = datetime.now()
        print(f"{rid} ({linha['arquivo_entrada']})... ", end="", flush=True)
        try:
            texto, modelo, eventos = revisar(copilot, entrada)
        except RuntimeError as e:
            print(f"FALHOU: {e}")
            raise SystemExit(f"Parado em {rid}; a linha ficou em branco e não foi repetida.")
        (RAIZ / linha["arquivo_resposta"]).write_text(texto, encoding="utf-8")
        (REGISTROS / f"{rid}.jsonl").write_text(
            "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in eventos), encoding="utf-8")
        linha.update({
            "data": inicio.date().isoformat(),
            "modelo": modelo,
            "interface": interface,
            "tipo_de_acesso": TIPO_DE_ACESSO,
            "configuracoes": CONFIGURACOES.format(modelo=modelo),
            "observacoes": (f"Horário da execução: {inicio:%H:%M}. O modelo foi escolhido pelo "
                            f"modo Auto; o log da sessão está em registros/copilot/{rid}.jsonl."),
        })
        gravar_csv(campos, linhas)
        print(f"ok ({modelo})")
