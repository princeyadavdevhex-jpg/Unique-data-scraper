import os
import asyncio
import json
import urllib.request
from loguru import logger
from typing import Optional, List

# --- DEPENDENCIES (Install via requirements.txt in GitHub Actions) ---
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
import nodriver as uc
from playwright.async_api import async_playwright
from camoufox.async_api import AsyncCamoufox
from DrissionPage import ChromiumPage
from seleniumbase import SB

# Extractors & Purifiers
from readability import Document as ReadabilityDoc
import justext
import html2text
from docling.document_converter import DocumentConverter
from tree_sitter import Language, Parser # The Code Sniper

# LLM Enforcer
import instructor
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

class ExtractedCyberData(BaseModel):
    is_valid_data: bool = Field(description="Is this valid IT/Cybersecurity data? True/False")
    topic_title: str = Field(description="Main title of the vulnerability or topic.")
    core_logic_summary: str = Field(description="Deep architectural explanation of the issue.")
    extracted_code_snippets: List[str] = Field(description="Exact exploit, patch, or POC code found.")

class HydraScraper:
    def __init__(self):
        logger.info("Hydra Scraper V3 Initialized. 17-Layer God-Tier Matrix Active.")
        
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.llm_client = instructor.from_openai(
            AsyncOpenAI(base_url="https://api-inference.huggingface.co/v1/", api_key=self.hf_api_key),
            mode=instructor.Mode.JSON
        )
        self.model_name = "Qwen/Qwen2.5-32B-Instruct"

    async def scrape(self, url: str) -> Optional[dict]:
        logger.info(f"Target Acquired: {url}")
        raw_html = None
        pure_text = None

        # ==========================================
        # PHASE 1: THE FETCHING GAUNTLET (Layers 1-9)
        # ==========================================
        
        # 1. API Hijacker
        pure_text = await self._layer_1_network_hijack(url)
        
        # 2. Camoufox (Anti-Detect Browser)
        if not pure_text: raw_html = await self._layer_2_camoufox(url)
        
        # 3. DrissionPage (Packet Intercept)
        if not raw_html and not pure_text: raw_html = self._layer_3_drissionpage(url)

        # 4. SeleniumBase (Undetected Mode)
        if not raw_html and not pure_text: raw_html = self._layer_4_seleniumbase(url)

        # 5. Nodriver (CDP Bypass)
        if not raw_html and not pure_text: raw_html = await self._layer_5_nodriver(url)

        # 6. Crawl4AI (AOM Parsing)
        if not raw_html and not pure_text: raw_html = await self._layer_6_crawl4ai(url)

        # 7. curl_cffi (TLS Imposter)
        if not raw_html and not pure_text: raw_html = self._layer_7_tls_imposter(url)

        # 8. Wayback Machine
        if not raw_html and not pure_text: raw_html = self._layer_8_wayback(url)

        # 9. Google Cache API (Alternative Archive)
        if not raw_html and not pure_text: raw_html = self._layer_9_google_cache(url)

        if not raw_html and not pure_text:
            logger.error("All 9 Infiltration layers failed. Target vaporized.")
            return None

        # ==========================================
        # PHASE 2: PURIFICATION & SNIPING (Layers 10-15)
        # ==========================================
        if raw_html and not pure_text:
            logger.info("Engaging 6-Layer Extraction Titans...")
            pure_text = self._purify_content(raw_html, url)

        if not pure_text or len(pure_text) < 100:
            return None

        # ==========================================
        # PHASE 3: THE AI ENFORCER (Layers 16-17)
        # ==========================================
        logger.info("Handing over to HF 32B Enforcer...")
        final_json = await self._layer_16_17_enforce_llm(pure_text)
        
        if final_json and final_json.is_valid_data:
            logger.success("✅ 17-Layer Extraction Complete. Perfect JSON secured.")
            return final_json.model_dump()
        return None

    # ---------------------------------------------------------
    # LAYER IMPLEMENTATIONS
    # ---------------------------------------------------------

    async def _layer_1_network_hijack(self, url):
        captured_data = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                async def handle_response(res):
                    if "json" in res.headers.get("content-type", "") and res.status == 200:
                        try: captured_data.append(str(await res.json()))
                        except: pass
                page.on("response", handle_response)
                await page.goto(url, wait_until="networkidle", timeout=10000)
                await browser.close()
                if captured_data: return "\n".join(captured_data)
        except Exception: pass
        return None

    async def _layer_2_camoufox(self, url):
        try:
            async with AsyncCamoufox() as browser:
                page = await browser.new_page()
                await page.goto(url)
                return await page.content()
        except Exception: return None

    def _layer_3_drissionpage(self, url):
        try:
            page = ChromiumPage()
            page.get(url)
            html = page.html
            page.quit()
            return html
        except Exception: return None

    def _layer_4_seleniumbase(self, url):
        try:
            with SB(uc=True, headless=True) as sb:
                sb.open(url)
                return sb.get_page_source()
        except Exception: return None

    async def _layer_5_nodriver(self, url):
        try:
            browser = await uc.start()
            page = await browser.get(url)
            await asyncio.sleep(3)
            html = await page.get_content()
            await browser.stop()
            return html
        except Exception: return None

    async def _layer_6_crawl4ai(self, url):
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                res = await crawler.arun(url=url)
                if res and res.html: return res.html
        except Exception: return None

    def _layer_7_tls_imposter(self, url):
        try:
            res = cffi_requests.get(url, impersonate="safari15_5", timeout=10)
            if res.status_code == 200: return res.text
        except Exception: return None

    def _layer_8_wayback(self, url):
        try:
            res = urllib.request.urlopen(f"http://archive.org/wayback/available?url={url}", timeout=10)
            data = json.loads(res.read().decode())
            if data.get("archived_snapshots"):
                return self._layer_7_tls_imposter(data["archived_snapshots"]["closest"]["url"])
        except Exception: return None

    def _layer_9_google_cache(self, url):
        try:
            return self._layer_7_tls_imposter(f"https://webcache.googleusercontent.com/search?q=cache:{url}")
        except Exception: return None

    def _purify_content(self, html: str, url: str) -> str:
        # Layer 10: Docling
        try:
            text = DocumentConverter().convert(html).document.export_to_markdown()
            if len(text) > 200: return text
        except Exception: pass

        # Layer 11-14: Readability + html2text + Tree-sitter + jusText
        try:
            clean_html = ReadabilityDoc(html).summary()
            markdown_text = html2text.HTML2Text().handle(clean_html)
            
        # --- THE MISSING TREE-SITTER SNIPER LOGIC ---
            try:
                # GitHub actions pe pehle se compiled .so file hogi
                PY_LANGUAGE = Language('build/my-languages.so', 'python')
                CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')
                parser = Parser()
                
                # Hunting for Python Code
                parser.set_language(PY_LANGUAGE)
                tree = parser.parse(bytes(clean_html, "utf8"))
                
                # Hunting for C++ Code
                parser.set_language(CPP_LANGUAGE)
                tree_cpp = parser.parse(bytes(clean_html, "utf8"))
                
                # Add extracted raw AST code to markdown
                markdown_text += "\n\n[AST SNIPER EXTRACTED CODE]\n" + str(tree.root_node) + "\n" + str(tree_cpp.root_node)
            except Exception as e:
                logger.debug(f"Tree-sitter AST compilation skipped/failed: {e}")
            # --------------------------------------------

            paragraphs = justext.justext(html, justext.get_stoplist("English"))
            linguistic_text = "\n".join([p.text for p in paragraphs if not p.is_boilerplate])
            
            return markdown_text + "\n\n" + linguistic_text
        except Exception:
            # Layer 15: Brute Force
            soup = BeautifulSoup(html, 'html.parser')
            for s in soup(["script", "style"]): s.extract()
            return soup.get_text(separator='\n', strip=True)

    async def _layer_16_17_enforce_llm(self, text: str) -> ExtractedCyberData:
        try:
            truncated = text[:30000]
            prompt = f"Analyze this web text. If valid cybersecurity logic/code, set True. Extract pure code blocks.\n\nDATA:\n{truncated}"
            return await self.llm_client.chat.completions.create(
                model=self.model_name,
                response_model=ExtractedCyberData,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.1
            )
        except Exception: return None
        
