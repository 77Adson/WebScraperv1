import time
from urllib.parse import urlparse

class RateLimiter:
    def __init__(self, delay=5):
        self.delay = delay
        self.last_request_times = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_time = self.last_request_times.get(domain, 0)
        elapsed = time.time() - last_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_times[domain] = time.time()

# Global instance
limiter = RateLimiter(delay=2)
