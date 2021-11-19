import json
from unittest import TestCase
from lib.utils.cache import Cache


class TestCache(TestCase):
    c = Cache()

    def test_flush(self):
        self.c.flushdb()

    def test__setitem__getitem__(self):
        self.c["foo"] = "bar"
        assert "bar" == self.c["foo"]
        self.c['complex_dict'] = json.dumps({'bobo': 'baba', 'barbarella': 68})
        print("complex dict = %r" % json.loads(self.c['complex_dict']))

    def test__contains__(self):
        self.c["foo"] = "bar"
        self.c['foo44'] = "xyz"
        assert "foo" in self.c
        assert "foo44" in self.c

    def test__len__(self):
        print("number of entries in the cache dict: %d BEFORE flushing" % len(self.c))
        self.c.flushdb()
        self.c["foo"] = "bar"
        self.c['foo44'] = "xyz"
        self.c["xyz"] = 123
        assert len(self.c) == 3
        self.c.flushdb()
