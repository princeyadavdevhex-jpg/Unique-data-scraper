import asyncio
import os
import json
import uuid
from datetime import datetime
from urllib.parse import urlparse
from loguru import logger

# Importing the isolated core modules
from modules.url_manager import URLManager
from modules.hydra_scraper import HydraScraper
from modules.llm_validator import LLMValidator

class NexusMasterPipeline:
    def __init__(self):
        logger.info("Initializing Nexus Time-Series Data Pipeline...")
        self.url_manager = URLManager()
        self.scraper = HydraScraper()
        self.validator = LLMValidator()
        
        # FIX 3: Update these seed topics with your actual target search queries
        self.seed_topics = [
            "zero day exploit POC C++",
            "kernel privilege escalation vulnerability",
            "advanced persistent threat architecture bypass"
        ]
        
        # Create a unique Run ID for this specific execution batch
        self.run_id = f"RUN_{datetime.now().strftime('%H-%M-%S')}_{str(uuid.uuid4())[:4]}"

    def _create_folder_structure(self, url: str) -> str:
        """Creates deeply nested folders: Year-Month / Day / Run_ID / domain.com"""
        now = datetime.now()
        year_month = now.strftime("%Y-%m")
        day = now.strftime("%d")
        
        # Extract purely the domain name
        domain = urlparse(url).netloc.replace("www.", "")
        if not domain: domain = "unknown_domain"

        folder_path = os.path.join("data", "bronze_vault", year_month, day, self.run_id, domain)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    async def save_raw_data(self, folder_path: str, raw_text: str):
        """Saves the completely raw, unedited extracted text FIRST."""
        filepath = os.path.join(folder_path, "00_RAW_DATA.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(raw_text)
        logger.debug(f"Raw Data locked in: {filepath}")

    async def save_purified_split_data(self, folder_path: str, data: dict):
        """Saves Title, Logic, Code, and Debate Questions into separate files."""
        # 1. Save Title
        with open(os.path.join(folder_path, "01_TITLE.txt"), "w", encoding="utf-8") as f:
            f.write(data.get("topic_title", "Unknown Title"))
            
        # 2. Save Core Logic
        with open(os.path.join(folder_path, "02_CORE_LOGIC.md"), "w", encoding="utf-8") as f:
            f.write(data.get("core_logic_summary", ""))
            
        # 3. Save Extracted Code Snippets
        with open(os.path.join(folder_path, "03_EXTRACTED_CODE.md"), "w", encoding="utf-8") as f:
            codes = data.get("extracted_code_snippets", [])
            for i, code in enumerate(codes):
                f.write(f"### Code Block {i+1}\n```\n{code}\n
```\n\n")
                
        # 4. Save Debate Seeds (Questions)
        with open(os.path.join(folder_path, "04_DEBATE_QUESTIONS.json"), "w", encoding="utf-8") as f:
            json.dump(data.get("debate_questions", []), f, indent=4)
            
        logger.success(f"📦 Split Purified Data Saved inside: {folder_path}")

    async def run_infinite_loop(self):
        """The Master Orchestrator: 24/7 Execution Loop"""
        logger.info(f"Nexus Data Engine: INFINITE LOOP ENGAGED 🚀. Run ID: {self.run_id}")
        
        current_topic_index = 0
        
        while True:
            target_urls = []
            
            # Step 1: Check URLs in Master Set or trigger DDGS
            if len(self.url_manager.visited_urls) == 0:
                topic = self.seed_topics[current_topic_index % len(self.seed_topics)]
                logger.warning("Vault empty. Triggering initial DDGS Seed fetch...")
                target_urls = self.url_manager.fetch_new_urls_via_ddgs(topic, max_results=5)
            else:
                topic = self.seed_topics[current_topic_index % len(self.seed_topics)]
                target_urls = self.url_manager.fetch_new_urls_via_ddgs(topic, max_results=2)
                
            current_topic_index += 1

            # Step 2: Execute the Pipeline for each fresh URL
            for url in target_urls:
                logger.info(f"--- Initiating Attack Vector on: {url} ---")
                
                # A. Extract Pure Text (The 17-Layer Matrix)
                pure_text = await self.scraper.scrape(url)
                
                if not pure_text:
                    logger.error(f"Scraping completely failed for {url}. Moving to next.")
                    continue
                
                # B. Create the exact nested folder structure for this URL
                folder_path = self._create_folder_structure(url)
                
                # C. Save Raw Data FIRST (Before LLM touches it)
                await self.save_raw_data(folder_path, pure_text)
                
                # D. Validate & Generate Debate Seeds (The HF 32B Enforcer)
                final_package = await self.validator.validate_and_generate(pure_text, url)
                
                if final_package and final_package["extracted_data"]["is_valid_data"]:
                    # E. Save the split purified data
                    await self.save_purified_split_data(folder_path, final_package["extracted_data"])
                    # F. Add to Master Set so it's NEVER scraped again
                    self.url_manager.add_url_to_master(url)
                else:
                    logger.warning(f"Data from {url} rejected by LLM. Raw data kept, moving on.")
                    
                # Small stealth delay
                await asyncio.sleep(2)
                
            logger.info("Batch cycle complete. Restarting loop...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(NexusMasterPipeline().run_infinite_loop())
    except KeyboardInterrupt:
        logger.info("Nexus Master Pipeline gracefully shut down by Admin.")
    except Exception as e:
        logger.critical(f"FATAL SYSTEM ERROR: {e}")
        
