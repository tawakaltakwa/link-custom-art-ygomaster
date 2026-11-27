#!/usr/bin/env python3
import os
import sys
import shutil
import sqlite3
import argparse

def load_ydk_map(ydk_file):
    mapping = {}
    if not os.path.exists(ydk_file):
        print(f"[!] Warning: File {ydk_file} tidak ditemukan.")
        return mapping
    with open(ydk_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                # passcode -> master duel id
                mapping[parts[0]] = parts[1]
    return mapping

def load_cdb_names(cdb_file):
    names = {}
    if os.path.exists(cdb_file):
        try:
            con = sqlite3.connect(cdb_file)
            cur = con.cursor()
            for row in cur.execute("SELECT id, name FROM texts"):
                names[str(row[0])] = row[1]
            con.close()
        except Exception as e:
            print(f"[!] Warning: Gagal membaca database {cdb_file}: {e}")
    return names

def clean_target(clean_path, dry_run=False):
    """Menghapus seluruh file/symlink custom art di ClientData/Card/Images/Illust/tcg"""
    clean_path = os.path.abspath(clean_path)
    if not os.path.exists(clean_path):
        print(f"[i] Folder tujuan tidak ada atau sudah bersih: {clean_path}")
        return

    print(f"[*] Membersihkan custom art di: {clean_path}")
    count = 0
    for root, dirs, files in os.walk(clean_path, topdown=False):
        for f in files:
            file_path = os.path.join(root, f)
            print(f"[-] [DELETE] {file_path}")
            if not dry_run:
                try:
                    if os.path.islink(file_path) or os.path.isfile(file_path):
                        os.remove(file_path)
                    count += 1
                except Exception as e:
                    print(f"[!] Gagal menghapus {file_path}: {e}")
            else:
                count += 1

        for d in dirs:
            dir_path = os.path.join(root, d)
            if not dry_run:
                try:
                    if os.path.islink(dir_path):
                        os.remove(dir_path)
                    elif not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except Exception:
                    pass

    # Bersihkan folder target jika kosong
    if not dry_run and os.path.isdir(clean_path) and not os.listdir(clean_path):
        try:
            os.rmdir(clean_path)
        except Exception:
            pass

    print("\n" + "="*50)
    print(f"Pembersihan selesai! Total item dihapus: {count}")
    print("="*50)

def main():
    parser = argparse.ArgumentParser(description="Map custom card arts from printed passcode to Master Duel ID or clean installed arts.")
    parser.add_argument("--src", default="custom/Kartu", help="Folder sumber custom art (default: custom/Kartu)")
    parser.add_argument("--dst", default="Data/ClientData/Card/Images/Illust/tcg", help="Folder tujuan (default: ClientData/Card/Images/Illust/tcg)")
    parser.add_argument("--ydk", default="Data/YdkIds.txt", help="Path ke YdkIds.txt")
    parser.add_argument("--cdb", default="custom/cards.cdb", help="Path ke cards.cdb")
    parser.add_argument("--copy", action="store_true", help="Gunakan penyalinan (copy) alih-alih symlink")
    parser.add_argument("--force", action="store_true", help="Timpa file yang sudah ada di folder tujuan")
    parser.add_argument("--dry-run", action="store_true", help="Hanya tampilkan simulasi tanpa membuat/menghapus file")
    parser.add_argument("--clean", action="store_true", help="Hapus seluruh custom art di ClientData/Card/Images/Illust/tcg (atau sesuai --dst)")

    args = parser.parse_args()

    # Eksekusi mode clean jika diminta
    if args.clean:
        clean_target(args.dst, dry_run=args.dry_run)
        return

    # Normalisasi path jika symlink folder ada perbedaan huruf besar/kecil
    src_dir = os.path.abspath(args.src)
    if not os.path.exists(src_dir) and os.path.exists(os.path.join(os.path.dirname(src_dir), "kartu")):
        src_dir = os.path.abspath(os.path.join(os.path.dirname(src_dir), "kartu"))
    elif not os.path.exists(src_dir) and os.path.exists(os.path.join(os.path.dirname(src_dir), "Kartu")):
        src_dir = os.path.abspath(os.path.join(os.path.dirname(src_dir), "Kartu"))

    dst_dir = os.path.abspath(args.dst)
    ydk_file = os.path.abspath(args.ydk)
    cdb_file = os.path.abspath(args.cdb)

    if not os.path.isdir(src_dir):
        print(f"[X] Error: Folder sumber tidak ditemukan: {src_dir}")
        sys.exit(1)

    os.makedirs(dst_dir, exist_ok=True)

    print(f"[*] Folder Sumber : {src_dir}")
    print(f"[*] Folder Tujuan : {dst_dir}")
    print(f"[*] Mode Operasi  : {'COPY' if args.copy else 'SYMLINK'}")
    if args.dry_run:
        print("[*] Mode DRY RUN aktif (tidak ada perubahan berkas).")

    passcode_to_md = load_ydk_map(ydk_file)
    cdb_names = load_cdb_names(cdb_file)

    processed = 0
    skipped = 0
    missing = 0

    files = sorted(os.listdir(src_dir))
    for filename in files:
        base, ext = os.path.splitext(filename)
        if ext.lower() not in ['.png', '.jpg', '.jpeg']:
            continue

        src_path = os.path.join(src_dir, filename)
        
        # Ambil MD ID dari passcode/cdb ID
        md_id = passcode_to_md.get(base)
        card_name = cdb_names.get(base, "Unknown Card")

        if not md_id:
            print(f"[-] [MISSING] {filename} (Passcode: {base}, '{card_name}') -> Tidak ditemukan di YdkIds.txt!")
            missing += 1
            continue

        dst_filename = f"{md_id}{ext.lower()}"
        dst_path = os.path.join(dst_dir, dst_filename)

        if os.path.lexists(dst_path):
            if not args.force:
                print(f"[~] [SKIP] {dst_filename} sudah ada di tujuan (dari {filename} / '{card_name}'). Gunakan --force untuk menimpa.")
                skipped += 1
                continue
            else:
                if not args.dry_run:
                    if os.path.islink(dst_path) or os.path.isfile(dst_path):
                        os.remove(dst_path)
                    elif os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)

        action_desc = "COPY" if args.copy else "LINK"
        print(f"[+] [{action_desc}] {filename} -> {dst_filename} ({card_name})")

        if not args.dry_run:
            try:
                if args.copy:
                    shutil.copy2(src_path, dst_path)
                else:
                    os.symlink(src_path, dst_path)
                processed += 1
            except Exception as e:
                print(f"[!] Gagal memproses {filename}: {e}")

    print("\n" + "="*50)
    print(f"Selesai! Berhasil: {processed}, Dilewati: {skipped}, Tidak Terdaftar: {missing}")
    print("="*50)

if __name__ == "__main__":
    main()
