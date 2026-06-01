import asyncio
import os
import json
import uuid
from loguru import logger

# Importing the isolated core modules
from modules.url_manager import URLManager
from modules.hydra_scraper import HydraScraper
from modules.llm_validator import LLMValidator

# Setup Vault Paths
BRONZE_VAULT_DIR = "data/bronze_vault"

class NexusMasterPipeline:
    def __init__(self):
        logger.info("Initializing Nexus Master Pipeline...")
        
        # Ensure Vault Exists
        os.makedirs(BRONZE_VAULT_DIR, exist_ok=True)
        
        # Initialize Core Modules
        self.url_manager = URLManager()
        self.scraper = HydraScraper()
        self.validator = LLMValidator()
        
        # Seed topics for DDGS fallback if the master URL list is completely empty
        self.seed_topics = [
            "zero day exploit POC C++",
            "kernel privilege escalation vulnerability",
            "advanced persistent threat architecture bypass"
        ]

    async def save_to_bronze_vault(self, data_package: dict):
        """Saves the perfectly validated JSON package into the Bronze Vault"""
        file_id = str(uuid.uuid4())[:8]
        filepath = os.path.join(BRONZE_VAULT_DIR, f"validated_logic_{file_id}.json")
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_package, f, indent=4)
        
        logger.success(f"📦 Package Secured in Bronze Vault: {filepath}")

    async def run_infinite_loop(self):
        """The Master Orchestrator: 24/7 Execution Loop"""
        logger.info("Nexus Data Engine: INFINITE LOOP ENGAGED 🚀")
        
        current_topic_index = 0
        
        while True:
            target_urls = []
            
            # Step 1: Check if we have URLs in the Master Set. If not, trigger DDGS.
            # In a real run, your master_urls.txt will already have 2000+ links.
            if len(self.url_manager.visited_urls) == 0:
                topic = self.seed_topics[current_topic_index % len(self.seed_topics)]
                logger.warning("Vault empty. Triggering initial DDGS Seed fetch...")
                target_urls = self.url_manager.fetch_new_urls_via_ddgs(topic, max_results=5)
                current_topic_index += 1
            else:
                # For this automated loop, if we exhaust our manual list, we use DDGS to keep it alive
                topic = self.seed_topics[current_topic_index % len(self.seed_topics)]
                target_urls = self.url_manager.fetch_new_urls_via_ddgs(topic, max_results=2)
                current_topic_index += 1

            # Step 2: Execute the Pipeline for each fresh URL
            for url in target_urls:
                logger.info(f"--- Initiating Attack Vector on: {url} ---")
                
                # A. Extract Pure Text (The 17-Layer Matrix)
                pure_text = await self.scraper.scrape(url)
                
                if not pure_text:
                    logger.error(f"Scraping completely failed for {url}. Moving to next target.")
                    continue
                
                # B. Validate & Generate Debate Seeds (The HF 32B Enforcer)
                final_package = await self.validator.validate_and_generate(pure_text, url)
                
                if final_package:
                    # C. Save the Data
                    await self.save_to_bronze_vault(final_package)
                    
                    # D. Add to Master Set so it's NEVER scraped again
                    self.url_manager.add_url_to_master(url)
                else:
                    logger.warning(f"Data from {url} was JUNK. Discarded.")
                    
                # Small stealth delay to prevent aggressive network blocking
                await asyncio.sleep(2)
                
            logger.info("Batch cycle complete. Restarting loop...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    # Start the async execution of the Master Pipeline
    pipeline = NexusMasterPipeline()
    try:
        asyncio.run(pipeline.run_infinite_loop())
    except KeyboardInterrupt:
        logger.info("Nexus Master Pipeline gracefully shut down by Admin.")
    except Exception as e:
        logger.critical(f"FATAL SYSTEM ERROR: {e}")
  
