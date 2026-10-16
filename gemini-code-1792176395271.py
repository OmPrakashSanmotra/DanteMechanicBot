"""
Dante S-Rank Mechanic AI - Complete Single-File Telegram Bot
100% Ready to Copy, Paste & Run.
"""

import os
import logging
from typing import List, Dict, Any
from openai import OpenAI
from supabase import create_client, Client
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Credentials ---
TELEGRAM_BOT_TOKEN = "8937656016:AAGqlodH23n0CIhoD34C8b2EDLz5OXHP9YQ"

# Agar environment variables set nahi hain toh yahan apni direct keys bhi daal sakta hai testing ke liye:
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-service-role-key")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")


class DanteUltimateEngine:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.llm_model = "gpt-4o"

    def _get_embedding(self, text: str) -> List[float]:
        response = self.openai_client.embeddings.create(
            input=[text],
            model=self.embedding_model
        )
        return response.data[0].embedding

    def query_semantic_memory(self, symptom_query: str, match_threshold: float = 0.70, count: int = 3) -> List[Dict[str, Any]]:
        query_embedding = self._get_embedding(symptom_query)
        try:
            response = self.supabase.rpc(
                "match_dante_memories",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": count
                }
            ).execute()
            return response.data
        except Exception as e:
            logger.warning(f"Vector memory search note: {e}")
            return []

    def diagnose(self, user_query: str, vehicle_model: str = "Workshop General / Auto-Detect") -> str:
        similar_memories = self.query_semantic_memory(user_query)
        
        memory_context = ""
        if similar_memories:
            memory_context = "\n\nPAST WORKSHOP MEMORY FOUND:\n"
            for idx, mem in enumerate(similar_memories, 1):
                memory_context += (
                    f"{idx}. Model: {mem['vehicle_model']} | System: {mem['system_type']}\n"
                    f"   Symptom: {mem['symptom_description']}\n"
                    f"   Verified Fix: {mem['verified_fix']} (Match: {mem['similarity']:.2f})\n"
                )

        system_prompt = (
            "You are Dante, the ultimate Ustad Mechanic for Indian two-wheelers and EVs. "
            "Speak in Hinglish with street-smart garage authority. "
            "Give output in clean plain text using simple formatting:\n"
            "SYMPTOM BREAKDOWN:\n"
            "MULTIMETER & PINOUT CHECK:\n"
            "USTAD FIX:\n"
            f"{memory_context}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Vehicle Model: {vehicle_model}\nFault/Symptom: {user_query}"}
        ]

        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.2
        )

        return response.choices.message.content


# Initialize Dante Engine
dante_engine = DanteUltimateEngine()


# --- Telegram Bot Message Handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_name = update.message.from_user.first_name
    
    logger.info(f"Received query from {user_name}: {user_text}")
    await update.message.reply_text("Dante checking workshop memory & wiring schematics...")

    try:
        diagnostic_response = dante_engine.diagnose(user_query=user_text)
        
        if len(diagnostic_response) > 4000:
            for x in range(0, len(diagnostic_response), 4000):
                await update.message.reply_text(diagnostic_response[x:x+4000])
        else:
            await update.message.reply_text(diagnostic_response)
            
    except Exception as e:
        logger.error(f"Error generating Dante response: {e}")
        await update.message.reply_text("Bhai, kuch technical error aa gaya. Dobara try karo!")


if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Dante S-Rank Telegram Bot is live and listening in the workshop bay...")
    app.run_polling()