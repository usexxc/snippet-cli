# 📦 Snippet CLI

**Manajer Code Snippet di Terminal — Simpen & cari code snippet langsung dari terminal. Gak perlu buka Google tiap kali lupa syntax!**

## 🚀 Install

```bash
git clone https://github.com/usexxc/snippet-cli
cd snippet-cli
pip install pygments pyperclip
```

## 💻 Cara Pake

```bash
# Tambah snippet
python snippet.py add

# Cari snippet
python snippet.py search flask

# Lihat detail + syntax highlighting
python snippet.py show flask_route

# Copy ke clipboard (tinggal paste Ctrl+V)
python snippet.py copy flask_route

# Lihat semua snippet
python snippet.py list

# Statistik
python snippet.py stats

# Export/Import
python snippet.py export
python snippet.py import snippets.json
```

## ✨ Fitur

| Fitur | Keterangan |
|-------|-----------|
| ✅ **Tambah snippet** | Nama + code + bahasa + tag + deskripsi |
| ✅ **Search** | Cari berdasarkan keyword, bahasa, atau tag |
| ✅ **Syntax highlighting** | Pake Pygments — 500+ bahasa didukung |
| ✅ **Copy ke clipboard** | Langsung paste di editor/code mana aja |
| ✅ **Favorit** | Tandai snippet favorit dengan ⭐ |
| ✅ **Statistik** | Lihat snippet paling sering dipake |
| ✅ **Export/Import JSON** | Backup atau share snippet ke temen |
| ✅ **SQLite database** | Data aman, gak ilang walau direstart |
| ✅ **Alias** | `search` = `find` = `cari`, `copy` = `cp`, dll |

## 📂 Database

Tersimpan di: `~/.snippet-cli/snippets.db`

## 📜 Lisensi

MIT — bebas dipakai, dimodifikasi, disebarkan.
