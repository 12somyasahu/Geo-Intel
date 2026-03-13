"""
env_loader.py — Central environment loader + API key pooling

Handles:
- Local Windows dev (.env file with UTF-8 BOM)
- Render.com production (env vars already set in environment)
- Key pooling for Groq and Tavily (multiple keys, round-robin with 429 fallback)
"""

import os
import threading
from pathlib import Path

_loaded = False
_lock   = threading.Lock()

def load_env():
    """Load .env file if running locally. Safe to call multiple times."""
    global _loaded
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        # On Render, env vars are already set — skip file loading
        if os.getenv("RENDER"):
            _loaded = True
            return
        # Local dev — find .env relative to this file
        env_path = Path(__file__).parent.parent / ".env"
        if not env_path.exists():
            # Fallback to hardcoded Windows path
            env_path = Path(r'D:\downloads\Geo-Intel\backend\.env')
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        k, v = k.strip(), v.strip()
                        if k and v and not os.environ.get(k):
                            os.environ[k] = v
        _loaded = True


# ── Key Pooling ────────────────────────────────────────────────────────────────

class KeyPool:
    """Round-robin API key pool with 429 fallback."""
    def __init__(self, keys: list[str]):
        self._keys   = keys
        self._index  = 0
        self._lock   = threading.Lock()

    def get(self) -> str | None:
        with self._lock:
            available = [k for k in self._keys if k]
            if not available:
                return None
            key = available[self._index % len(available)]
            self._index += 1
            return key

    def next(self) -> str | None:
        """Force rotate to next key (call on 429)."""
        with self._lock:
            self._index += 1
            available = [k for k in self._keys if k]
            if not available:
                return None
            return available[self._index % len(available)]


def _collect_keys(prefix: str) -> list[str]:
    """Collect all env vars matching PREFIX, PREFIX_1, PREFIX_2 etc."""
    load_env()
    keys = []
    # Single key
    if os.getenv(prefix):
        keys.append(os.getenv(prefix))
    # Numbered keys
    for i in range(1, 10):
        k = os.getenv(f"{prefix}_{i}")
        if k:
            keys.append(k)
    return list(dict.fromkeys(keys))  # deduplicate, preserve order


# Singletons — initialized on first use
_groq_pool:   KeyPool | None = None
_tavily_pool: KeyPool | None = None

def get_groq_pool() -> KeyPool:
    global _groq_pool
    if _groq_pool is None:
        keys = _collect_keys("GROQ_API_KEY")
        if not keys:
            raise RuntimeError("No GROQ_API_KEY found in environment")
        _groq_pool = KeyPool(keys)
        print(f"[env_loader] Groq pool: {len(keys)} key(s)")
    return _groq_pool

def get_tavily_pool() -> KeyPool:
    global _tavily_pool
    if _tavily_pool is None:
        keys = _collect_keys("TAVILY_API_KEY")
        if not keys:
            raise RuntimeError("No TAVILY_API_KEY found in environment")
        _tavily_pool = KeyPool(keys)
        print(f"[env_loader] Tavily pool: {len(keys)} key(s)")
    return _tavily_pool


def get_groq_client():
    """Get a Groq client using the next available key."""
    from groq import Groq
    key = get_groq_pool().get()
    return Groq(api_key=key)

def get_tavily_client():
    """Get a Tavily client using the next available key."""
    from tavily import TavilyClient
    key = get_tavily_pool().get()
    return TavilyClient(api_key=key)