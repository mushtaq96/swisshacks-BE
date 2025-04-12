import json
from pathlib import Path
from typing import Dict, List

DB_FILE = Path("ticket_db.json")

def init_db():
    """Initialize empty DB if not exists"""
    if not DB_FILE.exists():
        with open(DB_FILE, "w") as f:
            json.dump({"events": [], "orders": [], "tickets": []}, f)

def read_db() -> Dict:
    """Read entire DB"""
    with open(DB_FILE) as f:
        return json.load(f)

def write_db(data: Dict):
    """Overwrite entire DB"""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# CRUD Helpers
def add_event(event: Dict):
    db = read_db()
    db["events"].append(event)
    write_db(db)

def find_event(event_id: str) -> Dict:
    db = read_db()
    return next((e for e in db["events"] if e["id"] == event_id), None)

def update_event(event_id: str, updates: Dict):
    db = read_db()
    for e in db["events"]:
        if e["id"] == event_id:
            e.update(updates)
    write_db(db)