#!/usr/bin/env python
""" Cache: implement a simple redis based cache with the semantics of dicts.
Deals with the encoding on redis automatically.

USAGE example:
    from cache import Cache

    c = Cache()
    c["foo"] = "bar"
    print(c['foo'])
    > "bar"

Also see the unit test in tests/test_cache.py please.

"""

import time
import redis
from lib.config import Config, GLOBAL_CONFIG_PATH

c = Config()
config = c.load(GLOBAL_CONFIG_PATH)  # this is a bit redundant FIXME
TTL = config['redis'].get('cache_ttl', 24 * 3600)  # 1 day default


class Cache:
    """A simple cache of key/value pairs (both strings) via redis."""

    def __init__(self):
        """Construct it."""

        _c = Config()
        self.config = _c.load(GLOBAL_CONFIG_PATH)

        self.host = self.config['redis'].get('host', "localhost")
        self.port = int(self.config['redis'].get('port', 6379))
        self.password = self.config['redis'].get('password', None)
        self.db = int(self.config['redis'].get('db', 2))
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=self.db, password=self.password,
                                   decode_responses=True)
        if not self.r.exists("cache_metadata"):
            self.r.hset(b"cache_metadata", b"created_at", time.time())

    def __contains__(self, key: str) -> bool:
        """Check for existence of the key in the redis cache."""

        return self.r.exists(key)

    def __getitem__(self, key: str) -> str:
        """Get key from redis."""

        return self.r.get(key)

    def __setitem__(self, key: str, value: str, ttl: int = TTL) -> int:
        """Store the key in redis."""

        rv = self.r.set(key, value)
        if ttl:
            self.r.expire(key, ttl)
        return rv

    def __len__(self) -> int:
        """Return how many keys are stored in redis."""

        numkeys = 0
        info = self.r.info("keyspace")
        print("type(info) = %s. info=%s" % (type(info), info))
        db = "db%d" % self.db
        if db in info:
            numkeys = info[db]["keys"]
        return numkeys

    def flushdb(self):
        """Flush the current redis DB. WARNING: this flushes it! No confirmation asked."""
        return self.r.flushdb()


# XXX FIXME: this global cache var needs to die XXX
cache = Cache()
