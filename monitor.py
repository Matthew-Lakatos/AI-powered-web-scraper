import time
from dataclasses import dataclass, field

@dataclass
class Monitor:
    scraped: int = 0
    cached: int = 0
    scrape_times: list = field(default_factory=list)
    nlp_times: list = field(default_factory=list)

    def record_scrape(self, duration: float):
        self.scraped += 1
        self.scrape_times.append(duration)

    def record_cached(self):
        self.cached += 1

    def record_nlp(self, duration: float):
        self.nlp_times.append(duration)

    def summary(self):
        return {
            "scraped": self.scraped,
            "cached": self.cached,
            "avg_scrape_time": sum(self.scrape_times) / len(self.scrape_times) if self.scrape_times else 0,
            "avg_nlp_time": sum(self.nlp_times) / len(self.nlp_times) if self.nlp_times else 0,
        }
