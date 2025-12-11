import os
import json
from openai import OpenAI
from typing import Optional

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate_ad_caption(self, title: str, description: str, price: Optional[float] = None, business_name: Optional[str] = None, instruction: Optional[str] = None) -> str:
        """Generate a STRICT bullet-point list."""
        system_instruction = """You are a formatting assistant. 
        Your ONLY job is to take product details and format them into a clean vertical list with emojis.
        
        STRICT RULES:
        1. Start with a Headline in this format: "🔥 [TITLE]"
        2. Create 3 bullet points using these specific emojis if applicable: 
           - 🔌 Product: [Name]
           - 📝 Details: [Description]
           - 🏢 Vendor: [Business Name]
        3. DO NOT include Price.
        4. DO NOT include Contact Info.
        5. DO NOT include the word "None". If a detail is missing, skip that line.
        6. Do not write any intro or outro text."""

        user_content = f"""
        Title: {title}
        Description: {description if description else 'Available now'}
        Business: {business_name}
        {f'Instruction: {instruction}' if instruction else ''}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=150,
                temperature=0.5 
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating caption: {e}")
            return f"🔥 {title}\n🔌 Product: {title}\n📝 Details: {description}"

    def smart_chat(self, user_name, user_memory, user_message, product_data):
        """
        Analyzes message, replies naturally, and extracts new facts about the user.
        """
        system_prompt = f"""
        You are EasyEasy, a smart, friendly shopping assistant on WhatsApp.
        
        USER CONTEXT:
        - Name: {user_name}
        - MEMORY (What we know about them): {user_memory}
        
        AVAILABLE PRODUCTS ON EASYEASY (Recommend these if relevant):
        {product_data}
        
        YOUR GOAL:
        1. Reply naturally to the user's message. Be helpful, empathetic, and human-like (not robotic).
        2. If the user mentions a preference (e.g., "I love red shoes", "I'm a student"), extract it as a "new_fact".
        3. If a product matches their request, recommend it enthusiastically.
        
        OUTPUT FORMAT (JSON):
        {{
            "reply": "Your friendly reply here...",
            "new_fact": "Short fact learned about user (or null if nothing new)"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"} 
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI Error: {e}")
            return {"reply": "I'm having a little trouble thinking right now, but I'm here! How can I help?", "new_fact": None}

    def generate_welcome_message(self, user_name: Optional[str] = None) -> str:
        name_part = f"Hello {user_name}! " if user_name else "Hello! "
        prompt = f"""{name_part}Generate a warm, friendly welcome message for a WhatsApp bot that helps vendors advertise their products and helps users discover great deals. Keep it brief (2-3 sentences) and inviting."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a friendly bot assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating welcome message: {e}")
            return f"{name_part}Welcome to EasyEasy! 🎉 Your marketplace for amazing deals and promotions."