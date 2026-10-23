"""
Modulo de Compatibilidade e Gerenciador Dedicado do CobbleDrock.
Permite ativar/desativar os pacotes do CobbleDrock e expoe constantes para testes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import gerenciar_mods

COBBLEDROCK_BP_IDS = {
    "301ce48a-eef2-51b7-926d-b8a68eabcfea",
    "56a52fe3-c4d8-588d-9cce-6c6e6c381013",
}

COBBLEDROCK_RP_IDS = {
    "3e2975ad-9c9f-5098-8ac6-86bfb6cb6917",
    "266755bb-c9eb-5e1f-ad3e-f4e062d58c48",
}

COBBLEDROCK_PACKS: Dict[str, List[Dict[str, Any]]] = {
    "bp": [
        {
            "pack_id": "301ce48a-eef2-51b7-926d-b8a68eabcfea",
            "name": "CobbleDrock Core BP",
            "default_version": [1, 3, 1],
        },
        {
            "pack_id": "56a52fe3-c4d8-588d-9cce-6c6e6c381013",
            "name": "CobbleDrock Content BP",
            "default_version": [1, 3, 1],
        },
    ],
    "rp": [
        {
            "pack_id": "3e2975ad-9c9f-5098-8ac6-86bfb6cb6917",
            "name": "CobbleDrock Core RP",
            "default_version": [1, 3, 1],
        },
        {
            "pack_id": "266755bb-c9eb-5e1f-ad3e-f4e062d58c48",
            "name": "CobbleDrock Content RP",
            "default_version": [1, 3, 1],
        },
    ],
}


def load_json_file(path: Path) -> List[Dict[str, Any]]:
    return gerenciar_mods.load_json_file(path)


def save_json_file(path: Path, data: List[Dict[str, Any]]) -> None:
    gerenciar_mods.save_json_file(path, data)


def enable_cobbledrock(level_name: str | None = None) -> bool:
    return gerenciar_mods.enable_mod("cobbledrock", level_name)


def disable_cobbledrock(level_name: str | None = None) -> bool:
    return gerenciar_mods.disable_mod("cobbledrock", level_name)


def get_cobbledrock_status(level_name: str | None = None) -> Dict[str, Any]:
    return gerenciar_mods.get_mod_status("cobbledrock", level_name)
