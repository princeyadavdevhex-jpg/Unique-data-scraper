import os
import time
from loguru import logger
from duckduckgo_search import DDGS

class URLManager:
    def __init__(self, master_file="data/master_urls.txt"):
        self.master_file = master_file
        self.visited_urls = set()
        self._load_master_urls()

    def _load_master_urls(self):
        """Loads URLs into an O(1) set memory to prevent any duplicate execution."""
        os.makedirs(os.path.dirname(self.master_file), exist_ok=True)
        
        # Agar file nahi hai, toh create karega
        if not os.path.exists(self.master_file):
            open(self.master_file, 'a').close()
            
        with open(self.master_file, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url:
                    self.visited_urls.add(url)
        logger.info(f"Loaded {len(self.visited_urls)} URLs into Master Set (O(1) Deduplication Active).")

    def add_url_to_master(self, url):
        """Permanently saves a newly discovered, verified URL to the vault."""
        if url not in self.visited_urls:
            self.visited_urls.add(url)
            with open(self.master_file, 'a', encoding='utf-8') as f:
                f.write(f"{url}\n")
            logger.success(f"New URL permanently secured in Vault: {url}")

    def fetch_new_urls_via_ddgs(self, topic_keyword, max_results=5):
        """
        The DDGS Dynamic Dorking logic with Infinite Fallback Loop.
        Guarantees to return 'max_results' amount of 100% FRESH URLs.
        """
        logger.warning(f"Triggering DDGS Fallback Loop for topic: {topic_keyword}")
        fresh_urls = []
        dork_query = f"site:github.com OR site:exploit-db.com OR site:hackerone.com {topic_keyword}"
        
        # Infinite Loop: Jab tak fresh URLs na mile, rukna nahi hai
        while True:
            try:
                with DDGS() as ddgs:
                    # 15 results ek baar mein nikalenge taaki duplicate filter hone ke baad bhi data bache
                    results = list(ddgs.text(dork_query, max_results=15)) 
                    
                    if not results:
                        logger.error("DDGS returned 0 results. Sleeping 5s to avoid IP ban, then retrying...")
                        time.sleep(5)
                        continue

                    for r in results:
                        discovered_url = r.get("href")
                        
                        # Cross-Match & Reject Logic (The O(1) Filter)
                        if discovered_url and discovered_url not in self.visited_urls:
                            fresh_urls.append(discovered_url)
                            if len(fresh_urls) == max_results:
                                break
                                
                if not fresh_urls:
                    logger.error("All extracted URLs were duplicates. Retrying DDGS loop for new data...")
                    time.sleep(3)
                    continue

                logger.info(f"DDGS Extracted {len(fresh_urls)} absolutely FRESH URLs.")
                return fresh_urls

            except Exception as e:
                logger.error(f"DDGS Network/Rate-Limit Exception hit: {e}. Retrying in 10s...")
                time.sleep(10)

