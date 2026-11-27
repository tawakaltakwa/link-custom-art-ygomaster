# Deskripsi
Custom Art Cards untuk [YgoMaster](https://github.com/pixeltris/YgoMaster). Custom Art Cards milikmu (buatanmu sendiri atau asset hasil download dari web) menggunakan nama file berdasarkan ID kartu cetak, sedangkan YgoMaster menggunakan ID tersendiri sesuai Master Duel. Script ini membuat salinan gambar dan/atau symbolik link dengan mengganti nama sesuai dengan ID master duel ke direktori ClientData di YgoMaster. Membutuhkan [cards.cdb](custom/cards.cdb) (direpo ini cards.cdb hasil salinan dari instalasi [KoishiPro](https://koishi.pro/))

# Cara Kerja Script
1. Membaca file gambar dari custom/Kartu (atau custom/kartu).
2. Mencocokkan Passcode (nama file .png) dengan Master Duel ID melalui Data/YdkIds.txt.
3. Membaca nama kartu dari custom/cards.cdb sebagai label keterangan di terminal.
Membuat symlink (atau opsi copy) ke Data/ClientData/Card/Images/Illust/tcg/<md_id>.png.

# Penggunaan
Simpan file [link_custom_art.py](link_custom_art.py) dan folder [custom](custom/) di folder YgoMaster dan Jalankan perintah:
1. Simulasi (Dry Run) tanpa mengubah file apa pun:
    ```
    python3 link_custom_art.py --dry-run
    ```
2. Membuat Symlink (Dianjurkan, hemat disk & otomatis update jika file asli diedit):
    ```
    python3 link_custom_art.py --force
    ```
3. Menyalin Berkas Fisik (Copy file alih-alih symlink):
    ```
    python3 link_custom_art.py --copy --force
    ```
Argumen Tambahan (Opsional):
* --src: Path custom folder kartu (default: custom/Kartu).
* --dst: Path folder tujuan dump (default: Data/ClientData/Card/Images/Illust/tcg).
* --force: Menimpa link/file lama jika sudah ada.
* --copy: Menggandakan file (bukan symlink).
* --clean: Menghapus seluruh folder Data/ClientData/Card/Images/Illust beserta isinya (symlink/file salinan custom art).
* --dry-run: Dapat dikombinasikan dengan --clean  untuk melihat daftar file yang akan dihapus tanpa benar-benar menghapusnya.