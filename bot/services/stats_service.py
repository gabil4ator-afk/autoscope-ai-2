
import sqlite3
from pathlib import Path

DB = Path("bot_stats.db")

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS stats(
        user_id INTEGER PRIMARY KEY,
        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        text_analyses INTEGER DEFAULT 0,
        image_analyses INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

def register_user(user_id:int):
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    cur.execute("INSERT OR IGNORE INTO stats(user_id) VALUES(?)",(user_id,))
    conn.commit()
    conn.close()

def inc_text(user_id:int):
    register_user(user_id)
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    cur.execute("UPDATE stats SET text_analyses=text_analyses+1 WHERE user_id=?",(user_id,))
    conn.commit()
    conn.close()

def inc_image(user_id:int):
    register_user(user_id)
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    cur.execute("UPDATE stats SET image_analyses=image_analyses+1 WHERE user_id=?",(user_id,))
    conn.commit()
    conn.close()

def get_stats():
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    users=cur.execute("SELECT COUNT(*) FROM stats").fetchone()[0]
    texts=cur.execute("SELECT COALESCE(SUM(text_analyses),0) FROM stats").fetchone()[0]
    imgs=cur.execute("SELECT COALESCE(SUM(image_analyses),0) FROM stats").fetchone()[0]
    conn.close()
    return users,texts,imgs
