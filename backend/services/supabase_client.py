"""
Supabase Client Service (Python)
Integrates with Supabase Cloud Database using supabase-py.
Replaces legacy local SQLite with cloud-native PostgreSQL tables.
Includes in-memory fallback for local offline testing.
"""

import os
import time
import hashlib
from typing import Dict, Any, Optional

try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

_client: Optional[Any] = None
_is_configured = False

if create_client and SUPABASE_URL and SUPABASE_KEY and "your-supabase-project" not in SUPABASE_URL:
    try:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        _is_configured = True
        print("[INFO] Python Supabase Client initialized.")
    except Exception as e:
        print(f"[WARN] Supabase init error: {e}")
        _client = None
        _is_configured = False

# Fallback store for development/offline mode
_in_memory_store = {
    "baseline": 1482,
    "visits": 1482,
    "sessions": {},
    "messages": []
}

def is_supabase_connected() -> bool:
    return _is_configured and _client is not None

def get_visitor_count() -> int:
    """Fetch current visitor count from Supabase or fallback store."""
    if is_supabase_connected():
        try:
            res = _client.table("site_analytics").select("total_visits").eq("id", 1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0].get("total_visits", _in_memory_store["visits"])
        except Exception as e:
            print(f"⚠️ Supabase fetch visitor count error: {e}")
    return _in_memory_store["visits"]

def record_visit(visitor_id: Optional[str], ip_address: Optional[str], user_agent: Optional[str]) -> Dict[str, Any]:
    """Record unique visit in Supabase with session deduplication."""
    date_bucket = time.strftime('%Y-%m-%d', time.gmtime())
    iso_now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    ip_hash = hashlib.sha256((ip_address or '127.0.0.1').encode('utf-8')).hexdigest()[:16]
    client_hash = hashlib.sha256(visitor_id.encode('utf-8')).hexdigest()[:24] if visitor_id else ip_hash

    if is_supabase_connected():
        try:
            # Check existing session
            res = _client.table("visitor_sessions").select("id").match({
                "visitor_hash": client_hash,
                "date_bucket": date_bucket
            }).execute()

            if res.data and len(res.data) > 0:
                return {"count": get_visitor_count(), "isNewVisit": False}

            # Insert session
            _client.table("visitor_sessions").insert({
                "visitor_hash": client_hash,
                "ip_hash": ip_hash,
                "user_agent": (user_agent or '')[:255],
                "date_bucket": date_bucket,
                "visited_at": iso_now
            }).execute()

            # Increment count
            curr = get_visitor_count()
            new_count = curr + 1
            _client.table("site_analytics").upsert({
                "id": 1,
                "total_visits": new_count,
                "last_visit_at": iso_now
            }).execute()

            return {"count": new_count, "isNewVisit": True}
        except Exception as e:
            print(f"⚠️ Supabase record visit error: {e}")

    # Fallback in-memory
    session_key = f"{client_hash}_{date_bucket}"
    if session_key in _in_memory_store["sessions"]:
        return {"count": _in_memory_store["visits"], "isNewVisit": False}

    _in_memory_store["sessions"][session_key] = iso_now
    _in_memory_store["visits"] += 1
    return {"count": _in_memory_store["visits"], "isNewVisit": True}

def save_contact_message(name: str, email: str, message: str) -> bool:
    """Save contact message in Supabase."""
    record = {
        "name": name,
        "email": email,
        "message": message,
        "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "status": "delivered"
    }

    if is_supabase_connected():
        try:
            _client.table("contact_messages").insert(record).execute()
            return True
        except Exception as e:
            print(f"⚠️ Supabase save contact error: {e}")

    _in_memory_store["messages"].append(record)
    return True
