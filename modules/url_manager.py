import os
import time
from loguru import logger
from duckduckgo_search import DDGS

class URLManager:
    def __init__(self, master_file="data/master_urls.txt", pending_file="data/pending_targets.txt"):
        self.master_file = master_file
        self.pending_file = pending_file
        self.visited_urls = set()
        self._init_files()

    def _init_files(self):
        """Ensures both vault and pending files exist, and loads history."""
        os.makedirs(os.path.dirname(self.master_file), exist_ok=True)
        for filepath in [self.master_file, self.pending_file]:
            if not os.path.exists(filepath):
                open(filepath, 'a').close()
                
        with open(self.master_file, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url: self.visited_urls.add(url)
        logger.info(f"Loaded {len(self.visited_urls)} URLs into Blacklist Vault.")

    def add_url_to_master(self, url):
        """Saves a scraped URL to the vault blacklist."""
        if url not in self.visited_urls:
            self.visited_urls.add(url)
            with open(self.master_file, 'a', encoding='utf-8') as f:
                f.write(f"{url}\n")

    def get_pending_urls(self, batch_size=5):
        """Reads manual targets, removes them from pending file, and returns them."""
        targets = []
        remaining = []
        with open(self.pending_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            url = line.strip()
            if not url: continue
            
            if url not in self.visited_urls and len(targets) < batch_size:
                targets.append(url)
            else:
                remaining.append(url)
                
        with open(self.pending_file, 'w', encoding='utf-8') as f:
            for r in remaining: f.write(f"{r}\n")
            
        return targets

    def fetch_fallback_urls(self, original_url, max_results=5):
        """ONLY triggers if a manual URL fails. Extracts keywords from the dead URL to find replacements."""
        logger.warning(f"🚑 Scrape Failed! Triggering DDGS Fallback for dead link.")
        
        # URL se basic keywords nikalna DDGS search ke liye
        topic_keyword = original_url.split("/")[-1].replace("-", " ").replace(".html", "")
        dork_query = f"site:github.com OR site:exploit-db.com OR site:hackerone.com {topic_keyword} vulnerability POC"
        
        fresh_urls = []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(dork_query, max_results=10)) 
                for r in results:
                    discovered_url = r.get("href")
                    if discovered_url and discovered_url not in self.visited_urls:
                        fresh_urls.append(discovered_url)
                        if len(fresh_urls) == max_results: break
            logger.info(f"DDGS Fallback fetched {len(fresh_urls)} alternative URLs.")
            return fresh_urls
        except Exception as e:
            logger.error(f"DDGS Exception: {e}")
            return []
            
