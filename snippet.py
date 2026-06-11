#!/usr/bin/env python3
"""
📦 Snippet CLI — Manajer Code Snippet di Terminal
==================================================
Simpen, cari, copy code snippet langsung dari terminal.
Gak perlu buka Google tiap kali lupa syntax!

Cara pakai:
  python snippet.py add          # Tambah snippet baru
  python snippet.py search       # Cari snippet
  python snippet.py list         # Lihat semua
  python snippet.py copy <nama>  # Copy ke clipboard

Made with ❤️ by Nazril
Open source — bebas dipakai & dimodifikasi.
"""

import os
import sys
import json
import sqlite3
import argparse
import datetime
from pathlib import Path
from typing import Optional

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
    from pygments.formatters import TerminalFormatter
    HAVE_PYGMENTS = True
except ImportError:
    HAVE_PYGMENTS = False

try:
    import pyperclip
    HAVE_CLIPBOARD = True
except ImportError:
    HAVE_CLIPBOARD = False


# ═══════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════

DB_PATH = Path.home() / ".snippet-cli" / "snippets.db"


def get_db() -> sqlite3.Connection:
    """Dapetin koneksi database (auto-create)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection):
    """Bikin tabel kalo belum ada."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            language TEXT DEFAULT 'text',
            code TEXT NOT NULL,
            tags TEXT DEFAULT '',
            is_favorite INTEGER DEFAULT 0,
            use_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_snippets_name ON snippets(name);
        CREATE INDEX IF NOT EXISTS idx_snippets_lang ON snippets(language);
        CREATE INDEX IF NOT EXISTS idx_snippets_tags ON snippets(tags);
    """)
    conn.commit()


# ═══════════════════════════════════════════════
#  CORE OPERATIONS
# ═══════════════════════════════════════════════

def add_snippet(args):
    """Tambah snippet baru."""
    conn = get_db()
    name = args.name or input("📝 Nama snippet: ").strip()
    language = args.lang or input("🔤 Bahasa (python,js,go,text): ").strip() or "text"
    desc = args.desc or input("📋 Deskripsi (opsional): ").strip()

    print("📄 Code (paste code, tekan Ctrl+D/Enter 2x kalo selesai):")
    print("─" * 40)
    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except EOFError:
        pass
    code = "\n".join(lines).strip()

    tags_str = args.tags or input("🏷️  Tags (pisah koma, opsional): ").strip()

    if not code:
        print("❌ Code kosong. Gak jadi nambah.")
        return

    try:
        conn.execute(
            """INSERT INTO snippets (name, description, language, code, tags)
               VALUES (?, ?, ?, ?, ?)""",
            (name, desc, language, code, tags_str)
        )
        conn.commit()
        print(f"\n✅ Snippet '{name}' berhasil disimpan!")
    except sqlite3.IntegrityError:
        overwrite = input(f"⚠️  Snippet '{name}' udah ada. Timpa? (y/N): ").strip().lower()
        if overwrite == "y":
            conn.execute(
                """UPDATE snippets SET description=?, language=?, code=?, tags=?,
                   updated_at=datetime('now','localtime') WHERE name=?""",
                (desc, language, code, tags_str, name)
            )
            conn.commit()
            print(f"\n✅ Snippet '{name}' berhasil diupdate!")
        else:
            print("⏹️  Dibatalkan.")


def search_snippets(args):
    """Cari snippet berdasarkan keyword / bahasa / tag."""
    conn = get_db()
    query = args.query or ""
    lang = args.lang or ""
    tag = args.tag or ""
    limit = min(args.limit or 20, 100)

    conditions = []
    params = []

    if query:
        conditions.append("(name LIKE ? OR description LIKE ? OR code LIKE ? OR tags LIKE ?)")
        p = f"%{query}%"
        params.extend([p, p, p, p])

    if lang:
        conditions.append("language = ?")
        params.append(lang)

    if tag:
        conditions.append("tags LIKE ?")
        params.append(f"%{tag}%")

    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"SELECT * FROM snippets WHERE {where} ORDER BY use_count DESC, created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()

    if not rows:
        print("😕 Gak ada snippet yang cocok.")
        return

    print(f"\n📦 Ditemukan {len(rows)} snippet:\n")
    for row in rows:
        fav = "⭐" if row["is_favorite"] else "  "
        use = f"({row['use_count']}x)" if row["use_count"] > 0 else "     "
        name = row["name"]
        lang = row["language"]
        desc = (row["description"] or "")[:40]
        tags = (row["tags"] or "")
        print(f"  {fav} {name:25s} {use:>5s}  [{lang:8s}]  {desc}")
    print()


def list_snippets(args):
    """Tampilkan semua snippet."""
    conn = get_db()
    rows = conn.execute("""
        SELECT *, instr(tags, ',') as tag_count
        FROM snippets ORDER BY is_favorite DESC, use_count DESC, name ASC
    """).fetchall()

    if not rows:
        print("📭 Belum ada snippet. Tambah dulu pake: snippet.py add")
        return

    langs = {}
    for r in rows:
        l = r["language"] or "text"
        langs[l] = langs.get(l, 0) + 1

    print(f"\n📦 Total: {len(rows)} snippet | Bahasa: {len(langs)}")
    print(f"{'─' * 56}")
    for lang, count in sorted(langs.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 20)
        print(f"  {lang:12s}: {count:3d}  {bar}")
    print(f"{'─' * 56}\n")

    for row in rows:
        fav = "⭐" if row["is_favorite"] else "  "
        name = row["name"]
        lang = row["language"]
        use = f"{row['use_count']}x" if row["use_count"] > 0 else " -"
        tags = (row["tags"] or "")[:25]
        print(f"  {fav} {name:25s}  {use:>4s}  [{lang:10s}]  {tags}")

    print()


def show_snippet(args):
    """Tampilkan detail snippet + syntax highlighting."""
    conn = get_db()
    name = args.name
    rows = conn.execute("SELECT * FROM snippets WHERE name = ?", (name,)).fetchall()
    if not rows:
        print(f"❌ Snippet '{name}' gak ditemukan.")
        # Suggestion
        close = conn.execute(
            "SELECT name FROM snippets WHERE name LIKE ? LIMIT 5",
            (f"%{name}%",)
        ).fetchall()
        if close:
            print("   Mungkin maksud lo:")
            for r in close:
                print(f"   • {r['name']}")
        return

    row = rows[0]
    fav = "⭐" if row["is_favorite"] else " "
    tags = row["tags"] or "-"
    use_count = row["use_count"]

    print(f"\n{'═' * 56}")
    print(f"  {fav} {row['name']}")
    print(f"{'═' * 56}")
    print(f"  Bahasa    : {row['language']}")
    print(f"  Tags      : {tags}")
    print(f"  Dipake    : {use_count}x")
    print(f"  Dibuat    : {row['created_at']}")
    if row["description"]:
        print(f"  Deskripsi : {row['description']}")
    print(f"{'─' * 56}")

    code = row["code"]

    if HAVE_PYGMENTS:
        try:
            lexer = get_lexer_by_name(row["language"], stripall=True)
        except:
            try:
                lexer = get_lexer_for_filename(f"file.{row['language']}", stripall=True)
            except:
                lexer = None

        if lexer:
            print(highlight(code, lexer, TerminalFormatter()))
        else:
            print(code)
    else:
        # Fallback: kasih line number
        for i, line in enumerate(code.split("\n"), 1):
            print(f"  {i:3d} | {line}")

    print(f"{'─' * 56}")
    print(f"  💡 Copy: python snippet.py copy {row['name']}")
    print()

    # Increment use count
    conn.execute("UPDATE snippets SET use_count = use_count + 1 WHERE name = ?", (name,))
    conn.commit()


def copy_snippet(args):
    """Copy snippet ke clipboard."""
    if not HAVE_CLIPBOARD:
        print("❌ pyperclip gak terinstall. Jalankan: pip install pyperclip")
        return

    conn = get_db()
    name = args.name
    rows = conn.execute("SELECT code FROM snippets WHERE name = ?", (name,)).fetchall()

    if not rows:
        print(f"❌ Snippet '{name}' gak ditemukan.")
        return

    code = rows[0]["code"]
    try:
        pyperclip.copy(code)
        # Hitung baris
        lines = code.count("\n") + 1
        chars = len(code)
        print(f"✅ Snippet '{name}' ({lines} baris, {chars} chars) udah di-copy!")
        print(f"📋 Tinggal paste (Ctrl+V) di mana aja.")
    except Exception as e:
        print(f"❌ Gagal copy ke clipboard: {e}")
        print(f"   Manual copy:\n{code}")


def edit_snippet(args):
    """Edit snippet yang udah ada."""
    conn = get_db()
    name = args.name
    rows = conn.execute("SELECT * FROM snippets WHERE name = ?", (name,)).fetchall()

    if not rows:
        print(f"❌ Snippet '{name}' gak ditemukan.")
        return

    row = rows[0]
    print(f"✏️  Edit snippet '{name}' (Enter = skip):\n")

    lang = input(f"  Bahasa [{row['language']}]: ").strip() or row["language"]
    desc = input(f"  Deskripsi [{row['description'] or '-'}]: ").strip() or row["description"]
    tags = input(f"  Tags [{row['tags'] or '-'}]: ").strip() or row["tags"]

    conn.execute(
        """UPDATE snippets SET language=?, description=?, tags=?, updated_at=datetime('now','localtime')
           WHERE name=?""",
        (lang, desc, tags, name)
    )
    conn.commit()
    print(f"\n✅ Snippet '{name}' berhasil diupdate!")


def delete_snippet(args):
    """Hapus snippet."""
    conn = get_db()
    name = args.name
    rows = conn.execute("SELECT name FROM snippets WHERE name = ?", (name,)).fetchall()

    if not rows:
        print(f"❌ Snippet '{name}' gak ditemukan.")
        return

    confirm = input(f"⚠️  Yakin mau hapus '{name}'? (y/N): ").strip().lower()
    if confirm == "y":
        conn.execute("DELETE FROM snippets WHERE name = ?", (name,))
        conn.commit()
        print(f"🗑️  Snippet '{name}' berhasil dihapus.")
    else:
        print("⏹️  Dibatalkan.")


def favorite_snippet(args):
    """Toggle favorite snippet."""
    conn = get_db()
    name = args.name
    rows = conn.execute("SELECT is_favorite FROM snippets WHERE name = ?", (name,)).fetchall()

    if not rows:
        print(f"❌ Snippet '{name}' gak ditemukan.")
        return

    current = rows[0]["is_favorite"]
    new = 0 if current else 1
    conn.execute("UPDATE snippets SET is_favorite = ? WHERE name = ?", (new, name))
    conn.commit()

    if new:
        print(f"⭐ Snippet '{name}' ditandai sebagai favorit!")
    else:
        print(f" Snippet '{name}' dihapus dari favorit.")


def export_snippets(args):
    """Export semua snippet ke file JSON."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM snippets ORDER BY name").fetchall()

    output = args.output or f"snippets-export-{datetime.date.today()}.json"
    data = []

    for row in rows:
        data.append({
            "name": row["name"],
            "description": row["description"],
            "language": row["language"],
            "code": row["code"],
            "tags": row["tags"],
            "is_favorite": bool(row["is_favorite"]),
            "created_at": row["created_at"],
        })

    export = {
        "exported_at": datetime.datetime.now().isoformat(),
        "tool": "Snippet CLI v1.0",
        "total": len(data),
        "snippets": data,
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(data)} snippet di-export ke: {output}")


