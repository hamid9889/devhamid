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
    Increments visit count in Supabase 'site_analytics' table by 1 and returns current count.
    Falls back gracefully to in-memory counter if Supabase is not configured.
    """
    client = get_supabase_client()
    now_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    if client is not None:
        try:
            # 1. Fetch current count
            res = client.table("site_analytics").select("total_visits").eq("id", 1).execute()
            current_count = BASELINE_VISITS
            
            if res.data and len(res.data) > 0:
                current_count = res.data[0].get("total_visits", BASELINE_VISITS)

            new_count = current_count + 1

            # 2. Upsert incremented count
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
            res = client.table("site_analytics").select("total_visits").eq("id", 1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0].get("total_visits", _local_store["count"])
        except Exception as e:
            print(f"[WARN] Supabase fetch error: {e}")
    return _local_store["count"]
