from urllib import robotparser
from urllib.parse import urlparse

class RobotManager:
    def __init__(self):
        self.parsers = {}

    def can_fetch(self, url, user_agent='*'):
        domain = urlparse(url).scheme + "://" + urlparse(url).netloc
        if domain not in self.parsers:
            rp = robotparser.RobotFileParser()
            rp.set_url(domain + '/robots.txt')
            try:
                rp.read()
                self.parsers[domain] = rp
            except Exception as e:
                print(f"Error reading robots.txt for {domain}: {e}")
                # Assume we can fetch if robots.txt is unavailable
                return True
        
        parser = self.parsers.get(domain)
        if parser:
            return parser.can_fetch(user_agent, url)
        
        # Default to true if parser not found for any reason
        return True

# Global instance
robot_manager = RobotManager()