def import_snippets(args):
    """Import snippet dari file JSON."""
    path = args.path
    if not os.path.exists(path):
        print(f"❌ File gak ditemukan: {path}")
        return

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    snippets = data.get("snippets", [])
    if not snippets:
        print("❌ Gak ada snippet di file ini.")
        return

    conn = get_db()
    imported = 0
    skipped = 0

    for s in snippets:
        try:
            conn.execute(
                """INSERT INTO snippets (name, description, language, code, tags, is_favorite)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (s["name"], s.get("description", ""), s.get("language", "text"),
                 s["code"], s.get("tags", ""), 1 if s.get("is_favorite") else 0)
            )
            imported += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    print(f"✅ {imported} snippet berhasil di-import!")
    if skipped:
        print(f"⚠️  {skipped} snippet dilewati (nama udah ada).")


def stats_snippet(args):
    """Statistik penggunaan snippet."""
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) as c FROM snippets").fetchone()["c"]
    total_use = conn.execute("SELECT SUM(use_count) as c FROM snippets").fetchone()["c"] or 0
    fav_count = conn.execute("SELECT COUNT(*) as c FROM snippets WHERE is_favorite = 1").fetchone()["c"]
    languages = conn.execute("SELECT COUNT(DISTINCT language) as c FROM snippets").fetchone()["c"]

    top = conn.execute(
        "SELECT name, use_count FROM snippets ORDER BY use_count DESC LIMIT 5"
    ).fetchall()

    recent = conn.execute(
        "SELECT name, created_at FROM snippets ORDER BY created_at DESC LIMIT 5"
    ).fetchall()

    print(f"\n{'═' * 56}")
    print(f"  📊 STATISTIK SNIPPET")
    print(f"{'═' * 56}")
    print(f"  📦 Total snippet    : {total}")
    print(f"  👆 Total dipake     : {total_use}x")
    print(f"  ⭐ Favorit          : {fav_count}")
    print(f"  🔤 Bahasa           : {languages}")
    print(f"{'─' * 56}")

    if top:
        print(f"\n  🔥 Paling sering dipake:")
        for r in top:
            print(f"    {r['name']:25s}  ({r['use_count']}x)")
    if recent:
        print(f"\n  🆕 Terbaru:")
        for r in recent:
            print(f"    {r['name']:25s}  {r['created_at']}")

    # Cek db size
    db_size = os.path.getsize(DB_PATH) if DB_PATH.exists() else 0
    print(f"\n  💾 Database          : {db_size / 1024:.1f} KB")
    print()


def reset_snippets(args):
    """Hapus semua snippet & database."""
    confirm = input("⚠️⚠️⚠️  Yakin mau reset SEMUA snippet? (ketik 'reset'): ").strip()
    if confirm != "reset":
        print("⏹️  Dibatalkan.")
        return

    conn = get_db()
    conn.execute("DELETE FROM snippets")
    conn.commit()
    print("🗑️  Semua snippet berhasil dihapus.")

    # Compact database
    conn.execute("VACUUM")
    print("💾 Database di-compact.")


# ═══════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="📦 Snippet CLI — Manajer Code Snippet di Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python snippet.py add                         # Tambah snippet
  python snippet.py search flask                # Cari snippet
  python snippet.py list                        # Lihat semua snippet
  python snippet.py show flask_route            # Detail + syntax highlight
  python snippet.py copy flask_route            # Copy ke clipboard
  python snippet.py favorite flask_route        # Tandai favorit
  python snippet.py stats                       # Statistik
  python snippet.py export                      # Export ke JSON
  python snippet.py import snippets.json        # Import dari JSON
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Perintah")

    # add
    p_add = subparsers.add_parser("add", help="Tambah snippet baru")
    p_add.add_argument("--name", "-n", default="", help="Nama snippet")
    p_add.add_argument("--lang", "-l", default="", help="Bahasa pemrograman")
    p_add.add_argument("--desc", "-d", default="", help="Deskripsi")
    p_add.add_argument("--tags", "-t", default="", help="Tags (pisah koma)")

    # search
    p_search = subparsers.add_parser("search", aliases=["find", "cari"],
                                     help="Cari snippet")
    p_search.add_argument("query", nargs="?", default="", help="Kata kunci")
    p_search.add_argument("--lang", "-l", default="", help="Filter bahasa")
    p_search.add_argument("--tag", "-t", default="", help="Filter tag")
    p_search.add_argument("--limit", type=int, default=20, help="Maks hasil")

    # list
    subparsers.add_parser("list", aliases=["ls", "all"],
                          help="Tampilkan semua snippet")

    # show
    p_show = subparsers.add_parser("show", aliases=["get", "view"],
                                   help="Lihat detail snippet")
    p_show.add_argument("name", help="Nama snippet")

    # copy
    p_copy = subparsers.add_parser("copy", aliases=["cp"],
                                   help="Copy snippet ke clipboard")
    p_copy.add_argument("name", help="Nama snippet")

    # edit
    p_edit = subparsers.add_parser("edit", help="Edit snippet")
    p_edit.add_argument("name", help="Nama snippet")

    # delete
    p_delete = subparsers.add_parser("delete", aliases=["del", "rm", "hapus"],
                                     help="Hapus snippet")
    p_delete.add_argument("name", help="Nama snippet")

    # favorite
    p_fav = subparsers.add_parser("favorite", aliases=["fav", "star"],
                                  help="Toggle favorit")
    p_fav.add_argument("name", help="Nama snippet")

    # export
    p_export = subparsers.add_parser("export", help="Export snippet ke JSON")
    p_export.add_argument("--output", "-o", default="", help="Nama file output")

    # import
    p_import = subparsers.add_parser("import", help="Import snippet dari JSON")
    p_import.add_argument("path", help="Path file JSON")

    # stats
    subparsers.add_parser("stats", aliases=["stat"],
                          help="Statistik snippet")

    # reset
    subparsers.add_parser("reset", help="⚠️  Hapus semua snippet & database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n💡 Tambah snippet: python snippet.py add")
        print("📋 Lihat semua:   python snippet.py list")
        return

    # Handle aliases
    cmd = args.command
    if cmd in ("find", "cari"):
        cmd = "search"
    elif cmd in ("ls", "all"):
        cmd = "list"
    elif cmd in ("get", "view"):
        cmd = "show"
    elif cmd in ("cp",):
        cmd = "copy"
    elif cmd in ("del", "rm", "hapus"):
        cmd = "delete"
    elif cmd in ("fav", "star"):
        cmd = "favorite"
    elif cmd in ("stat",):
        cmd = "stats"

    commands = {
        "add": add_snippet,
        "search": search_snippets,
        "list": list_snippets,
        "show": show_snippet,
        "copy": copy_snippet,
        "edit": edit_snippet,
        "delete": delete_snippet,
        "favorite": favorite_snippet,
        "export": export_snippets,
        "import": import_snippets,
        "stats": stats_snippet,
        "reset": reset_snippets,
    }

    if cmd in commands:
        commands[cmd](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
