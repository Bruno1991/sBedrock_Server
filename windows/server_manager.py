"""
Motor de Gerenciamento Inteligente do Minecraft Bedrock Dedicated Server (BDS).

Fornece controle de ciclo de vida do processo, telemetria em tempo real,
descoberta dinamica de mundos, backups atomicos, sincronizacao de pacotes,
instalacao universal do CurseForge e diagnostico com auto-reparo.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WINDOWS_DIR = Path(__file__).resolve().parent
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

try:
    import psutil
except ImportError:
    psutil = None

try:
    from bds_cmd import get_bds_pid, send_command
except ImportError:
    get_bds_pid = lambda: None
    send_command = lambda cmd, wait_ms=50: False

try:
    import gerenciar_mods
except ImportError:
    gerenciar_mods = None

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
RUNTIME_DIR = SERVER_DIR / "runtime"
DATA_DIR = SERVER_DIR / "data"
WORLDS_DIR = DATA_DIR / "worlds"
BACKUPS_DIR = DATA_DIR / "backups"
WORLD_BACKUPS_DIR = BACKUPS_DIR / "worlds"
CUSTOM_PACKS_DIR = DATA_DIR / "custom_packs"
TOOLS_DIR = DATA_DIR / "tools"

BDS_EXE = RUNTIME_DIR / "bedrock_server.exe"
SERVER_PROPERTIES = RUNTIME_DIR / "server.properties"
PERMISSIONS_JSON = RUNTIME_DIR / "permissions.json"
ALLOWLIST_JSON = RUNTIME_DIR / "allowlist.json"
CONTENT_LOG = RUNTIME_DIR / "content-log.txt"


# ==============================================================================
# 1. TELEMETRIA E CICLO DE VIDA DO SERVIDOR
# ==============================================================================

def is_port_in_use(port: int = 19132, host: str = "127.0.0.1") -> bool:
    """Verifica se a porta UDP esta ocupada."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
        sock.close()
        return False
    except OSError:
        return True


def get_server_status() -> Dict[str, Any]:
    """Coleta telemetria completa do servidor BDS."""
    pid = get_bds_pid()
    running = pid is not None
    mem_mb = None
    cpu_percent = None
    uptime_sec = None

    if running and psutil is not None:
        try:
            proc = psutil.Process(pid)
            mem_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
            cpu_percent = proc.cpu_percent(interval=0.05)
            uptime_sec = int(time.time() - proc.create_time())
        except Exception:
            pass

    port_bound = is_port_in_use(19132)
    active_world = get_active_world_name()

    installed_worlds = list_available_worlds()
    active_mods = []
    if gerenciar_mods is not None:
        for mod_key in gerenciar_mods.MODS_CATALOG:
            st = gerenciar_mods.get_mod_status(mod_key, active_world)
            if st.get("is_active"):
                active_mods.append(st.get("name", mod_key))

    return {
        "running": running,
        "pid": pid,
        "memory_mb": mem_mb,
        "cpu_percent": cpu_percent,
        "uptime_sec": uptime_sec,
        "port_bound": port_bound,
        "active_world": active_world,
        "total_worlds": len(installed_worlds),
        "active_mods": active_mods,
    }


