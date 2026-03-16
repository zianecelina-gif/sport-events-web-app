import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DBFILENAME = 'database.sqlite'

# ─── Low-level DB helpers ────────────────────────────────────────────

def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        if all:
            res = cur.fetchall()
            return [dict(e) for e in res] if res else []
        else:
            res = cur.fetchone()
            return dict(res) if res else None


def db_insert(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid


def db_run(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        conn.execute(query, args)
        conn.commit()


def db_update(query, args=(), db_name=DBFILENAME):
    with sqlite3.connect(db_name) as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.rowcount


# ─── Database class ──────────────────────────────────────────────────

class DB:
    def __init__(self, db_path=DBFILENAME):
        self.db_path = db_path

    # ── Schema ────────────────────────────────────────────────────

    @staticmethod
    def initialize_db():
        db_run('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                family_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                bio TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        db_run('''
            CREATE TABLE IF NOT EXISTS Activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        ''')
        db_run('''
            CREATE TABLE IF NOT EXISTS Events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                date DATE NOT NULL,
                location TEXT NOT NULL,
                headcount INTEGER NOT NULL,
                activity TEXT NOT NULL,
                activity_id INTEGER NOT NULL,
                owner_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(activity_id) REFERENCES Activities(id),
                FOREIGN KEY(owner_id) REFERENCES Users(id)
            );
        ''')
        db_run('''
            CREATE TABLE IF NOT EXISTS Participations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES Users(id),
                FOREIGN KEY(event_id) REFERENCES Events(id),
                UNIQUE(user_id, event_id)
            );
        ''')

        # Seed activities if empty
        existing = db_fetch('SELECT COUNT(*) as cnt FROM Activities')
        if existing and existing['cnt'] == 0:
            activities = [
                'Football', 'Basketball', 'Cricket', 'Tennis', 'Volleyball',
                'Ping-pong', 'Badminton', 'Rugby', 'Golf', 'Natation',
                'Athlétisme', 'Cyclisme', 'Gymnastique', 'Boxe', 'MMA',
                'Baseball', 'Ski', 'Hockey sur glace', 'Hockey sur gazon',
                'Escalade', 'Musculation', 'Pétanque', 'Autre'
            ]
            for activity in activities:
                db_insert('INSERT OR IGNORE INTO Activities (name) VALUES (?)', (activity,))

    # ── Auth ──────────────────────────────────────────────────────

    @staticmethod
    def signup(username, password, first_name, family_name, age, gender, bio):
        password_hash = generate_password_hash(password)
        user_id = db_insert(
            "INSERT INTO Users (username, password_hash, first_name, family_name, age, gender, bio) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, password_hash, first_name, family_name, age, gender, bio)
        )
        return user_id

    @staticmethod
    def login(username, password):
        user = db_fetch('SELECT id, password_hash FROM Users WHERE username = ?', (username,))
        if user and check_password_hash(user['password_hash'], password):
            return user['id']
        return -1

    @staticmethod
    def verify_username_available(username):
        user = db_fetch('SELECT id FROM Users WHERE username = ?', (username,))
        return user is None

    # ── Users ─────────────────────────────────────────────────────

    @staticmethod
    def get_user_by_id(user_id):
        return db_fetch('SELECT * FROM Users WHERE id = ?', (user_id,))

    @staticmethod
    def count_users():
        result = db_fetch('SELECT COUNT(*) as cnt FROM Users')
        return result['cnt'] if result else 0

    # ── Activities ────────────────────────────────────────────────

    @staticmethod
    def list_activities():
        return db_fetch('SELECT * FROM Activities ORDER BY name', all=True)

    @staticmethod
    def get_activity_id(name):
        activity = db_fetch('SELECT id FROM Activities WHERE name = ?', (name,))
        return activity['id'] if activity else None

    # ── Events ────────────────────────────────────────────────────

    @staticmethod
    def create_event(name, description, date, location, headcount, activity, activity_id, owner_id):
        return db_insert(
            'INSERT INTO Events (name, description, date, location, headcount, activity, activity_id, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (name, description, date, location, headcount, activity, activity_id, owner_id)
        )

    @staticmethod
    def list_events():
        return db_fetch('SELECT * FROM Events ORDER BY date ASC', all=True)

    @staticmethod
    def list_events_by_activity(activity_name):
        return db_fetch('SELECT * FROM Events WHERE activity = ? ORDER BY date ASC', (activity_name,), all=True)

    @staticmethod
    def get_event_by_id(event_id):
        return db_fetch('SELECT * FROM Events WHERE id = ?', (event_id,))

    @staticmethod
    def get_event_by_name(name):
        return db_fetch('SELECT id FROM Events WHERE name = ?', (name,))

    @staticmethod
    def get_event_headcount(event_id):
        event = db_fetch('SELECT headcount FROM Events WHERE id = ?', (event_id,))
        return event['headcount'] if event else 0

    @staticmethod
    def count_events():
        result = db_fetch('SELECT COUNT(*) as cnt FROM Events')
        return result['cnt'] if result else 0

    @staticmethod
    def delete_event(event_id):
        db_run('DELETE FROM Participations WHERE event_id = ?', (event_id,))
        db_run('DELETE FROM Events WHERE id = ?', (event_id,))

    # ── Participations ────────────────────────────────────────────

    @staticmethod
    def register_user_to_event(user_id, event_id):
        try:
            db_insert('INSERT INTO Participations (user_id, event_id) VALUES (?, ?)', (user_id, event_id))
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def cancel_user_registration(user_id, event_id):
        db_run('DELETE FROM Participations WHERE user_id = ? AND event_id = ?', (user_id, event_id))

    @staticmethod
    def list_participations_by_event(event_id):
        return db_fetch('SELECT user_id FROM Participations WHERE event_id = ?', (event_id,), all=True)

    @staticmethod
    def list_participations_by_user(user_id):
        return db_fetch('SELECT event_id FROM Participations WHERE user_id = ?', (user_id,), all=True)

    @staticmethod
    def count_participations_by_event(event_id):
        result = db_fetch('SELECT COUNT(*) as cnt FROM Participations WHERE event_id = ?', (event_id,))
        return result['cnt'] if result else 0

    @staticmethod
    def count_participations_by_user(user_id):
        result = db_fetch('SELECT COUNT(*) as cnt FROM Participations WHERE user_id = ?', (user_id,))
        return result['cnt'] if result else 0

    @staticmethod
    def is_user_registered(user_id, event_id):
        registration = db_fetch('SELECT id FROM Participations WHERE user_id = ? AND event_id = ?', (user_id, event_id))
        return registration is not None

    @staticmethod
    def count_total_participations():
        result = db_fetch('SELECT COUNT(*) as cnt FROM Participations')
        return result['cnt'] if result else 0


# Initialize database on module import
DB.initialize_db()
