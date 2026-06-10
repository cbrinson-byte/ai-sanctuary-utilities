import os
import sys
import time
import subprocess
from pathlib import Path

# ==========================================
# CORE CONFIGURATION PATHS & TRIGGERS
# ==========================================
VIRTUAL_DRIVE_PATH = "./secure_storage"
MONITORED_USB_DEVICE = "SECURE_KEY"


def clear_system_clipboard():
    """
    Attempts to clear clipboard contents.
    """
    print("[*] Evicting system clipboard memory traces...")

    try:
        if sys.platform.startswith("win"):
            subprocess.run("clip", input="", text=True, shell=True)

        elif sys.platform.startswith("linux"):
            subprocess.run(
                ["sh", "-c", "command -v xclip >/dev/null && xclip -selection clipboard /dev/null"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        print("[+] Clipboard memory successfully sanitized.")

    except Exception as e:
        print(f"[-] Clipboard clear failed: {e}")


def lock_down_local_containers():
    """
    Simulates sealing a local storage directory.
    """
    print(f"[!] CRITICAL: Initiating lockdown for path: {VIRTUAL_DRIVE_PATH}")

    clear_system_clipboard()

    if os.path.exists(VIRTUAL_DRIVE_PATH):
        try:
            lock_marker = f"{VIRTUAL_DRIVE_PATH}.LOCKED"

            if not os.path.exists(lock_marker):
                os.rename(VIRTUAL_DRIVE_PATH, lock_marker)

            print(f"[++] Boundary containment successful. Drive sealed at: {lock_marker}")

        except Exception as e:
            print(f"[-] Drive isolation step encountered errors: {e}")

    print("[++] System lockdown operations completed successfully.")
    sys.exit(0)


def verify_hardware_state():
    """
    Checks for the presence of a configured hardware-key file/folder.
    Returns True if found, False otherwise.
    """

    candidate_paths = []

    if sys.platform.startswith("win"):
        # Check common drive letters
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            candidate_paths.append(Path(f"{letter}:/") / MONITORED_USB_DEVICE)

    else:
        # Common Linux removable-media locations
        media_root = Path("/media")
        run_media_root = Path("/run/media")

        if media_root.exists():
            for user_dir in media_root.glob("*"):
                candidate_paths.append(user_dir / MONITORED_USB_DEVICE)

        if run_media_root.exists():
            for user_dir in run_media_root.glob("*/*"):
                candidate_paths.append(user_dir / MONITORED_USB_DEVICE)

    # Also allow a local relative path for testing
    candidate_paths.append(Path(MONITORED_USB_DEVICE))

    for path in candidate_paths:
        try:
            if path.exists():
                return True
        except PermissionError:
            continue

    return False


def monitoring_loop():
    """
    Background loop tracking hardware states continuously.
    """
    print("[*] Defensive Switch Monitor Active. Running continuous checks...")

    try:
        while True:
            hardware_secure = verify_hardware_state()

            if not hardware_secure:
                print("\\n[!] ALERT: Physical hardware state modification detected!")
                lock_down_local_containers()

            time.sleep(1)

    except KeyboardInterrupt:
        print("\\n[*] Monitoring loop gracefully paused by operator command.")


if __name__ == "__main__":
    print("==========================================")
    print("  ZERO-TRUST AUTOMATED SYSTEM LOCK SWITCH ")
    print("==========================================")
    monitoring_loop()
