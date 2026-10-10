"""Хранилище: пользователи, подписки и коды активации (SQLite)."""
import secrets
import sqlite3
from datetime import datetime, timedelta

FOREVER = "9999-12-31T00:00:00"
# Без похожих символов (0/O, 1/I), чтобы код было легко переписать
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class DB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TEXT NOT NULL,
                sub_until TEXT,
                is_admin INTEGER NOT NULL DEFAULT 0,
                requests INTEGER NOT NULL DEFAULT 0,
                day TEXT,
                day_requests INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS codes (
                code TEXT PRIMARY KEY,
                days INTEGER NOT NULL,          -- 0 = навсегда
                created_at TEXT NOT NULL,
                used_by INTEGER,
                used_at TEXT
            );
        """)
        self.conn.commit()

    # ---------- пользователи ----------
    def touch_user(self, user_id: int, username: str | None, first_name: str | None):
        self.conn.execute(
            """INSERT INTO users (id, username, first_name, created_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET username = excluded.username, first_name = excluded.first_name""",
            (user_id, username, first_name, _now()),
        )
        self.conn.commit()

    def get_user(self, user_id: int):
        return self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    def is_admin(self, user_id: int) -> bool:
        u = self.get_user(user_id)
        return bool(u and u["is_admin"])

    def set_admin(self, user_id: int, value: bool):
        self.conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (int(value), user_id))
        self.conn.commit()

    def admin_ids(self) -> list[int]:
        return [r["id"] for r in self.conn.execute("SELECT id FROM users WHERE is_admin = 1")]

    def sub_until(self, user_id: int) -> datetime | None:
        """Дата окончания активной подписки или None, если подписки нет."""
        u = self.get_user(user_id)
        if not u or not u["sub_until"]:
            return None
        until = datetime.fromisoformat(u["sub_until"])
        return until if until > datetime.now() else None

    def revoke(self, user_id: int) -> bool:
        cur = self.conn.execute("UPDATE users SET sub_until = NULL WHERE id = ?", (user_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def count_request(self, user_id: int, daily_limit: int) -> bool:
        """Засчитывает запрос. False, если дневной лимит исчерпан."""
        today = datetime.now().date().isoformat()
        u = self.get_user(user_id)
        used = u["day_requests"] if u and u["day"] == today else 0
        if daily_limit and used >= daily_limit:
            return False
        self.conn.execute(
            "UPDATE users SET requests = requests + 1, day = ?, day_requests = ? WHERE id = ?",
            (today, used + 1, user_id),
        )
        self.conn.commit()
        return True

    def active_subscribers(self):
        return self.conn.execute(
            "SELECT * FROM users WHERE sub_until > ? ORDER BY sub_until", (_now(),)
        ).fetchall()

    def stats(self) -> dict:
        q = lambda sql, *a: self.conn.execute(sql, a).fetchone()[0]
        today = datetime.now().date().isoformat()
        return {
            "users": q("SELECT COUNT(*) FROM users"),
            "active": q("SELECT COUNT(*) FROM users WHERE sub_until > ?", _now()),
            "codes_free": q("SELECT COUNT(*) FROM codes WHERE used_by IS NULL"),
            "codes_used": q("SELECT COUNT(*) FROM codes WHERE used_by IS NOT NULL"),
            "requests_total": q("SELECT COALESCE(SUM(requests), 0) FROM users"),
            "requests_today": q("SELECT COALESCE(SUM(day_requests), 0) FROM users WHERE day = ?", today),
        }

    # ---------- коды ----------
    def create_code(self, days: int) -> str:
        while True:
            raw = "".join(secrets.choice(ALPHABET) for _ in range(12))
            code = f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"
            try:
                self.conn.execute(
                    "INSERT INTO codes (code, days, created_at) VALUES (?, ?, ?)", (code, days, _now())
                )
                self.conn.commit()
                return code
            except sqlite3.IntegrityError:
                continue  # совпадение — генерируем заново

    def redeem(self, user_id: int, code: str) -> datetime | None:
        """Активирует одноразовый код. Возвращает новую дату окончания или None."""
        code = normalize_code(code)
        row = self.conn.execute("SELECT * FROM codes WHERE code = ? AND used_by IS NULL", (code,)).fetchone()
        if not row:
            return None
        if row["days"] == 0:
            until = datetime.fromisoformat(FOREVER)
        else:
            # продлеваем от текущей даты окончания, если подписка ещё идёт
            start = self.sub_until(user_id) or datetime.now()
            until = start + timedelta(days=row["days"])
        cur = self.conn.execute(
            "UPDATE codes SET used_by = ?, used_at = ? WHERE code = ? AND used_by IS NULL", (user_id, _now(), code)
        )
        if cur.rowcount != 1:
            self.conn.rollback()
            return None
        self.conn.execute("UPDATE users SET sub_until = ? WHERE id = ?", (until.isoformat(timespec="seconds"), user_id))
        self.conn.commit()
        return until

    def delete_code(self, code: str) -> bool:
        cur = self.conn.execute("DELETE FROM codes WHERE code = ? AND used_by IS NULL", (normalize_code(code),))
        self.conn.commit()
        return cur.rowcount > 0

    def recent_codes(self, limit: int = 20):
        return self.conn.execute(
            """SELECT c.*, u.username FROM codes c LEFT JOIN users u ON u.id = c.used_by
               ORDER BY c.created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()


def normalize_code(code: str) -> str:
    raw = "".join(ch for ch in code.upper() if ch.isalnum())
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}" if len(raw) == 12 else code.strip().upper()


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
