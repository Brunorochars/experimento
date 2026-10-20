"""Permite rodar os testes contra a versão correta ou a defeituosa.

Uso:
    pytest programas --versao=correta
    pytest programas --versao=defeituosa
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).parent


def pytest_addoption(parser):
    parser.addoption(
        "--versao",
        default="correta",
        choices=["correta", "defeituosa"],
        help="versão dos programas a testar",
    )


def pytest_configure(config):
    versao = config.getoption("--versao")
    for pasta in sorted((RAIZ / "programas").glob(f"*/{versao}")):
        sys.path.insert(0, str(pasta))
