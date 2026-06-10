import os
import shutil
import tarfile
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

ACTIVE_LLM_DIR = BASE_DIR / "active_profile"
SANDBOX_STORAGE_DIR = BASE_DIR / "sandbox_storage"

PROFILE_STATE_FILE = SANDBOX_STORAGE_DIR / ".last_active_profile"

PROFILES = {
    "1": "Technical_Work_Profile",
    "2": "Private_Companion_Profile"
}

CACHE_DIRS = [
    BASE_DIR / "cache",
    BASE_DIR / "temp",
    BASE_DIR / "runtime_cache"
]


def clear_system_cache():
    """
    Removes application-managed cache directories and recreates them.
    Only operates inside this project's directory tree.
    """
    print("[*] Initiating system context purge...")

    for cache_dir in CACHE_DIRS:
        try:
            if cache_dir.exists():
                shutil.rmtree(cache_dir)

            cache_dir.mkdir(parents=True, exist_ok=True)

        except Exception as exc:
            print(f"[!] Failed to clear cache: {cache_dir}")
            print(f"    {exc}")

    print("[+] Context buffer successfully cleared.")


def get_last_active_profile():
    try:
        if PROFILE_STATE_FILE.exists():
            return PROFILE_STATE_FILE.read_text().strip()
    except Exception:
        pass

    return "Unknown_Profile"


def set_last_active_profile(profile_name):
    SANDBOX_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    with open(PROFILE_STATE_FILE, "w", encoding="utf-8") as f:
        f.write(profile_name)


def backup_active_profile(current_profile_name):
    if (
        not ACTIVE_LLM_DIR.exists()
        or not any(ACTIVE_LLM_DIR.iterdir())
    ):
        print("[-] Active directory empty. Skipping backup phase.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_filename = f"{current_profile_name}_{timestamp}.tar.gz"

    backup_dir = SANDBOX_STORAGE_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / backup_filename

    print(f"[*] Archiving active context to: {backup_filename}...")

    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add(
            str(ACTIVE_LLM_DIR),
            arcname=ACTIVE_LLM_DIR.name
        )

    print("[+] Backup execution finalized.")


def swap_profile(target_profile_id):
    target_profile_name = PROFILES.get(target_profile_id)

    if not target_profile_name:
        print("[-] Invalid profile selection.")
        return

    target_profile_path = SANDBOX_STORAGE_DIR / target_profile_name
    target_profile_path.mkdir(parents=True, exist_ok=True)

    last_active = get_last_active_profile()

    backup_active_profile(last_active)

    clear_system_cache()

    print("[*] Clearing active profile directory...")

    if ACTIVE_LLM_DIR.exists():
        shutil.rmtree(ACTIVE_LLM_DIR)

    ACTIVE_LLM_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[*] Rehydrating environment: {target_profile_name}...")

    for item in target_profile_path.iterdir():
        destination = ACTIVE_LLM_DIR / item.name

        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)

    set_last_active_profile(target_profile_name)

    print(f"[++] Boundary shift complete. Active Persona: {target_profile_name}")


if __name__ == "__main__":
    print("==========================================")
    print("   LOCAL PERSONA MEMORY SANDBOX MANAGER   ")
    print("==========================================")

    print("Select target execution profile:")
    print("1 - Technical / Work Directory")
    print("2 - Private / Companion Containment")

    choice = input("\\nEnter selection (1 or 2): ").strip()

    if choice in PROFILES:
        swap_profile(choice)
    else:
        print("[-] Operation canceled: Invalid input parameter.")
        sys.exit(1)
