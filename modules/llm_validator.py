import os
from pydantic import BaseModel, Field
from typing import List
from loguru import logger
from openai import AsyncOpenAI
import instructor

# 1. THE SCHEMATIC (AI ko exactly kya format chahiye)
class ExtractedData(BaseModel):
    is_valid_data: bool = Field(description="True ONLY if the text contains actual programming, cybersecurity logic, or exploit POCs. False if it's just news, ads, or garbage.")
    topic_title: str = Field(description="A precise, professional title for the exploit or logic.")
    core_logic_summary: str = Field(description="Detailed summary of how the logic or attack vector works.")
    extracted_code_snippets: List[str] = Field(description="List of raw code blocks extracted from the text. Keep it pure code.")
    debate_questions: List[str] = Field(description="5 extreme, highly technical debate questions for Red Team vs Blue Team AI based on this data.")

class LLMValidator:
    def __init__(self):
        logger.info("Awakening the LLM Judge (Hugging Face Interface)...")
        # Yeh Github secrets se teri HF key uthayega
        self.hf_token = os.getenv("HUGGINGFACE_API_KEY")
        
        # Hum OpenAI library ka use karke Hugging Face ke API ko call kar rahe hain (Instructor ke sath)
        self.client = instructor.from_openai(
            AsyncOpenAI(
                base_url="https://api-inference.huggingface.co/v1/",
                api_key=self.hf_token
            ),
            mode=instructor.Mode.JSON
        )
        # Using a top-tier model for logic validation
        self.model = "Qwen/Qwen2.5-72B-Instruct"

    async def validate_and_generate(self, pure_text: str, url: str) -> dict:
        """The AI Interrogation Room"""
        logger.info("🧠 Passing raw data to LLM Validator for purification...")
        
        try:
            # Model context window ko safe rakhne ke liye text ko limit kar rahe hain
            safe_text = pure_text[:12000] 
            
            response = await self.client.chat.completions.create(
                model=self.model,
                response_model=ExtractedData,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an elite cybersecurity AI data validator. Your job is to extract highly technical logic, architecture details, and code from raw scraped data. If the text is junk, news, or lacks deep technical depth, strictly set is_valid_data to False."
                    },
                    {
                        "role": "user", 
                        "content": f"Analyze this scraped text from {url}:\n\n{safe_text}"
                    }
                ]
            )
            
            # Agar data kachra hai, toh system aage nahi badhega
            if not response.is_valid_data:
                logger.warning(f"⚖️ LLM Judge Verdict: JUNK/REJECTED for {url}")
            else:
                logger.success(f"⚖️ LLM Judge Verdict: APPROVED & PURIFIED for {url}")
                
            return {
                "source_url": url,
                "extracted_data": response.model_dump()
            }
            
        except Exception as e:
            logger.error(f"❌ LLM Validator failed or API rate limit hit: {e}")
            # Agar error aaye toh safe side False return karo taaki kachra save na ho
            return None
  
