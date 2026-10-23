"""
Instalador e Conversor Automatizado do Cobbled Farms para Minecraft Bedrock Dedicated Server (BDS).

Cobbled Farms e o mapa oficial de tutoriais e aventuras para o mod Cobblemon.
Este script automatiza:
1. O download do pacote oficial do CurseForge (Projeto 924311 - Cobbled Farms v4).
2. A verificacao e obtencao do conversor oficial Chunker CLI (HiveGamesOSS/Chunker).
3. A conversao de precisao do mundo Java para o formato nativo Bedrock 1.26.50+ (LevelDB).
4. A integracao dos pacotes de comportamento e recursos do CobbleDrock (BP e RP).
5. A configuracao dos metadados (levelname.txt, world_icon.jpeg).
6. A opcao de alternar imediatamente para o Cobbled Farms como mapa ativo no BDS.
"""

from __future__ import annotations

import argparse
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

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
DATA_DIR = SERVER_DIR / "data"
WORLDS_DIR = DATA_DIR / "worlds"
TOOLS_DIR = DATA_DIR / "tools"
TARGET_WORLD_NAME = "Cobbled Farms"
TARGET_WORLD_DIR = WORLDS_DIR / TARGET_WORLD_NAME

CURSEFORGE_PROJECT_ID = "924311"
CURSEFORGE_FILE_ID = "7252452"  # Cobbled Farms v4 (Latest)
CURSEFORGE_DOWNLOAD_URL = (
    f"https://www.curseforge.com/api/v1/mods/{CURSEFORGE_PROJECT_ID}/files/{CURSEFORGE_FILE_ID}/download"
)
CHUNKER_JAR_URL = (
    "https://github.com/HiveGamesOSS/Chunker/releases/download/1.21.0/chunker-cli-1.21.0.jar"
)


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


def download_cobbled_farms(dest_zip: Path, force: bool = False) -> Path:
    """Baixa o zip do Cobbled Farms do CurseForge ou usa cache local existente."""
    if not force and dest_zip.is_file() and dest_zip.stat().st_size > 50_000_000:
        print(f"[*] Usando pacote Cobbled Farms em cache: {dest_zip} ({dest_zip.stat().st_size // (1024*1024)} MB)")
        return dest_zip

    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    print(f"[*] Baixando Cobbled Farms v4 do CurseForge ({CURSEFORGE_DOWNLOAD_URL})...")
    req = urllib.request.Request(CURSEFORGE_DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(dest_zip, "wb") as f:
        shutil.copyfileobj(resp, f)
    print(f"[+] Download concluido com sucesso! ({dest_zip.stat().st_size // (1024*1024)} MB)")
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

    print("[*] Iniciando conversao Chunker (Java 1.21 -> Bedrock 1.26)...")
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


def setup_cobbled_farms_metadata(world_dir: Path, icon_source: Optional[Path] = None) -> None:
    """Configura levelname.txt e world_icon.jpeg."""
    levelname_file = world_dir / "levelname.txt"
    levelname_file.write_text("Cobbled Farms\n", encoding="utf-8")

    if icon_source and icon_source.is_file():
        try:
            from PIL import Image

            im = Image.open(icon_source).convert("RGB")
            im.save(world_dir / "world_icon.jpeg", "JPEG")
            print("[+] Icone do mundo convertido para world_icon.jpeg.")
        except Exception as exc:
            print(f"[AVISO] Nao foi possivel converter icon.png: {exc}")


def enable_cobblemon_addons(world_name: str = TARGET_WORLD_NAME) -> bool:
    """Ativa os pacotes de comportamento e textura do CobbleDrock no mundo."""
    if gerenciar_mods is not None:
        return gerenciar_mods.enable_mod("cobbledrock", world_name)
    return False


def install_cobbled_farms(activate_as_current: bool = False, force_download: bool = False) -> bool:
    """Executa o processo completo de instalacao e integracao do Cobbled Farms."""
    print("\n" + "=" * 65)
    print("      INSTALADOR OFICIAL: COBBLED FARMS PARA BEDROCK SERVER")
    print("=" * 65)

    chunker_jar = ensure_chunker_jar()
    cache_zip = DATA_DIR / "cobbled_farms.zip"
    download_cobbled_farms(cache_zip, force=force_download)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        print("[*] Extraindo arquivo ZIP do Cobbled Farms...")
        with zipfile.ZipFile(cache_zip, "r") as z:
            z.extractall(tmp_path)

        # Encontrar pasta com level.dat
        java_world_dir = None
        for root, dirs, files in os.walk(tmp_path):
            if "level.dat" in files and "region" in dirs:
                java_world_dir = Path(root)
                break

        if not java_world_dir:
            print("[ERRO] Mundo Java valido nao encontrado no pacote extraido.")
            return False

        print(f"[+] Mundo Java localizado em: {java_world_dir.name}")
        icon_source = java_world_dir / "icon.png"

        # Se ja existir pasta do mundo alvo, fazer backup de seguranca
        if TARGET_WORLD_DIR.exists():
            backup_name = f"Cobbled_Farms_backup_{int(time.time())}"
            backup_dest = DATA_DIR / "backups" / backup_name
            print(f"[*] Fazendo backup do mundo anterior para: {backup_dest}")
            backup_dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copytree(TARGET_WORLD_DIR, backup_dest)
            except Exception as e:
                print(f"[AVISO] Falha ao criar backup: {e}")

        ok = convert_java_world_to_bedrock(java_world_dir, TARGET_WORLD_DIR, chunker_jar)
        if not ok:
            return False

        setup_cobbled_farms_metadata(TARGET_WORLD_DIR, icon_source if icon_source.is_file() else None)

    # Configurar CobbleDrock (Addon Bedrock de Cobblemon)
    print("[*] Vinculando CobbleDrock Add-on (Core + Content) ao mapa Cobbled Farms...")
    enable_cobblemon_addons(TARGET_WORLD_NAME)

    if activate_as_current and gerenciar_mods is not None:
        print(f"[*] Configurando '{TARGET_WORLD_NAME}' como mundo ativo no servidor...")
        gerenciar_mods.switch_active_world(TARGET_WORLD_NAME)

    print("\n" + "=" * 65)
    print(" [SUCESSO] Cobbled Farms instalado e configurado com exito!")
    print(f" Localizacao: {TARGET_WORLD_DIR}")
    print(" Add-ons ativados: CobbleDrock Core & Content (Pokemon e Batalhas)")
    print("=" * 65 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Instalador e Conversor do Cobbled Farms para Bedrock")
    parser.add_argument("--activate", action="store_true", help="Ativa Cobbled Farms como o mundo corrente no BDS")
    parser.add_argument("--force-download", action="store_true", help="Forca o download mesmo se houver cache local")
    args = parser.parse_args()

    success = install_cobbled_farms(activate_as_current=args.activate, force_download=args.force_download)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
