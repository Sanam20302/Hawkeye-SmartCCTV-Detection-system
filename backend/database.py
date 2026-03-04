import sqlite3
import json
import os
import datetime

DB_PATH = "faces.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Table for trusted faces
    # embedding will be stored as a JSON string list of floats
    c.execute('''CREATE TABLE IF NOT EXISTS trusted_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # Table for missing/wanted faces
    c.execute('''CREATE TABLE IF NOT EXISTS missing_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    image_path TEXT,
                    category TEXT NOT NULL DEFAULT 'Missing',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # Table for untrusted face captures
    c.execute('''CREATE TABLE IF NOT EXISTS untrusted_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    conn.commit()
    conn.close()

def add_trusted_face(name, embedding, image_path=None):
    """
    embedding: list of floats
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    embedding_json = json.dumps(embedding)
    c.execute("INSERT INTO trusted_faces (name, embedding, image_path) VALUES (?, ?, ?)", (name, embedding_json, image_path))
    conn.commit()
    face_id = c.lastrowid
    conn.close()
    return face_id

def get_trusted_faces():
    """
    Returns a list of dicts: {'id': int, 'name': str, 'embedding': list, 'image_path': str}
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, embedding, image_path FROM trusted_faces")
    rows = c.fetchall()
    conn.close()
    
    faces = []
    for r in rows:
        faces.append({
            "id": r[0],
            "name": r[1],
            "embedding": json.loads(r[2]),
            "image_path": r[3]
        })
    return faces

def delete_trusted_face(face_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM trusted_faces WHERE id = ?", (face_id,))
    conn.commit()
    conn.close()

def add_missing_face(name, embedding, image_path=None, category="Missing"):
    """
    embedding: list of floats
    category: "Missing" or "Wanted"
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    embedding_json = json.dumps(embedding)
    
    # Check if category column exists, if not, add it (simple migration)
    try:
        c.execute("INSERT INTO missing_faces (name, embedding, image_path, category) VALUES (?, ?, ?, ?)", (name, embedding_json, image_path, category))
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE missing_faces ADD COLUMN category TEXT NOT NULL DEFAULT 'Missing'")
        c.execute("INSERT INTO missing_faces (name, embedding, image_path, category) VALUES (?, ?, ?, ?)", (name, embedding_json, image_path, category))
        
    conn.commit()
    face_id = c.lastrowid
    conn.close()
    return face_id

def get_missing_faces():
    """
    Returns a list of dicts: {'id': int, 'name': str, 'embedding': list, 'image_path': str, 'category': str}
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Use pragma to check if category exists to handle legacy db
    c.execute("PRAGMA table_info(missing_faces)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'category' not in columns:
        c.execute("ALTER TABLE missing_faces ADD COLUMN category TEXT NOT NULL DEFAULT 'Missing'")
        conn.commit()
    
    c.execute("SELECT id, name, embedding, image_path, category FROM missing_faces")
    rows = c.fetchall()
    conn.close()
    
    faces = []
    for r in rows:
        faces.append({
            "id": r[0],
            "name": r[1],
            "embedding": json.loads(r[2]),
            "image_path": r[3],
            "category": r[4]
        })
    return faces

def delete_missing_face(face_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM missing_faces WHERE id = ?", (face_id,))
    conn.commit()
    conn.close()

def log_untrusted_face(image_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO untrusted_faces (image_path) VALUES (?)", (image_path,))
    conn.commit()
    conn.close()

def get_untrusted_faces():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, image_path, timestamp FROM untrusted_faces ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    faces = []
    for r in rows:
        faces.append({
            "id": r[0],
            "image_path": r[1],
            "timestamp": r[2]
        })
    return faces
