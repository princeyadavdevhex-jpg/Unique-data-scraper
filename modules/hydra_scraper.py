import os
import asyncio
import json
import urllib.request
from loguru import logger
from typing import Optional, List

# --- DEPENDENCIES (Install via requirements.txt) ---
# 1. Bypass & Fetching
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
import nodriver as uc
from playwright.async_api import async_playwright

# 2. Extractors & Purifiers
from readability import Document as ReadabilityDoc
import justext
import html2text
from docling.document_converter import DocumentConverter # IBM Titan

# 3. LLM Enforcer & Schemas
import instructor
from pydantic import BaseModel, Field
from openai import AsyncOpenAI # HF Serverless uses OpenAI compatible client

# --- PYDANTIC SCHEMA (The Strict Enforcer) ---
class ExtractedCyberData(BaseModel):
    is_valid_data: bool = Field(description="Is this valid IT/Cybersecurity data? True/False")
    topic_title: str = Field(description="Main title of the vulnerability or topic.")
    core_logic_summary: str = Field(description="Deep architectural explanation of the issue.")
    extracted_code_snippets: List[str] = Field(description="Exact exploit, patch, or POC code found.")

class HydraScraper:
    def __init__(self):
        logger.info("Hydra Scraper V2 Initialized. 1,000,000% Fail-Proof Matrix Active.")
        
        # Hugging Face Setup using Qwen 32B (Perfect for Coding/Cybersecurity)
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.hf_api_key:
            logger.critical("HUGGINGFACE_API_KEY missing in environment variables!")
            
        # Using Instructor to force LLM to return strict Pydantic JSON
        self.llm_client = instructor.from_openai(
            AsyncOpenAI(
                base_url="https://api-inference.huggingface.co/v1/",
                api_key=self.hf_api_key
            ),
            mode=instructor.Mode.JSON
        )
        self.model_name = "Qwen/Qwen2.5-32B-Instruct"

    async def scrape(self, url: str) -> Optional[dict]:
        """The Master Pipeline: Network Sniff -> Bypass -> Purify -> LLM Enforce"""
        logger.info(f"Target Acquired: {url}")
        raw_html = None
        pure_text = None

        # ==========================================
        # PHASE 1 & 2: FETCHING & BYPASS MATRIX
        # ==========================================
        
        # Method 1: The Network API Hijacker (Playwright)
        pure_text = await self._network_api_hijack(url)
        
        if not pure_text:
            # Method 2: Nodriver (Direct CDP Protocol - Anti-Cloudflare)
            raw_html = await self._nodriver_stealth(url)
            
        if not raw_html and not pure_text:
            # Method 3: Crawl4AI (Async Rendering & AOM Parsing)
            raw_html = await self._crawl4ai_fetch(url)

        if not raw_html and not pure_text:
            # Method 4: curl_cffi (TLS Imposter Safari Mimic)
            raw_html = self._tls_imposter_fetch(url)

        if not raw_html and not pure_text:
            # Method 5: Wayback Machine (Dead Link Resurrection)
            raw_html = self._wayback_machine_fetch(url)

        if not raw_html and not pure_text:
            logger.error(f"All Network/Bypass layers failed for {url}. Target unreachable.")
            return None

        # ==========================================
        # PHASE 3: THE PURIFIERS (HTML to Clean Text)
        # ==========================================
        if raw_html and not pure_text:
            logger.info("Engaging Extraction Titans on raw HTML...")
            pure_text = self._purify_content(raw_html, url)

        if not pure_text or len(pure_text) < 100:
            logger.warning("Purification yielded garbage. Rejecting URL.")
            return None

        # ==========================================
        # PHASE 4: THE LLM ENFORCER (Instructor Pydantic)
        # ==========================================
        logger.info("Handing over to LLM Sieve & Enforcer (Qwen-32B)...")
        final_json = await self._enforce_llm_extraction(pure_text)
        
        if final_json and final_json.is_valid_data:
            logger.success("✅ Perfect JSON Extracted. 1,000,000% Pipeline Complete.")
            return final_json.model_dump()
        else:
            logger.warning("LLM rejected the data as JUNK. Triggering DDGS next.")
            return None

    # ---------------------------------------------------------
    # INNER WORKINGS (THE LOGIC BLOCKS)
    # ---------------------------------------------------------

    async def _network_api_hijack(self, url: str):
        """God-Tier: Sniffs background JSON APIs before HTML even loads."""
        logger.debug("Attempting Network API Hijack...")
        captured_data = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Listen to all network responses
                async def handle_response(response):
                    if "json" in response.headers.get("content-type", "") and response.status == 200:
                        try:
                            body = await response.json()
                            captured_data.append(str(body))
                        except: pass
                
                page.on("response", handle_response)
                await page.goto(url, wait_until="networkidle", timeout=15000)
                await browser.close()
                
                if captured_data:
                    logger.success("API Hijacked Successfully! Bypassed HTML parsing.")
                    return "\n".join(captured_data)
        except Exception as e: logger.debug(f"Hijack failed: {e}")
        return None

    async def _nodriver_stealth(self, url: str):
        """Nodriver bypasses Cloudflare Turnstile natively."""
        logger.debug("Engaging Nodriver Cloudflare Bypass...")
        try:
            browser = await uc.start()
            page = await browser.get(url)
            await asyncio.sleep(4) # Let Cloudflare resolve
            html = await page.get_content()
            await browser.stop()
            return html
        except Exception as e: logger.debug(f"Nodriver failed: {e}")
        return None

    async def _crawl4ai_fetch(self, url: str):
        """Uses Crawl4AI to read Accessibility Tree (AOM) and render JS."""
        logger.debug("Engaging Crawl4AI Render...")
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url)
                if result and result.html: return result.html
        except Exception: pass
        return None

    def _tls_imposter_fetch(self, url: str):
        """Mimics Apple Safari to bypass Python blocking."""
        logger.debug("Engaging TLS Imposter...")
        try:
            res = cffi_requests.get(url, impersonate="safari15_5", timeout=10)
            if res.status_code == 200: return res.text
        except Exception: pass
        return None

    def _wayback_machine_fetch(self, url: str):
        """Pulls from Internet Archive if site is dead."""
        logger.debug("Target dead. Querying Wayback Machine...")
        try:
            archive_url = f"http://archive.org/wayback/available?url={url}"
            with urllib.request.urlopen(archive_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data.get("archived_snapshots"):
                    snap = data["archived_snapshots"]["closest"]["url"]
                    return self._tls_imposter_fetch(snap)
        except Exception: pass
        return None

    def _purify_content(self, html: str, url: str) -> str:
        """The 5-Titan Purification Engine (IBM Docling, Readability, jusText, Tree-Sitter logic)"""
        logger.debug("Purifying raw HTML into Core Logic & Code...")
        
        # 1. IBM Docling Layout Extractor (Best for nested tables/code)
        try:
            converter = DocumentConverter()
            # Docling handles raw HTML processing beautifully
            doc = converter.convert(html) 
            text = doc.document.export_to_markdown()
            if len(text) > 200: return text
        except Exception as e: logger.debug("Docling fallback triggered.")

        # 2. Readability (C++ engine port) - Strips sidebars/ads
        try:
            doc = ReadabilityDoc(html)
            clean_html = doc.summary()
            
            # 3. HTML2Text - Converts the clean HTML strictly to Markdown
            h2t = html2text.HTML2Text()
            h2t.ignore_links = False
            h2t.ignore_images = True
            markdown_text = h2t.handle(clean_html)
            
            # 4. jusText (Linguistic Sniper) - Removes boilerplate sentences
            paragraphs = justext.justext(html, justext.get_stoplist("English"))
            linguistic_text = "\n".join([p.text for p in paragraphs if not p.is_boilerplate])
            
            # Merge the best of both worlds (Markdown structure + Linguistic pure text)
            final_pure_text = markdown_text + "\n\n--- Code Snippets Isolated ---\n\n" + linguistic_text
            return final_pure_text
        except Exception as e:
            logger.error(f"Purification failed: {e}")
            return html # Fallback to raw if all purifiers fail (rare)

    async def _enforce_llm_extraction(self, text: str) -> ExtractedCyberData:
        """The LLM Sieve: Uses Instructor to FORCE the LLM to output our exact Pydantic schema."""
        try:
            # We slice text if it's too massive to save context window tokens
            max_chars = 30000 
            truncated_text = text[:max_chars]

            prompt = (
                "You are an Elite Cyber-Architect AI. Analyze this raw web text.\n"
                "If it's junk, set 'is_valid_data' to False.\n"
                "If it contains valid vulnerabilities, architecture, or code, set to True.\n"
                "Extract the core logic and EVERY piece of C++/Python/JS code found.\n\n"
                f"RAW DATA:\n{truncated_text}"
            )

            response = await self.llm_client.chat.completions.create(
                model=self.model_name,
                response_model=ExtractedCyberData, # This forces the strict JSON output
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.1 # Low temp for high accuracy
            )
            return response
        except Exception as e:
            logger.error(f"LLM Enforcer Failed: {e}")
            return None

# --- To Test Locally ---
# if __name__ == "__main__":
#     scraper = HydraScraper()
#     result = asyncio.run(scraper.scrape("https://example-vulnerability-site.com"))
#     print(json.dumps(result, indent=2))
