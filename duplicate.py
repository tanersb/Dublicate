import os
import logging
import click
import shutil
import hashlib
from collections import defaultdict

# Logging yapılandırması
logging.basicConfig(
    filename="history.log",
    format="%(asctime)s %(levelname)s: %(message)s",
    filemode="a"
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def _checksum(folder_path, file_path):
    """
    Dosyanın checksum değerini (MD5 hash) hesaplar.
    """
    absolute_path = os.path.join(folder_path, file_path)
    try:
        # Dosya içeriğini oku ve hash değerini hesapla
        with open(absolute_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except PermissionError as e:
        logger.error(f"PermissionError: {e} - {absolute_path}")
        print(f"Permission denied: {absolute_path}")
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {e} - {absolute_path}")
        print(f"File not found: {absolute_path}")
    except Exception as e:
        logger.error(f"Unexpected error: {e} - {absolute_path}")
        print(f"Unexpected error: {e} - {absolute_path}")
    return None

def scan(folder_path):
    """
    Verilen klasördeki dosyaları tarar ve hash değerlerine göre gruplar.
    """
    hashes = defaultdict(list)
    try:
        files = os.listdir(folder_path)
    except PermissionError as e:
        logger.error(f"PermissionError: {e} - {folder_path}")
        print(f"Permission denied: {folder_path}")
        return hashes
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {e} - {folder_path}")
        print(f"Folder not found: {folder_path}")
        return hashes

    for file in files:
        absolute_path = os.path.join(folder_path, file)

        # Gizli dosya ve klasörleri atla
        if file.startswith(".") or file.startswith("_"):
            logger.info(f"Skipping hidden file or directory: {absolute_path}")
            print(f"Skipping hidden file or directory: {absolute_path}")
            continue

        # Okuma izni kontrolü
        if not os.access(absolute_path, os.R_OK):
            logger.warning(f"Skipping inaccessible file: {absolute_path}")
            print(f"Skipping inaccessible file: {absolute_path}")
            continue

        # Dosya hash'ini al
        hash = _checksum(folder_path, file)
        if hash:  # Eğer hash None değilse
            hashes[hash].append(file)
    return hashes

def fuse(hashes, folder_path, remove_files=False, save_log=True):
    """
    Aynı hash değerine sahip dosyaları işleme alır:
    - remove_files=True: Dosyaları siler.
    - remove_files=False: Dosyaları "duplicates" klasörüne taşır.
    """
    if not remove_files:
        duplicates_dir = "./duplicates"
        if not os.path.exists(duplicates_dir):
            os.makedirs(duplicates_dir)

    for key, files in hashes.items():
        if len(files) > 1:
            print(f"Duplicate found with hash {key}: {files}")
            original_file = files.pop(0)  # İlk dosyayı ana dosya olarak belirle

            for file in files:
                file_absolute_path = os.path.join(folder_path, file)
                try:
                    if remove_files:  # Dosyayı sil
                        os.remove(file_absolute_path)
                        if save_log:
                            logger.info(f"Deleted: {file_absolute_path}")
                    else:  # Dosyayı "duplicates" klasörüne taşı
                        shutil.move(file_absolute_path, duplicates_dir)
                        if save_log:
                            logger.info(
                                f"Moved '{file_absolute_path}' to '{duplicates_dir}'"
                            )
                except PermissionError as e:
                    logger.error(f"PermissionError: {e} - {file_absolute_path}")
                    print(f"Permission denied: {file_absolute_path}")
                except FileNotFoundError as e:
                    logger.error(f"FileNotFoundError: {e} - {file_absolute_path}")
                    print(f"File not found: {file_absolute_path}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e} - {file_absolute_path}")
                    print(f"Unexpected error: {e} - {file_absolute_path}")
        else:
            print("No duplicates found.")

@click.command()
@click.argument("folder_path", default="./")
@click.option(
    "-R",
    "--remove",
    is_flag=True,
    help="Remove files instead of moving them."
)
@click.option(
    "-L",
    "--log",
    is_flag=True,
    help="Save logs for actions performed."
)
def main(folder_path, remove, log):
    """
    Klasördeki dosyaları tarar, tekrar eden dosyaları tespit eder ve işlem yapar.
    """
    # Klasörün varlığını ve erişilebilirliğini kontrol et
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    if not os.access(folder_path, os.R_OK):
        print(f"Error: No read access to the folder '{folder_path}'.")
        return

    hashes = scan(folder_path)
    fuse(hashes, folder_path, remove_files=remove, save_log=log)

if __name__ == "__main__":
    main()
