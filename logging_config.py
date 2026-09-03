"""Configuração centralizada de logs da aplicação."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from conf import LOG_ARQUIVO, LOG_BACKUP_COUNT, LOG_MAX_BYTES, LOG_NIVEL


def configurar_logging() -> logging.Logger:
    """Configura uma única vez os destinos de log do projeto.

    As mensagens são exibidas no terminal e registradas em arquivo rotativo,
    evitando que a pasta de logs cresça indefinidamente.
    """
    logger = logging.getLogger("finance_pipeline")
    if logger.handlers:
        return logger

    nivel = getattr(logging, LOG_NIVEL.upper(), logging.INFO)
    logger.setLevel(nivel)
    logger.propagate = False
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setLevel(nivel)
    console.setFormatter(formato)
    logger.addHandler(console)

    caminho = Path(LOG_ARQUIVO)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    arquivo = RotatingFileHandler(
        caminho, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
    )
    arquivo.setLevel(nivel)
    arquivo.setFormatter(formato)
    logger.addHandler(arquivo)
    return logger
