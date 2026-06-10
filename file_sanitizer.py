import os
import shutil
import time
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    Image = None

LANDING_ZONE = "./landing_zone"
SECURE_STORAGE_DOCS = "./secure_storage/documents"
SECURE_STORAGE_MEDIA = "./secure_storage/media"
SECURE_STORAGE_UNKNOWN = "./secure_storage/unverified"

SAFE_DOC_EXTENSIONS = ['.txt', '.pdf', '.md', '.json', '.csv']
SAFE_MEDIA_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.mp3', '.mp4', '.wav']


def init_directories():
    """Ensures local file scaffolding exists before execution."""
    for folder in [
        LANDING_ZONE,
        SECURE_STORAGE_DOCS,
        SECURE_STORAGE_MEDIA,
        SECURE_STORAGE_UNKNOWN
    ]:
        os.makedirs(folder, exist_ok=True)


def get_unique_destination(dest_path):
    """
    Avoid filename collisions by appending _v2, _v3, etc.
    """
    if not os.path.exists(dest_path):
        return dest_path

    directory, filename = os.path.split(dest_path)
    stem, ext = os.path.splitext(filename)

    counter = 2
    while True:
        candidate = os.path.join(directory, f"{stem}_v{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def strip_metadata(file_path, extension):
    """
    Attempts to remove image metadata such as EXIF/GPS tags.
    Falls back to returning the original file for unsupported formats.
    """
    print(f"[*] Sanitizing metadata telemetry for: {os.path.basename(file_path)}")

    image_exts = {".jpg", ".jpeg", ".png"}

    if extension.lower() in image_exts and Image is not None:
        try:
            with Image.open(file_path) as img:
                data = list(img.getdata())

                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(data)

                clean_path = file_path + ".sanitized"
                clean_img.save(clean_path)

            os.replace(clean_path, file_path)
            print("[+] Image metadata removed.")
        except Exception as exc:
            print(f"[!] Metadata removal skipped: {exc}")
    else:
        print("[*] No metadata sanitization routine available for this file type.")

    return file_path


def analyze_and_route_file(file_name):
    """
    Inspects extensions, strips telemetry, and routes cleanly to storage.
    """
    source_path = os.path.join(LANDING_ZONE, file_name)

    if os.path.isdir(source_path):
        return

    _, ext = os.path.splitext(file_name.lower())
    timestamp = datetime.now().strftime("%Y%m%d")
    clean_name = f"{timestamp}_{file_name}"

    if ext in SAFE_DOC_EXTENSIONS:
        sanitized_file = strip_metadata(source_path, ext)

        dest_path = os.path.join(SECURE_STORAGE_DOCS, clean_name)
        dest_path = get_unique_destination(dest_path)

        shutil.move(sanitized_file, dest_path)
        print(f"[++] Document secured and routed to: {dest_path}")

    elif ext in SAFE_MEDIA_EXTENSIONS:
        sanitized_file = strip_metadata(source_path, ext)

        dest_path = os.path.join(SECURE_STORAGE_MEDIA, clean_name)
        dest_path = get_unique_destination(dest_path)

        shutil.move(sanitized_file, dest_path)
        print(f"[++] Media file secured and routed to: {dest_path}")

    else:
        dest_path = os.path.join(SECURE_STORAGE_UNKNOWN, file_name)
        dest_path = get_unique_destination(dest_path)

        shutil.move(source_path, dest_path)

        print(
            f"[-] WARNING: Unverified payload extension ({ext}). "
            f"Quarantined to: {dest_path}"
        )


def monitor_landing_zone():
    """Continuously watches folder for incoming local transfers."""
    print(f"[*] DecontamLocal Active. Monitoring '{LANDING_ZONE}' directory...")

    try:
        while True:
            files = os.listdir(LANDING_ZONE)

            if files:
                print(f"[!] Target files detected incoming: {len(files)} items.")

                for file_name in files:
                    try:
                        analyze_and_route_file(file_name)
                    except Exception as e:
                        print(f"[-] Processing breakdown for {file_name}: {e}")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\\n[*] Monitoring loop deactivated gracefully by user.")


if __name__ == "__main__":
    print("==========================================")
    print("   DECONTAMLOCAL: AIR-GAP FILE SANITIZER  ")
    print("==========================================")

    init_directories()
    monitor_landing_zone()
