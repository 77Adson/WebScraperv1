from urllib import robotparser
from urllib.parse import urlparse
import logging

# Konfiguracja podstawowego loggera
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
                logging.warning(f"Nie można odczytać pliku robots.txt dla domeny {domain}: {e}. Przyjmuję, że można pobierać.")
                # Zapisujemy None, aby nie próbować ponownie dla tej samej domeny
                self.parsers[domain] = None
                return True
        
        parser = self.parsers.get(domain)
        if parser:
            allowed = parser.can_fetch(user_agent, url)
            if not allowed:
                logging.info(f"URL odrzucony przez robots.txt: {url} (User-agent: {user_agent})")
            return allowed
        
        # Domyślnie zezwalaj, jeśli parser nie został znaleziony (np. błąd odczytu)
        return True

# Global instance
robot_manager = RobotManager()
