"""Хранилище магазина одежды: категории → подкатегории → товары, заявки, пользователи (SQLite)."""
import sqlite3
from datetime import datetime


class DB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
                created_at TEXT NOT NULL, age_ok INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS admin_sessions (user_id INTEGER PRIMARY KEY, since TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY,
                category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                name TEXT NOT NULL, UNIQUE(category_id, name)
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                brand_id INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                price INTEGER NOT NULL DEFAULT 0,
                sizes TEXT NOT NULL DEFAULT '',       -- размеры в наличии через «|»
                color TEXT NOT NULL DEFAULT '',       -- цвет (просто текст в карточке)
                in_stock INTEGER NOT NULL DEFAULT 1,
                photo TEXT,                            -- file_id фото в Telegram
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, username TEXT, first_name TEXT,
                product_id INTEGER, product TEXT NOT NULL, size TEXT, price INTEGER,
                created_at TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0
            );
        """)
        self.conn.commit()

    def _one(self, sql, *a):
        return self.conn.execute(sql, a).fetchone()

    def _all(self, sql, *a):
        return self.conn.execute(sql, a).fetchall()

    def _run(self, sql, *a):
        cur = self.conn.execute(sql, a)
        self.conn.commit()
        return cur

    # ---------- пользователи ----------
    def touch_user(self, uid, username, first_name):
        self._run("""INSERT INTO users (id, username, first_name, created_at) VALUES (?, ?, ?, ?)
                     ON CONFLICT(id) DO UPDATE SET username = excluded.username, first_name = excluded.first_name""",
                  uid, username, first_name, _now())

    def age_ok(self, uid) -> bool:
        u = self._one("SELECT age_ok FROM users WHERE id = ?", uid)
        return bool(u and u["age_ok"])

    def set_age_ok(self, uid):
        self._run("UPDATE users SET age_ok = 1 WHERE id = ?", uid)

    def user_ids(self) -> list[int]:
        return [r["id"] for r in self._all("SELECT id FROM users")]

    # ---------- сессии админов ----------
    def has_session(self, uid) -> bool:
        return self._one("SELECT 1 FROM admin_sessions WHERE user_id = ?", uid) is not None

    def open_session(self, uid):
        self._run("INSERT OR REPLACE INTO admin_sessions (user_id, since) VALUES (?, ?)", uid, _now())

    def close_session(self, uid):
        self._run("DELETE FROM admin_sessions WHERE user_id = ?", uid)

    # ---------- каталог ----------
    def categories(self):
        return self._all("""SELECT c.*, COUNT(p.id) AS n FROM categories c
                            LEFT JOIN brands b ON b.category_id = c.id LEFT JOIN products p ON p.brand_id = b.id
                            GROUP BY c.id ORDER BY c.name COLLATE NOCASE""")

    def category(self, cid):
        return self._one("SELECT * FROM categories WHERE id = ?", cid)

    def add_category(self, name) -> int:
        row = self._one("SELECT id FROM categories WHERE name = ? COLLATE NOCASE", name)
        return row["id"] if row else self._run("INSERT INTO categories (name) VALUES (?)", name).lastrowid

    def brands(self, cid):
        return self._all("""SELECT b.*, COUNT(p.id) AS n FROM brands b LEFT JOIN products p ON p.brand_id = b.id
                            WHERE b.category_id = ? GROUP BY b.id ORDER BY b.name COLLATE NOCASE""", cid)

    def brand(self, bid):
        return self._one("""SELECT b.*, c.name AS category FROM brands b JOIN categories c ON c.id = b.category_id
                            WHERE b.id = ?""", bid)

    def add_brand(self, cid, name) -> int:
        row = self._one("SELECT id FROM brands WHERE category_id = ? AND name = ? COLLATE NOCASE", cid, name)
        return row["id"] if row else self._run("INSERT INTO brands (category_id, name) VALUES (?, ?)", cid, name).lastrowid

    def rename_category(self, cid, name):
        self._run("UPDATE categories SET name = ? WHERE id = ?", name, cid)

    def rename_brand(self, bid, name):
        self._run("UPDATE brands SET name = ? WHERE id = ?", name, bid)

    def products(self, bid):
        return self._all("SELECT * FROM products WHERE brand_id = ? ORDER BY in_stock DESC, name COLLATE NOCASE", bid)

    def product(self, pid):
        return self._one("""SELECT p.*, b.name AS brand, b.category_id, c.name AS category FROM products p
                            JOIN brands b ON b.id = p.brand_id JOIN categories c ON c.id = b.category_id
                            WHERE p.id = ?""", pid)

    def add_product(self, bid, name, price, sizes, color, in_stock, photo, description) -> int:
        return self._run("""INSERT INTO products (brand_id, name, price, sizes, color, in_stock, photo, description, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         bid, name, price, "|".join(sizes), color, int(in_stock), photo, description, _now()).lastrowid

    def update_product(self, pid, **fields):
        if "sizes" in fields:
            fields["sizes"] = "|".join(fields["sizes"])
        sets = ", ".join(f"{k} = ?" for k in fields)
        self._run(f"UPDATE products SET {sets} WHERE id = ?", *fields.values(), pid)
        self.cleanup()

    def delete_product(self, pid):
        self._run("DELETE FROM products WHERE id = ?", pid)
        self.cleanup()

    def cleanup(self):
        """Убирает пустые бренды и категории, чтобы в каталоге не было пустых разделов."""
        self._run("DELETE FROM brands WHERE id NOT IN (SELECT DISTINCT brand_id FROM products)")
        self._run("DELETE FROM categories WHERE id NOT IN (SELECT DISTINCT category_id FROM brands)")

    # ---------- заявки ----------
    def add_order(self, uid, username, first_name, p, size) -> int:
        name = f"{p['category']} → {p['brand']} → {p['name']}"
        return self._run("""INSERT INTO orders (user_id, username, first_name, product_id, product, size, price, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         uid, username, first_name, p["id"], name, size, p["price"], _now()).lastrowid

    def order(self, oid):
        return self._one("SELECT * FROM orders WHERE id = ?", oid)

    def set_order_done(self, oid):
        self._run("UPDATE orders SET done = 1 WHERE id = ?", oid)

    def recent_orders(self, limit=15):
        return self._all("SELECT * FROM orders ORDER BY id DESC LIMIT ?", limit)

    def stats(self) -> dict:
        q = lambda sql, *a: self._one(sql, *a)[0]
        today = datetime.now().date().isoformat()
        return {
            "users": q("SELECT COUNT(*) FROM users"),
            "products": q("SELECT COUNT(*) FROM products"),
            "in_stock": q("SELECT COUNT(*) FROM products WHERE in_stock = 1"),
            "orders": q("SELECT COUNT(*) FROM orders"),
            "orders_today": q("SELECT COUNT(*) FROM orders WHERE created_at >= ?", today),
            "orders_open": q("SELECT COUNT(*) FROM orders WHERE done = 0"),
        }


def sizes_of(p) -> list[str]:
    return [c for c in (p["sizes"] or "").split("|") if c]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
