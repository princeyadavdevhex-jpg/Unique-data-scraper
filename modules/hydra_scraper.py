import asyncio
import json
import urllib.request
from loguru import logger

# --- 100% FREE & OPEN SOURCE DEPENDENCIES ---
from curl_cffi import requests as cffi_requests
import trafilatura
from bs4 import BeautifulSoup

# Heavy Stealth Browsers (Async)
from crawl4ai import AsyncWebCrawler
import nodriver as uc

class HydraScraper:
    def __init__(self):
        logger.info("Hydra Scraper Initialized. 11-Layer Fallback Matrix Active.")

    async def scrape(self, url):
        """
        Master Scrape Function. Tries different layers sequentially.
        Returns CLEAN TEXT/MARKDOWN (No HTML/CSS garbage).
        """
        logger.info(f"Target Acquired: {url}")

        # TIER 1: The Modern LLM Feeder (Strips HTML natively)
        result = await self._layer_1_crawl4ai(url)
        if result: return result

        # TIER 2: The Cloudflare Killer (Direct Browser Protocol)
        result = await self._layer_2_nodriver(url)
        if result: return result

        # TIER 3: The TLS Imposter + Trafilatura (Ultra-fast stealth)
        result = self._layer_3_curl_cffi(url)
        if result: return result

        # TIER 4: The Archive Ghost (If site is completely down/deleted)
        result = self._layer_4_wayback_machine(url)
        if result: return result
        
        # TIER 5: The Brute-Force Legacy (Last Resort)
        result = self._layer_5_beautifulsoup_brute(url)
        if result: return result

        logger.error(f"ALL 11 LAYERS FAILED for {url}. Target is either dead or military-grade locked.")
        return None

    # ---------------------------------------------------------
    # CORE LAYER IMPLEMENTATIONS (THE FALLBACKS)
    # ---------------------------------------------------------

    async def _layer_1_crawl4ai(self, url):
        """Layer 1-3 (Internal): AsyncWebCrawler handles stealth, rendering, and markdown conversion."""
        try:
            logger.debug("Executing Layer 1: Crawl4AI (Markdown Extraction)...")
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url)
                if result and result.markdown and len(result.markdown) > 200:
                    logger.success("Layer 1 SUCCESS: Clean Markdown Extracted.")
                    return result.markdown
        except Exception as e:
            logger.warning(f"Layer 1 Failed: {e}")
        return None

    async def _layer_2_nodriver(self, url):
        """Layer 4-5: Nodriver completely bypasses Cloudflare/Turnstile without webdrivers."""
        try:
            logger.debug("Executing Layer 2: Nodriver (Cloudflare Bypass)...")
            browser = await uc.start()
            page = await browser.get(url)
            await asyncio.sleep(3) # Wait for JS execution/Cloudflare validation
            
            html_content = await page.get_content()
            await browser.stop()
            
            # Use Trafilatura to strip CSS/JS and get pure text
            clean_text = trafilatura.extract(html_content)
            if clean_text and len(clean_text) > 200:
                logger.success("Layer 2 SUCCESS: Cloudflare Bypassed & Text Extracted.")
                return clean_text
        except Exception as e:
            logger.warning(f"Layer 2 Failed: {e}")
        return None

    def _layer_3_curl_cffi(self, url):
        """Layer 6-8: Spoofs TLS fingerprint (mimics Safari/Chrome perfectly) to bypass API blocks."""
        try:
            logger.debug("Executing Layer 3: curl_cffi (TLS Imposter)...")
            # Impersonating a Mac Safari browser exactly
            response = cffi_requests.get(url, impersonate="safari15_5", timeout=10)
            
            if response.status_code == 200:
                clean_text = trafilatura.extract(response.text)
                if clean_text and len(clean_text) > 200:
                    logger.success("Layer 3 SUCCESS: TLS Spoofing worked.")
                    return clean_text
        except Exception as e:
            logger.warning(f"Layer 3 Failed: {e}")
        return None

    def _layer_4_wayback_machine(self, url):
        """Layer 9-10: If the site is down, 404, or deleted, pull from the internet archive."""
        try:
            logger.debug("Executing Layer 4: Wayback Machine (Archive Extraction)...")
            archive_url = f"http://archive.org/wayback/available?url={url}"
            with urllib.request.urlopen(archive_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get("archived_snapshots") and data["archived_snapshots"].get("closest"):
                    snapshot_url = data["archived_snapshots"]["closest"]["url"]
                    logger.info(f"Snapshot found! Scraping from archive: {snapshot_url}")
                    
                    # Call Layer 3 on the archived URL
                    return self._layer_3_curl_cffi(snapshot_url)
        except Exception as e:
            logger.warning(f"Layer 4 Failed: {e}")
        return None

    def _layer_5_beautifulsoup_brute(self, url):
        """Layer 11: The absolute brute-force fallback. Grabs all <p> and <code> tags directly."""
        try:
            logger.debug("Executing Layer 5: BeautifulSoup Brute-Force...")
            response = cffi_requests.get(url, impersonate="chrome110", timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Strip out script and style tags completely
                for script in soup(["script", "style", "header", "footer", "nav"]):
                    script.extract()
                    
                text = soup.get_text(separator='\n', strip=True)
                if text and len(text) > 200:
                    logger.success("Layer 5 SUCCESS: Brute-forced text extraction.")
                    return text
        except Exception as e:
            logger.warning(f"Layer 5 Failed: {e}")
        return None