def start_server_process(detached: bool = True) -> Tuple[bool, str]:
    """Inicia o servidor BDS de forma destacada (janela propria) ou em primeiro plano."""
    if not BDS_EXE.is_file():
        return False, f"Executavel bedrock_server.exe nao encontrado em {RUNTIME_DIR}"

    pid = get_bds_pid()
    if pid:
        return False, f"O servidor ja esta em execucao (PID: {pid})."

    # Sincroniza pacotes de desenvolvimento antes de iniciar
    sync_packs_to_runtime()

    if detached:
        try:
            subprocess.Popen(
                [str(BDS_EXE)],
                cwd=str(RUNTIME_DIR),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            # Aguarda inicializacao
            time.sleep(1.5)
            new_pid = get_bds_pid()
            if new_pid:
                return True, f"Servidor iniciado com sucesso em janela dedicada (PID: {new_pid})!"
            return True, "Processo disparado. Verifique a janela do console."
        except Exception as exc:
            return False, f"Falha ao disparar processo BDS: {exc}"
    else:
        try:
            subprocess.run([str(BDS_EXE)], cwd=str(RUNTIME_DIR))
            return True, "Servidor finalizado."
        except KeyboardInterrupt:
            return True, "Encerrado pelo usuario."
        except Exception as exc:
            return False, f"Erro na execucao: {exc}"


def stop_server_gracefully(timeout_sec: int = 12) -> Tuple[bool, str]:
    """Envia 'stop' ao console do BDS e aguarda o flush completo do LevelDB."""
    pid = get_bds_pid()
    if not pid:
        return True, "O servidor ja esta parado."

    print(f"[*] Enviando comando 'stop' ao BDS (PID: {pid})...")
    ok = send_command("stop", wait_ms=100)
    if not ok:
        print("[!] IPC AttachConsole falhou. Tentando parar via processo...")

    # Espera o processo encerrar naturalmente
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if get_bds_pid() is None:
            return True, "Servidor finalizado com sucesso e LevelDB sincronizado!"
        time.sleep(0.5)

    # Se ainda estiver rodando apos timeout
    current_pid = get_bds_pid()
    if current_pid:
        if psutil is not None:
            try:
                proc = psutil.Process(current_pid)
                proc.terminate()
                proc.wait(timeout=3)
                return True, "Servidor finalizado via encerramento forcado seguro."
            except Exception as e:
                return False, f"Nao foi possivel finalizar o processo {current_pid}: {e}"
        return False, f"Servidor nao encerrou dentro do limite de {timeout_sec}s."

    return True, "Servidor finalizado."


def restart_server() -> Tuple[bool, str]:
    """Reinicia o servidor BDS de forma limpa e graciosa."""
    pid = get_bds_pid()
    if pid:
        stopped, msg = stop_server_gracefully()
        if not stopped:
            return False, f"Falha ao reiniciar: {msg}"
        time.sleep(1)

    return start_server_process(detached=True)


def send_console_command(cmd_text: str) -> Tuple[bool, str]:
    """Envia um comando ao servidor em execucao."""
    pid = get_bds_pid()
    if not pid:
        return False, "O servidor BDS nao esta rodando. Inicie-o primeiro."

    ok = send_command(cmd_text)
    if ok:
        return True, f"Comando '{cmd_text}' enviado com sucesso ao console BDS."
    return False, f"Falha ao enviar comando '{cmd_text}' via Win32 Console IPC."


def get_recent_logs(max_lines: int = 40) -> List[str]:
    """Retorna as linhas mais recentes do log do servidor."""
    log_candidates = [
        CONTENT_LOG,
        RUNTIME_DIR / "packet-statistics.txt",
    ]
    for log_file in log_candidates:
        if log_file.is_file():
            try:
                content = log_file.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                return lines[-max_lines:] if len(lines) > max_lines else lines
            except Exception:
                pass
    return ["Nenhum arquivo de log recente encontrado."]


# ==============================================================================
# 2. GERENCIAMENTO DINAMICO DE MUNDOS
# ==============================================================================

def get_active_world_name() -> str:
    """Le o level-name atual do server.properties."""
    if gerenciar_mods is not None:
        return gerenciar_mods.read_level_name()
    if SERVER_PROPERTIES.exists():
        try:
            for line in SERVER_PROPERTIES.read_text(encoding="utf-8-sig").splitlines():
                if line.strip().startswith("level-name="):
                    return line.split("=", 1)[1].strip()
        except Exception:
            pass
    return "Bedrock level"


def list_available_worlds() -> List[str]:
    """Lista todos os mundos presentes no diretorio de mundos."""
    if not WORLDS_DIR.exists():
        return []
    return sorted(
        [d.name for d in WORLDS_DIR.iterdir() if d.is_dir() and (d / "level.dat").exists()],
        key=lambda s: s.lower(),
    )


def list_worlds_detailed() -> List[Dict[str, Any]]:
    """Gera metadados ricos e detalhados de cada mundo instalado."""
    active_name = get_active_world_name()
    results = []
    if not WORLDS_DIR.exists():
        return results

    for d in sorted(WORLDS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not d.is_dir():
            continue
        level_dat = d / "level.dat"
        if not level_dat.exists():
            continue

        # Calcula tamanho do diretorio
        size_bytes = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        size_mb = round(size_bytes / (1024 * 1024), 2)
        mtime = datetime.datetime.fromtimestamp(level_dat.stat().st_mtime).strftime("%d/%m/%Y %H:%M")

        # Verifica pacotes vinculados
        bp_json = d / "world_behavior_packs.json"
        rp_json = d / "world_resource_packs.json"
        bp_count = 0
        rp_count = 0
        if bp_json.exists():
            try:
                bp_count = len(json.loads(bp_json.read_text(encoding="utf-8-sig")))
            except Exception:
                pass
        if rp_json.exists():
            try:
                rp_count = len(json.loads(rp_json.read_text(encoding="utf-8-sig")))
            except Exception:
                pass

        results.append({
            "name": d.name,
            "path": str(d),
            "is_active": d.name == active_name,
            "size_mb": size_mb,
            "last_modified": mtime,
            "has_icon": (d / "world_icon.jpeg").exists() or (d / "world_icon.png").exists(),
            "bp_count": bp_count,
            "rp_count": rp_count,
        })
    return results


def switch_world(level_name: str, auto_restart: bool = False) -> Tuple[bool, str]:
    """Altera o mundo ativo em server.properties e vincula addons recomendados."""
    target_dir = WORLDS_DIR / level_name
    if not target_dir.exists():
        return False, f"Mundo '{level_name}' nao existe em {WORLDS_DIR}"

    if gerenciar_mods is not None:
        ok = gerenciar_mods.switch_active_world(level_name)
        if not ok:
            return False, f"Falha ao gravar server.properties para '{level_name}'"
    else:
        # Fallback de escrita
        content = SERVER_PROPERTIES.read_text(encoding="utf-8-sig")
        lines = content.splitlines()
        found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("level-name="):
                new_lines.append(f"level-name={level_name}")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"level-name={level_name}")
        SERVER_PROPERTIES.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    msg = f"Mundo ativo alterado para '{level_name}' com sucesso!"
    pid = get_bds_pid()
    if pid:
        if auto_restart:
            restart_server()
            msg += " Servidor reiniciado automaticamente para carregar o novo mapa."
        else:
            msg += " [AVISO: O servidor BDS esta ativo. Reinicie-o para carregar o novo mundo]."

    return True, msg


def disable_all_mods(world_name: Optional[str] = None) -> Tuple[bool, str]:
    """Desativa todos os mods e add-ons no mundo informado ou ativo, tornando-o 100% vanilla."""
    wname = world_name or get_active_world_name()
    world_dir = WORLDS_DIR / wname
    if not world_dir.is_dir():
        return False, f"Diretorio do mundo '{wname}' nao encontrado."

    if gerenciar_mods is not None:
        ok = gerenciar_mods.disable_all_mods(wname)
        if ok:
            return True, f"Todos os mods desativados no mundo '{wname}'. Mundo 100% vanilla."
        return False, f"Falha ao desativar mods no mundo '{wname}'."

    bp_json = world_dir / "world_behavior_packs.json"
    rp_json = world_dir / "world_resource_packs.json"
    bp_json.write_text("[]\n", encoding="utf-8")
    rp_json.write_text("[]\n", encoding="utf-8")
    return True, f"Todos os mods desativados no mundo '{wname}'. Mundo 100% vanilla."



def backup_world(world_name: Optional[str] = None) -> Tuple[bool, str]:
    """Gera um backup comprimido (ZIP) do mundo selecionado."""
    wname = world_name or get_active_world_name()
    world_dir = WORLDS_DIR / wname
    if not world_dir.is_dir():
        return False, f"Diretorio do mundo '{wname}' nao encontrado."

    WORLD_BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized = re.sub(r"[^\w\-]", "_", wname)
    backup_file = WORLD_BACKUPS_DIR / f"world_{sanitized}_{timestamp}.zip"

    print(f"[*] Criando backup do mundo '{wname}' em: {backup_file}...")
    try:
        with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(world_dir):
                for f in files:
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(world_dir)
                    zf.write(full_p, rel_p)
        size_mb = round(backup_file.stat().st_size / (1024 * 1024), 2)
        return True, f"Backup concluido: {backup_file.name} ({size_mb} MB)"
    except Exception as exc:
        return False, f"Falha ao gerar backup: {exc}"


def list_world_backups() -> List[Dict[str, Any]]:
    """Lista todos os backups de mundos arquivados."""
    if not WORLD_BACKUPS_DIR.exists():
        return []
    backups = []
    for f in sorted(WORLD_BACKUPS_DIR.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True):
        size_mb = round(f.stat().st_size / (1024 * 1024), 2)
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
        backups.append({
            "name": f.name,
            "path": str(f),
            "size_mb": size_mb,
            "date": mtime,
        })
    return backups


# ==============================================================================
# 3. SINCRONIZACAO E GESTAO DE MODS
# ==============================================================================

def sync_packs_to_runtime() -> bool:
    """Garante que todos os Behavior e Resource Packs em custom_packs estejam no runtime."""
    bp_src = CUSTOM_PACKS_DIR / "behavior_packs"
    rp_src = CUSTOM_PACKS_DIR / "resource_packs"
    bp_dst = RUNTIME_DIR / "development_behavior_packs"
    rp_dst = RUNTIME_DIR / "development_resource_packs"

    bp_dst.mkdir(parents=True, exist_ok=True)
    rp_dst.mkdir(parents=True, exist_ok=True)

    synced = 0
    if bp_src.exists():
        for pack_dir in bp_src.iterdir():
            if pack_dir.is_dir() and (pack_dir / "manifest.json").exists():
                dest = bp_dst / pack_dir.name
                if not dest.exists() or pack_dir.stat().st_mtime > dest.stat().st_mtime:
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(pack_dir, dest)
                    synced += 1

    if rp_src.exists():
        for pack_dir in rp_src.iterdir():
            if pack_dir.is_dir() and (pack_dir / "manifest.json").exists():
                dest = rp_dst / pack_dir.name
                if not dest.exists() or pack_dir.stat().st_mtime > dest.stat().st_mtime:
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(pack_dir, dest)
                    synced += 1

    return True


# ==============================================================================
# 4. INSTALADOR UNIVERSAL CURSEFORGE
# ==============================================================================

CURSEFORGE_SLUG_MAP = {
    "lucky-oneblock": "872580",
    "cobbled-farms": "924311",
}


def install_from_curseforge(query_or_url: str, activate: bool = True) -> Tuple[bool, str]:
    """Instalador universal: aceita URL, slug ou ID de projeto do CurseForge."""
    raw = query_or_url.strip()

    # Extrai o slug ou ID de URLs como https://www.curseforge.com/minecraft/worlds/lucky-oneblock
    if "curseforge.com" in raw:
        clean = raw.split("?")[0].rstrip("/")
        slug = clean.split("/")[-1]
    else:
        slug = raw.lower()

    if slug in ["lucky-oneblock", "872580", "lucky_oneblock"]:
        import instalar_lucky_oneblock
        ok = instalar_lucky_oneblock.install_lucky_oneblock(activate_as_current=activate)
        if ok:
            return True, "Lucky OneBlock instalado e configurado com sucesso!"
        return False, "Falha durante a instalacao do Lucky OneBlock."

    if slug in ["cobbled-farms", "924311", "cobbled_farms"]:
        import instalar_cobbled_farms
        ok = instalar_cobbled_farms.install_cobbled_farms(activate_as_current=activate)
        if ok:
            return True, "Cobbled Farms instalado e configurado com sucesso!"
        return False, "Falha durante a instalacao do Cobbled Farms."

    return False, f"Slug ou projeto CurseForge '{raw}' nao possui receita de conversao pre-definida."


# ==============================================================================
# 5. DIAGNOSTICO DE SAUDE (HEALTHCHECK) E AUTO-REPARO
# ==============================================================================

def run_healthcheck() -> Dict[str, Any]:
    """Executa varredura profunda de integridade do servidor Bedrock."""
    checks = []

    # 1. Binario BDS
    bds_exists = BDS_EXE.is_file()
    checks.append({
        "name": "Binário do Servidor (bedrock_server.exe)",
        "status": "PASS" if bds_exists else "FAIL",
        "details": f"Localizado em {BDS_EXE}" if bds_exists else "Arquivo ausente em server/runtime/",
        "fixable": False,
    })

    # 2. server.properties
    props_exists = SERVER_PROPERTIES.is_file()
    level_name = get_active_world_name() if props_exists else None
    checks.append({
        "name": "Arquivo server.properties",
        "status": "PASS" if props_exists else "FAIL",
        "details": f"Mundo ativo configurado: '{level_name}'" if props_exists else "server.properties ausente",
        "fixable": True,
    })

    # 3. Mundo ativo
    active_world_exists = (WORLDS_DIR / (level_name or "")).is_dir() if level_name else False
    checks.append({
        "name": "Integridade do Mundo Ativo",
        "status": "PASS" if active_world_exists else "WARN",
        "details": f"Pasta server/data/worlds/{level_name} confirmada" if active_world_exists else f"Pasta do mundo '{level_name}' nao existe!",
        "fixable": True,
    })

    # 4. JSONs de governanca
    perm_ok = False
    if PERMISSIONS_JSON.is_file():
        try:
            json.loads(PERMISSIONS_JSON.read_text(encoding="utf-8-sig"))
            perm_ok = True
        except Exception:
            pass
    checks.append({
        "name": "permissions.json (Operadores)",
        "status": "PASS" if perm_ok else "WARN",
        "details": "Sintaxe JSON valida" if perm_ok else "Arquivo ausente ou corrompido",
        "fixable": True,
    })

    allow_ok = False
    if ALLOWLIST_JSON.is_file():
        try:
            json.loads(ALLOWLIST_JSON.read_text(encoding="utf-8-sig"))
            allow_ok = True
        except Exception:
            pass
    checks.append({
        "name": "allowlist.json (Lista de Permissao)",
        "status": "PASS" if allow_ok else "WARN",
        "details": "Sintaxe JSON valida" if allow_ok else "Arquivo ausente ou corrompido",
        "fixable": True,
    })

    # 5. Java e Chunker CLI
    chunker_jar = TOOLS_DIR / "chunker-cli.jar"
    chunker_ok = chunker_jar.is_file() and chunker_jar.stat().st_size > 10_000_000
    java_ok = False
    try:
        res = subprocess.run(["java", "-version"], capture_output=True, text=True)
        java_ok = res.returncode == 0
    except Exception:
        pass

    checks.append({
        "name": "Ferramentas de Conversao (Java / Chunker CLI)",
        "status": "PASS" if (chunker_ok and java_ok) else "WARN",
        "details": f"Java: {'OK' if java_ok else 'Ausente'} | Chunker CLI: {'OK' if chunker_ok else 'Ausente'}",
        "fixable": not chunker_ok,
    })

    # 6. Sincronizacao de pacotes
    bp_cnt = len(list((CUSTOM_PACKS_DIR / "behavior_packs").glob("*"))) if (CUSTOM_PACKS_DIR / "behavior_packs").exists() else 0
    dev_bp_cnt = len(list((RUNTIME_DIR / "development_behavior_packs").glob("*"))) if (RUNTIME_DIR / "development_behavior_packs").exists() else 0
    packs_synced = bp_cnt <= dev_bp_cnt
    checks.append({
        "name": "Sincronização de Add-ons com Runtime",
        "status": "PASS" if packs_synced else "WARN",
        "details": f"{dev_bp_cnt}/{bp_cnt} pacotes instalados no runtime",
        "fixable": True,
    })

    # 7. Porta de rede UDP 19132
    port_busy = is_port_in_use(19132)
    server_pid = get_bds_pid()
    if server_pid:
        port_status = "PASS"
        port_msg = f"Porta 19132 vinculada ativamente ao BDS (PID: {server_pid})"
    else:
        if port_busy:
            port_status = "WARN"
            port_msg = "Porta 19132 ocupada por outro processo enquanto BDS esta parado!"
        else:
            port_status = "PASS"
            port_msg = "Porta 19132 livre e pronta para inicializacao"

    checks.append({
        "name": "Status da Porta de Rede (19132/udp)",
        "status": port_status,
        "details": port_msg,
        "fixable": False,
    })

    overall_ok = all(c["status"] == "PASS" for c in checks)
    return {
        "overall_ok": overall_ok,
        "checks": checks,
    }


def auto_heal_server() -> List[str]:
    """Aplica reparos automaticos aos problemas diagnosticados."""
    actions = []

    # Cria pastas essenciais
    for d in [DATA_DIR, WORLDS_DIR, BACKUPS_DIR, WORLD_BACKUPS_DIR, CUSTOM_PACKS_DIR, RUNTIME_DIR]:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            actions.append(f"Diretorio criado: {d}")

    # Repara permissions.json
    if not PERMISSIONS_JSON.exists():
        template_perm = PROJECT_ROOT / "templates" / "permissions.json.template"
        if template_perm.exists():
            shutil.copy2(template_perm, PERMISSIONS_JSON)
        else:
            PERMISSIONS_JSON.write_text("[]\n", encoding="utf-8")
        actions.append("permissions.json restaurado com sucesso.")

    # Repara allowlist.json
    if not ALLOWLIST_JSON.exists():
        template_allow = PROJECT_ROOT / "templates" / "allowlist.json.template"
        if template_allow.exists():
            shutil.copy2(template_allow, ALLOWLIST_JSON)
        else:
            ALLOWLIST_JSON.write_text("[]\n", encoding="utf-8")
        actions.append("allowlist.json restaurado com sucesso.")

    # Sincroniza pacotes
    sync_packs_to_runtime()
    actions.append("Add-ons sincronizados para o runtime.")

    # Garante Chunker se necessario
    chunker_jar = TOOLS_DIR / "chunker-cli.jar"
    if not chunker_jar.exists() or chunker_jar.stat().st_size < 10_000_000:
        try:
            import instalar_cobbled_farms
            instalar_cobbled_farms.ensure_chunker_jar()
            actions.append("Chunker CLI baixado e validado.")
        except Exception:
            pass

    return actions
