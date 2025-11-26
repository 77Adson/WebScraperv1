import time
import random
from urllib.parse import urlparse
from collections import deque

class RateLimiter:
    def __init__(self, min_delay=1, max_delay=5, requests_per_minute=60, error_increase_factor=2):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.requests_per_minute = requests_per_minute
        self.error_increase_factor = error_increase_factor
        self.last_request_times = {}
        self.domain_delays = {}
        self.domain_requests = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        
        # RPM limit
        now = time.time()
        if domain not in self.domain_requests:
            self.domain_requests[domain] = deque()
        
        while len(self.domain_requests[domain]) >= self.requests_per_minute:
            if now - self.domain_requests[domain][0] > 60:
                self.domain_requests[domain].popleft()
            else:
                time.sleep(1)
                now = time.time()

        min_delay, max_delay = self.domain_delays.get(domain, (self.min_delay, self.max_delay))

        last_time = self.last_request_times.get(domain, 0)
        elapsed = time.time() - last_time
        delay = random.uniform(min_delay, max_delay)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        self.last_request_times[domain] = time.time()
        self.domain_requests[domain].append(time.time())

    def handle_error_429(self, url):
        domain = urlparse(url).netloc
        min_delay, max_delay = self.domain_delays.get(domain, (self.min_delay, self.max_delay))
        
        new_min_delay = min_delay * self.error_increase_factor
        new_max_delay = max_delay * self.error_increase_factor
        
        self.domain_delays[domain] = (new_min_delay, new_max_delay)
        print(f"Increased delay for {domain} to {new_min_delay}-{new_max_delay}s after 429 error.")

# Global instance
limiter = RateLimiter(min_delay=1, max_delay=5, requests_per_minute=15)
