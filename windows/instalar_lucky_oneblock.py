"""
Instalador e Conversor Automatizado do Lucky OneBlock para Minecraft Bedrock Dedicated Server (BDS).

Baseado no projeto CurseForge oficial:
- Projeto: 872580 (Lucky OneBlock - Lucky Blocks - Multiplayer por el_this_boy)
- URL: https://www.curseforge.com/minecraft/worlds/lucky-oneblock

Etapas Automatizadas:
1. Download do pacote oficial do CurseForge via API pública de arquivos.
2. Conversao do mapa Java para o formato nativo Bedrock 1.26.50+ (LevelDB) via Chunker CLI.
3. Compilação e implantação do Add-on Lucky Block & OneBlock Engine (Behavior Pack + Resource Pack).
4. Vinculação dos UUIDs em world_behavior_packs.json e world_resource_packs.json.
5. Configuração de metadados: levelname.txt e world_icon.jpeg.
6. Suporte a ativacao imediata no servidor como mapa principal.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

# Setup de caminhos
WINDOWS_DIR = Path(__file__).resolve().parent
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

try:
    import gerenciar_mods
except ImportError:
    gerenciar_mods = None

try:
    import build_lucky_addon
except ImportError:
    build_lucky_addon = None

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
DATA_DIR = SERVER_DIR / "data"
WORLDS_DIR = DATA_DIR / "worlds"
TOOLS_DIR = DATA_DIR / "tools"

TARGET_WORLD_NAME = "Lucky OneBlock"
TARGET_WORLD_DIR = WORLDS_DIR / TARGET_WORLD_NAME

CURSEFORGE_PROJECT_ID = "872580"
CURSEFORGE_FILES_API = f"https://www.curseforge.com/api/v1/mods/{CURSEFORGE_PROJECT_ID}/files"
CHUNKER_JAR_URL = "https://github.com/HiveGamesOSS/Chunker/releases/download/1.21.0/chunker-cli-1.21.0.jar"


def ensure_chunker_jar(tools_dir: Path = TOOLS_DIR) -> Path:
    """Garante a presenca do utilitario Chunker CLI Jar."""
    tools_dir.mkdir(parents=True, exist_ok=True)
    jar_path = tools_dir / "chunker-cli.jar"
    if jar_path.is_file() and jar_path.stat().st_size > 10_000_000:
        return jar_path

    print(f"[*] Baixando Chunker CLI de {CHUNKER_JAR_URL}...")
    req = urllib.request.Request(CHUNKER_JAR_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(jar_path, "wb") as f:
        shutil.copyfileobj(resp, f)
    print(f"[+] Chunker CLI pronto em: {jar_path}")
    return jar_path


def get_latest_file_id() -> str:
    """Obtem o ID do arquivo mais recente do projeto no CurseForge."""
    try:
        req = urllib.request.Request(CURSEFORGE_FILES_API, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        files = data.get("data", [])
        if files:
            # Primeiro arquivo da lista é o mais recente
            file_id = str(files[0]["id"])
            print(f"[*] Versao mais recente no CurseForge identificada: ID {file_id} ({files[0].get('displayName')})")
            return file_id
    except Exception as exc:
        print(f"[AVISO] Falha ao consultar API do CurseForge ({exc}). Usando versao estavel padrao.")
    return "8550497"  # Fallback estavel


def download_lucky_oneblock(dest_zip: Path, force: bool = False) -> Path:
    """Baixa o zip do Lucky OneBlock do CurseForge ou reutiliza cache local."""
    if not force and dest_zip.is_file() and dest_zip.stat().st_size > 5_000:
        print(f"[*] Usando pacote Lucky OneBlock em cache: {dest_zip} ({dest_zip.stat().st_size} bytes)")
        return dest_zip

    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    file_id = get_latest_file_id()
    download_url = f"https://www.curseforge.com/api/v1/mods/{CURSEFORGE_PROJECT_ID}/files/{file_id}/download"

    print(f"[*] Baixando Lucky OneBlock do CurseForge ({download_url})...")
    req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(dest_zip, "wb") as f:
        shutil.copyfileobj(resp, f)
    print(f"[+] Download concluido com sucesso! ({dest_zip.stat().st_size} bytes)")
    return dest_zip


def convert_java_world_to_bedrock(source_world_dir: Path, target_bedrock_dir: Path, chunker_jar: Path) -> bool:
    """Converte o mundo Java para formato Bedrock LevelDB usando Chunker CLI."""
    target_bedrock_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "java",
        "-Xmx4G",
        "-jar",
        str(chunker_jar),
        "-i",
        str(source_world_dir),
        "-f",
        "BEDROCK_R26_50",
        "-o",
        str(target_bedrock_dir),
    ]

    print("[*] Iniciando conversao Chunker (Java -> Bedrock 1.26)...")
    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        print(f"[ERRO] Falha na conversao Chunker: {result.stderr or result.stdout}")
        return False

    db_dir = target_bedrock_dir / "db"
    level_dat = target_bedrock_dir / "level.dat"
    if not db_dir.is_dir() or not level_dat.is_file():
        print("[ERRO] Arquivos de mundo Bedrock (db/ ou level.dat) nao foram gerados.")
        return False

    print("[+] Conversao Chunker concluida com sucesso!")
    return True


def setup_world_metadata(world_dir: Path) -> None:
    """Configura levelname.txt e gera o icone oficial world_icon.jpeg."""
    levelname_file = world_dir / "levelname.txt"
    levelname_file.write_text(f"{TARGET_WORLD_NAME}\n", encoding="utf-8")

    icon_path = world_dir / "world_icon.jpeg"
    if build_lucky_addon is not None:
        build_lucky_addon.generate_pack_icon(icon_path, "LUCKY ONEBLOCK")
        print("[+] Icone do mundo configurado em world_icon.jpeg.")


def attach_lucky_addon_to_world(world_dir: Path) -> None:
    """Vincula os pacotes de comportamento e recursos ao mundo em world_*_packs.json."""
    bp_path = world_dir / "world_behavior_packs.json"
    rp_path = world_dir / "world_resource_packs.json"

    bp_uuid = build_lucky_addon.BP_UUID if build_lucky_addon else "59aa09c5-0a2c-4134-8481-725801fba963"
    rp_uuid = build_lucky_addon.RP_UUID if build_lucky_addon else "60910110-474e-41b4-aa72-68e06a917819"

    # Carrega ou cria listas
    def load_or_init(p: Path):
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:
                pass
        return []

    bps = load_or_init(bp_path)
    rps = load_or_init(rp_path)

    # Evita duplicatas
    if not any(b.get("pack_id") == bp_uuid for b in bps if isinstance(b, dict)):
        bps.append({"pack_id": bp_uuid, "version": [1, 0, 0]})
    if not any(r.get("pack_id") == rp_uuid for r in rps if isinstance(r, dict)):
        rps.append({"pack_id": rp_uuid, "version": [1, 0, 0]})

    bp_path.write_text(json.dumps(bps, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rp_path.write_text(json.dumps(rps, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[+] Add-on Lucky Block vinculado ao mundo '{TARGET_WORLD_NAME}'.")


def install_lucky_oneblock(activate_as_current: bool = False, force_download: bool = False) -> bool:
    """Executa o processo de ponta a ponta para baixar, converter e instalar o Lucky OneBlock."""
    print("\n" + "=" * 65)
    print("      INSTALADOR OFICIAL: LUCKY ONEBLOCK PARA BEDROCK SERVER")
    print("=" * 65)

    # 1. Compilar o Addon Lucky Block (BP + RP) e implantar no runtime
    if build_lucky_addon is not None:
        build_lucky_addon.build_all()

    chunker_jar = ensure_chunker_jar()
    cache_zip = DATA_DIR / "lucky_oneblock.zip"
    download_lucky_oneblock(cache_zip, force=force_download)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        print("[*] Extraindo pacote ZIP do Lucky OneBlock...")
        with zipfile.ZipFile(cache_zip, "r") as z:
            z.extractall(tmp_path)

        # Encontrar pasta com level.dat
        java_world_dir = None
        for root, dirs, files in os.walk(tmp_path):
            if "level.dat" in files:
                java_world_dir = Path(root)
                break

        if not java_world_dir:
            print("[ERRO] Arquivo level.dat nao encontrado no pacote extraido.")
            return False

        print(f"[+] Mundo Java localizado em: {java_world_dir.name}")

        # Se ja existir pasta do mundo alvo, fazer backup antes de sobrescrever
        if TARGET_WORLD_DIR.exists():
            backup_name = f"Lucky_OneBlock_backup_{int(time.time())}"
            backup_dest = DATA_DIR / "backups" / backup_name
            print(f"[*] Criando backup do mundo anterior para: {backup_dest}")
            backup_dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copytree(TARGET_WORLD_DIR, backup_dest)
            except Exception as e:
                print(f"[AVISO] Falha ao criar backup previo: {e}")

        ok = convert_java_world_to_bedrock(java_world_dir, TARGET_WORLD_DIR, chunker_jar)
        if not ok:
            return False

        setup_world_metadata(TARGET_WORLD_DIR)

    # Vincular Add-on Lucky Block
    attach_lucky_addon_to_world(TARGET_WORLD_DIR)

    if activate_as_current and gerenciar_mods is not None:
        print(f"[*] Configurando '{TARGET_WORLD_NAME}' como mundo ativo no servidor...")
        gerenciar_mods.switch_active_world(TARGET_WORLD_NAME)

    print("\n" + "=" * 65)
    print(" [SUCESSO] Lucky OneBlock instalado e configurado com exito!")
    print(f" Localizacao: {TARGET_WORLD_DIR}")
    print(" Motor ativo: Lucky Block & OneBlock Engine v1.0.0")
    print("=" * 65 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Instalador e Conversor do Lucky OneBlock para Bedrock")
    parser.add_argument("--activate", action="store_true", help="Ativa Lucky OneBlock como o mundo ativo no BDS")
    parser.add_argument("--force-download", action="store_true", help="Forca o download mesmo se houver cache local")
    args = parser.parse_args()

    success = install_lucky_oneblock(activate_as_current=args.activate, force_download=args.force_download)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
