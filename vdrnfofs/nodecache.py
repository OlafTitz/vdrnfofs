import time

class NodeCache:
    class CacheEntry:
        def __init__(self, node):
            self.time = time.time()
            self.node = node

    def __init__(self):
        self.cache = {}
        self.last_clean = time.time()

    def get(self, path, creator):
        #
        # !!! It might be nicer to have a thread for cleaning the cache, but
        # with the Fuse option multithreaded = False, threading seems to
        # be totally impossible. Somehow Fuse blocks ALL threads.
        #
        now = time.time()
        if (now - self.last_clean) > 15:
            self.cache = dict((k, v) for k, v in self.cache.items() if (now - v.time) <= 10)
            self.last_clean = now

        cache_entry = self.cache.get(path, None)
        if not cache_entry or (now - cache_entry.time) > 10:
            cache_entry = NodeCache.CacheEntry(creator(path))
            self.cache[path] = cache_entry
        return cache_entry.node
