"""
Supabase Visitor Counter Service
Connects to Supabase Cloud Database using supabase-py.
Manages persistent visitor analytics in the 'site_analytics' table.
Increments count on each request and returns the current total.
Provides graceful in-memory fallback for local offline testing.
"""

import os
import time
from typing import Dict, Any, Optional

try:
    from supabase import create_client, Client  # type: ignore
except ImportError:
    create_client = None
    Client = None

# Baseline visit counter default
BASELINE_VISITS = 1482

# In-memory store fallback
_local_store = {
    "count": BASELINE_VISITS,
    "last_updated": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
}

def get_supabase_client() -> Optional[Any]:
    """Initialize and return Supabase client using SUPABASE_URL and SUPABASE_KEY."""
    url = (os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL") or "").strip().strip('"\'')
    key = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip().strip('"\'')

    if not url or not key or "your-supabase-project" in url:
        return None

    if create_client is None:
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        print(f"[WARN] Failed to connect to Supabase: {e}")
        return None

def increment_and_get_visits() -> int:
    """
    Increments visit count in Supabase 'visits' or 'site_analytics' table and returns count.
    Falls back gracefully to in-memory counter if Supabase is not configured.
    """
    client = get_supabase_client()
    now_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    if client is not None:
        # 1. Try modern 'visits' table
        try:
            res = client.table("visits").select("*").order("id", desc=False).limit(1).execute()
            if res.data and len(res.data) > 0:
                current = res.data[0]
                new_count = current.get("count", BASELINE_VISITS) + 1
                client.table("visits").update({
                    "count": new_count,
                    "last_updated": now_iso
                }).eq("id", current["id"]).execute()
                _local_store["count"] = new_count
                return new_count
            else:
                client.table("visits").insert({
                    "id": 1,
                    "count": BASELINE_VISITS + 1,
                    "last_updated": now_iso
                }).execute()
                _local_store["count"] = BASELINE_VISITS + 1
                return _local_store["count"]
        except Exception:
            pass

        # 2. Try legacy 'site_analytics' table
        try:
            res = client.table("site_analytics").select("total_visits").eq("id", 1).execute()
            current_count = BASELINE_VISITS
            if res.data and len(res.data) > 0:
                current_count = res.data[0].get("total_visits", BASELINE_VISITS)
            new_count = current_count + 1
            client.table("site_analytics").upsert({
                "id": 1,
                "total_visits": new_count,
                "last_visit_at": now_iso
            }).execute()
            _local_store["count"] = new_count
            return new_count
        except Exception as e:
            print(f"[WARN] Supabase visitor increment error, using fallback: {e}")

    # In-memory fallback
    _local_store["count"] += 1
    _local_store["last_updated"] = now_iso
    return _local_store["count"]

def get_current_visits() -> int:
    """Returns current count without incrementing."""
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("visits").select("*").order("id", desc=False).limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0].get("count", _local_store["count"])
        except Exception:
            pass
        try:
            res = client.table("site_analytics").select("total_visits").eq("id", 1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0].get("total_visits", _local_store["count"])
        except Exception as e:
            print(f"[WARN] Supabase fetch error: {e}")
    return _local_store["count"]

def get_blog_posts() -> list:
    """Fetch blog posts from Supabase 'blog_posts' table or local fallback."""
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("blog_posts").select("*").execute()
            if res.data and len(res.data) > 0:
                return res.data
        except Exception as e:
            print(f"[WARN] Supabase blog_posts fetch: {e}")

    # Fallback to local posts.json
    try:
        import json
        from pathlib import Path
        for path in [
            Path(__file__).parent.parent.parent / "frontend" / "data" / "posts.json",
            Path(__file__).parent.parent / "frontend" / "data" / "posts.json"
        ]:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
    except Exception:
        pass
    return []

def get_contacts() -> list:
    """Fetch stored contact form submissions from Supabase 'contacts' table."""
    client = get_supabase_client()
    if client is not None:
        try:
            res = client.table("contacts").select("*").execute()
            if res.data:
                return res.data
        except Exception as e:
            print(f"[WARN] Supabase contacts fetch: {e}")
    return []

def save_contact(name: str, email: str, message: str) -> bool:
    """Insert contact entry into Supabase 'contacts' table."""
    client = get_supabase_client()
    if client is not None:
        try:
            client.table("contacts").insert({
                "name": name,
                "email": email,
                "message": message,
                "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }).execute()
            return True
        except Exception as e:
            print(f"[WARN] Supabase contacts insert: {e}")
    return False
