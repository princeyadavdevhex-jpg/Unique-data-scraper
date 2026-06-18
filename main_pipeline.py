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
        
        # ORIGINAL LOGIC KEPT: Seed topics for DDGS fallback 
        self.seed_topics = [
            "zero day exploit POC C++",
            "kernel privilege escalation vulnerability",
            "advanced persistent threat architecture bypass"
        ]
        
        # NEW LOGIC ADDED: Run ID for the new folder structure
        self.run_id = f"RUN_{datetime.now().strftime('%H-%M-%S')}_{str(uuid.uuid4())[:4]}"

    # --- NEW FOLDER & SPLIT STORAGE LOGIC ADDED HERE ---
    def _create_folder_structure(self, url: str) -> str:
        """Creates deeply nested folders: Year-Month / Day / Run_ID / domain.com"""
        now = datetime.now()
        domain = urlparse(url).netloc.replace("www.", "")
        if not domain: domain = "unknown_domain"

        folder_path = os.path.join(BRONZE_VAULT_DIR, now.strftime("%Y-%m"), now.strftime("%d"), self.run_id, domain)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    async def save_raw_data(self, folder_path: str, raw_text: str):
        filepath = os.path.join(folder_path, "00_RAW_DATA.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(raw_text)
        logger.debug(f"Raw Data locked in: {filepath}")

    async def save_purified_split_data(self, folder_path: str, data: dict):
        with open(os.path.join(folder_path, "01_TITLE.txt"), "w", encoding="utf-8") as f:
            f.write(data.get("topic_title", "Unknown Title"))
        with open(os.path.join(folder_path, "02_CORE_LOGIC.md"), "w", encoding="utf-8") as f:
            f.write(data.get("core_logic_summary", ""))
        with open(os.path.join(folder_path, "03_EXTRACTED_CODE.md"), "w", encoding="utf-8") as f:
            for i, code in enumerate(data.get("extracted_code_snippets", [])):
                f.write(f"### Code Block {i+1}\n```\n{code}\n```\n\n")
        with open(os.path.join(folder_path, "04_DEBATE_QUESTIONS.json"), "w", encoding="utf-8") as f:
            json.dump(data.get("debate_questions", []), f, indent=4)
        logger.success(f"📦 Split Purified Data Saved inside: {folder_path}")
    # ---------------------------------------------------

    async def run_infinite_loop(self):
        """The Master Orchestrator: Execution Loop with Graceful Shutdown"""
        logger.info(f"Nexus Data Engine: PIPELINE ENGAGED 🚀. Run ID: {self.run_id}")
        
        current_topic_index = 0
        
        while True:
            target_urls = []
            
            # --- NEW SMART LOGIC (Overrides infinite loop to prevent bans) ---
            target_urls = self.url_manager.get_pending_urls(batch_size=5)
            
            if not target_urls:
                logger.success("🏁 All manual URLs processed! Pending file is empty.")
                logger.info("Initiating Graceful Container Shutdown to prevent API bans.")
                break # Container automatically ruk jayega, aage Github Action ka push chalega
            # ----------------------------------------------------------------

            # Step 2: Execute the Pipeline for each fresh URL
            for url in target_urls:
                logger.info(f"--- Initiating Attack Vector on: {url} ---")
                
                # A. Extract Pure Text (The 17-Layer Matrix)
                pure_text = await self.scraper.scrape(url)
                
                # B. Validation & Saving (If successful)
                success = False
                if pure_text:
                    folder_path = self._create_folder_structure(url)
                    await self.save_raw_data(folder_path, pure_text)
                    
                    final_package = await self.validator.validate_and_generate(pure_text, url)
                    if final_package and final_package["extracted_data"]["is_valid_data"]:
                        await self.save_purified_split_data(folder_path, final_package["extracted_data"])
                        self.url_manager.add_url_to_master(url)
                        success = True
                    else:
                        logger.warning(f"Data from {url} was JUNK. Raw kept, moving on.")
                else:
                    logger.error(f"Scraping completely failed for {url}.")

                # --- NEW LOGIC: DDGS MEDIC (THE RULE OF 3) ---
                if not success:
                    logger.warning(f"🚑 Target failed! Using DDGS Fallback Medic for dead link.")
                    fallback_urls = self.url_manager.fetch_fallback_urls(url, max_results=5)
                    
                    successful_fallbacks = 0
                    for fb_url in fallback_urls:
                        if successful_fallbacks >= 3:
                            logger.info("🎯 Got 3 successful fallbacks. Halting DDGS medic for this target.")
                            break
                            
                        logger.info(f"Attempting Fallback Vector: {fb_url}")
                        fb_text = await self.scraper.scrape(fb_url)
                        
                        if fb_text:
                            fb_folder = self._create_folder_structure(fb_url)
                            await self.save_raw_data(fb_folder, fb_text)
                            
                            fb_package = await self.validator.validate_and_generate(fb_text, fb_url)
                            if fb_package and fb_package["extracted_data"]["is_valid_data"]:
                                await self.save_purified_split_data(fb_folder, fb_package["extracted_data"])
                                self.url_manager.add_url_to_master(fb_url)
                                successful_fallbacks += 1
                # ---------------------------------------------
                
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
    
