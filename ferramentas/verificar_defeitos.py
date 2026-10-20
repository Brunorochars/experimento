"""Confere o material antes dos testes com os assistentes.

1. A versão correta passa em todos os testes.
2. Cada defeito, aplicado sozinho, faz falhar exatamente os testes listados no gabarito
   (o que indica que um defeito não interfere no efeito de outro).
3. Na versão defeituosa completa, falham apenas os testes dos três defeitos.
4. Cada programa tem entre 80 e 150 linhas.

    python ferramentas/verificar_defeitos.py
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
from defeitos import DEFEITOS  # noqa: E402


def falhas(pasta_codigo, pasta_testes):
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-rf", "-p", "no:cacheprovider",
         "--noconftest", str(pasta_testes)],
        capture_output=True, text=True,
        env={"PYTHONPATH": str(pasta_codigo), "PATH": ""},
    )
    nomes = set(re.findall(r"^FAILED \S+::(\S+)", r.stdout, re.M))
    if r.returncode not in (0, 1):
        print(r.stdout, r.stderr)
        raise SystemExit("erro ao rodar pytest")
    return nomes


def esperados(d):
    return {t.strip() for t in d["teste"].split(",")}


def casa(falhou, esperado):
    """Um teste parametrizado listado sem [..] cobre todas as suas variações."""
    def cobre(f, e):
        return f == e or f.split("[")[0] == e

    sem_explicacao = {f for f in falhou if not any(cobre(f, e) for e in esperado)}
    sem_falha = {e for e in esperado if not any(cobre(f, e) for f in falhou)}
    return not sem_explicacao and not sem_falha


ok = True
programas = sorted({d["programa"] for d in DEFEITOS})
for prog in programas:
    base = RAIZ / "programas" / prog
    testes = base / "tests"
    arquivo = next((base / "correta").glob("*.py"))
    n_linhas = len(arquivo.read_text(encoding="utf-8").splitlines())
    print(f"\n== {prog} ({n_linhas} linhas) ==")
    if not 80 <= n_linhas <= 150:
        print("  ! fora da faixa de 80 a 150 linhas"); ok = False

    f = falhas(base / "correta", testes)
    print(f"  correta: {'todos os testes passam' if not f else 'FALHAS ' + str(sorted(f))}")
    ok &= not f

    for d in [x for x in DEFEITOS if x["programa"] == prog]:
        with tempfile.TemporaryDirectory() as tmp:
            codigo = arquivo.read_text(encoding="utf-8").replace(d["original"], d["defeituoso"])
            Path(tmp, arquivo.name).write_text(codigo, encoding="utf-8")
            f = falhas(tmp, testes)
        bate = casa(f, esperados(d))
        print(f"  {d['codigo']} sozinho: {'OK' if bate else 'DIVERGE'} -> {sorted(f)}")
        ok &= bate

    f = falhas(base / "defeituosa", testes)
    todos = set().union(*(esperados(d) for d in DEFEITOS if d["programa"] == prog))
    bate = casa(f, todos)
    print(f"  defeituosa completa: {'OK' if bate else 'DIVERGE'} ({len(f)} testes falham)")
    ok &= bate

print("\nTUDO CERTO" if ok else "\nHÁ PROBLEMAS")
sys.exit(0 if ok else 1)
