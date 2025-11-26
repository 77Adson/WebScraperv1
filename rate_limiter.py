import time
import random
from urllib.parse import urlparse

class RateLimiter:
    def __init__(self, min_delay=1, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_times = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_time = self.last_request_times.get(domain, 0)
        elapsed = time.time() - last_time
        delay = random.uniform(self.min_delay, self.max_delay)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request_times[domain] = time.time()

# Global instance
limiter = RateLimiter(min_delay=1, max_delay=5)
