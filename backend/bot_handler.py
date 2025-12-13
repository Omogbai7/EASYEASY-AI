import json
import uuid
import random
import os
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
# FIX 1: Added SystemSetting to imports
from models import db, User, Promo, Payment, Broadcast, Conversation, SupportTicket, PromoStatus, PaymentStatus, Order, OrderStatus, SystemSetting
from services.whatsapp_service import WhatsAppService
from services.openai_service import OpenAIService

# Configuration
COMMUNITY_CODE = "EASY50" 
DAILY_AI_LIMIT = 10
PAYMENT_LINK = os.getenv("LINK_PAYMENT_FLUTTERWAVE", "https://flutterwave.com/pay/default")

class BotHandler:
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.openai = OpenAIService()

    def get_interest_map(self):
        return {
            "1": "Business", "2": "Fashion", "3": "Food", "4": "Campus",
            "5": "Jobs", "6": "Tech", "7": "Entertainment", "8": "Real Estate",
            "9": "Health", "10": "Education"
        }

    def handle_message(self, phone_number: str, message_text: str, message_type: str = "text"):
        """Main message handler"""

        # 1. Get or create user
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.session.add(user)
            db.session.commit()

        # 2. Get or create conversation
        conversation = Conversation.query.filter_by(phone_number=phone_number).first()
        if not conversation:
            conversation = Conversation(phone_number=phone_number, state="WELCOME", context="{}")
            db.session.add(conversation)
            db.session.commit()
            self.send_welcome_message(phone_number, user)
            return

        conversation.last_message_at = datetime.utcnow()
        state = conversation.state
        msg_lower = message_text.lower().strip() if message_text else ""

        # --- GLOBAL CANCEL / RESTART ---
        if msg_lower in ["cancel", "restart", "reset", "quit", "abort"]:
            self.whatsapp.send_text_message(phone_number, "🔄 Operation cancelled. Resetting...")
            if user.is_vendor and user.current_mode == "vendor":
                conversation.state = "VENDOR_MENU"
                self.show_vendor_menu(phone_number)
            elif user.is_subscriber and user.current_mode == "subscriber":
                conversation.state = "CUSTOMER_MENU"
                self.send_customer_menu(phone_number)
            else:
                conversation.state = "WELCOME"
                self.send_welcome_message(phone_number, user)
            db.session.commit()
            return

        # --- GLOBAL COMMANDS ---
        if msg_lower in ["hi", "hello", "hey", "menu", "start"]:
            self.handle_global_entry(phone_number, user, conversation)
            return

        # --- STATE MACHINE ---
        if state == "WELCOME":
            self.handle_role_selection(phone_number, message_text, conversation, user)
        elif state == "SELECT_DASHBOARD":
            self.handle_dashboard_selection(phone_number, message_text, conversation, user)

        # VENDOR FLOWS
        elif state == "VENDOR_NAME":
            self.handle_vendor_name(phone_number, message_text, conversation, user)
        elif state == "VENDOR_BUSINESS":
            self.handle_vendor_business(phone_number, message_text, conversation, user)
        elif state == "VENDOR_DESC": 
            self.handle_vendor_desc(phone_number, message_text, conversation, user)
        elif state == "VENDOR_VERIFICATION":
            self.whatsapp.send_text_message(phone_number, "⚠️ Please upload an image or PDF document for verification (NIN, Utility Bill, or Bank Statement) to proceed.")
        elif state == "VENDOR_MENU":
            self.handle_vendor_menu(phone_number, message_text, conversation, user)
        
        # PROMO CREATION
        elif state == "PROMO_TITLE":
            self.handle_promo_title(phone_number, message_text, conversation)
        elif state == "PROMO_DESCRIPTION":
            self.handle_promo_description(phone_number, message_text, conversation)
        elif state == "PROMO_CATEGORY":
            self.handle_promo_category(phone_number, message_text, conversation)
        elif state == "PROMO_TARGET_GENDER":
            self.handle_promo_target_gender(phone_number, message_text, conversation)
        elif state == "PROMO_PRICE":
            self.handle_promo_price(phone_number, message_text, conversation)
        elif state == "PROMO_CONTACT":
            self.handle_promo_contact(phone_number, message_text, conversation)
        elif state == "PROMO_MEDIA":
            self.handle_promo_media(phone_number, message_text, conversation, user)   
        elif state == "PROMO_REVIEW_AI":
            self.handle_promo_ai_review(phone_number, message_text, conversation, user)
        elif state == "PROMO_TYPE":
            self.handle_promo_type_selection(phone_number, message_text, conversation, user)
        elif state == "PAID_IMPRESSIONS":
            self.handle_paid_impressions(phone_number, message_text, conversation, user)
        elif state == "VENDOR_VERIFY_CODE":
            self.handle_vendor_code_verification(phone_number, message_text, conversation, user)
        elif state == "SUPPORT_MESSAGE":
            self.handle_support_message(phone_number, message_text, conversation, user)

        # Waiting states
        elif state in ["PAID_PAYMENT_CONFIRM", "VENDOR_JOIN_COMMUNITY", 
                       "FREE_TASKS_SOCIAL", "CUSTOMER_COMMUNITY_TASK"]:
            pass 

        # Free Flow Inputs
        elif state == "FREE_TASK_SCREENSHOT_1":
            self.handle_free_screenshot_1(phone_number, message_text, conversation, user)
        elif state == "FREE_TASK_SCREENSHOT_2":
            self.handle_free_screenshot_2(phone_number, message_text, conversation, user)

        # CUSTOMER FLOWS
        elif state == "CUSTOMER_NAME":
            self.handle_customer_name(phone_number, message_text, conversation, user)
        elif state == "CUSTOMER_GENDER":
            self.handle_customer_gender(phone_number, message_text, conversation, user)
        elif state == "CUSTOMER_INTERESTS":
            self.handle_customer_interests(phone_number, message_text, conversation, user)
        elif state == "CUSTOMER_REFERRAL":
            self.handle_customer_referral(phone_number, message_text, conversation, user)
        elif state == "CUSTOMER_COMMUNITY_CODE":
            self.handle_community_code_verification(phone_number, message_text, conversation, user)
        elif state == "CUSTOMER_MENU":
            self.handle_customer_menu(phone_number, message_text, conversation, user)
        elif state == "CUSTOMER_UPDATE_INTERESTS":
            self.handle_update_interests(phone_number, message_text, conversation, user)
        
        # AI Chat Fallback
        elif user.is_subscriber and user.current_mode == "subscriber" and conversation.state == "CUSTOMER_MENU":
             self.handle_customer_ai_chat(phone_number, message_text, conversation, user)

        db.session.commit()

    # GLOBAL & LIMITS
    def check_ai_limits(self, user):
        now = datetime.utcnow()
        if user.last_ai_usage and user.last_ai_usage.date() < now.date():
            user.daily_ai_count = 0 
        if user.daily_ai_count >= DAILY_AI_LIMIT:
            return False
        return True

    # 1. DAILY CHECK-IN 
    def handle_global_entry(self, phone_number, user, conversation):
        now = datetime.utcnow()
        checkin_msg = ""
        
        # Check if 24 hours passed
        if not user.last_checkin or (now - user.last_checkin) >= timedelta(hours=24):
            user.points += 500  
            user.last_checkin = now
            checkin_msg = "🌟 +500 Points for daily check-in!\n"
            db.session.commit()

    # 2. AI CHAT REWARDS (Controlled)
    def handle_customer_ai_chat(self, phone_number, message, conversation, user):
        
        # 1. CHECK LIMITS (Don't let them bankrupt you)
        if not self.check_ai_limits(user):
            self.whatsapp.send_text_message(phone_number, "⏳ You've reached your daily AI chat limit. Please try again tomorrow!")
            return

        # 2. GIVE REWARDS (Your existing logic, slightly cleaned up)
        now = datetime.utcnow()
        if user.last_ai_reward and user.last_ai_reward.date() < now.date():
             user.ai_points_today = 0
             
        time_since_last = (now - (user.last_ai_reward or datetime.min)).total_seconds() / 60
        
        # Reward specific logic
        reward_msg = ""
        if time_since_last >= 5 and user.ai_points_today < 2000:
             user.points += 1000
             user.ai_points_today += 1000
             user.last_ai_reward = now
             reward_msg = " (💰 +1,000 Pts)"
             db.session.commit()

        # 3. FETCH PRODUCTS (Feed the AI context)
        # We grab the last 15 approved items so the AI knows what is for sale.
        recent_promos = Promo.query.filter_by(status=PromoStatus.APPROVED).order_by(Promo.created_at.desc()).limit(15).all()
        
        products_context = "CURRENT INVENTORY:\n"
        if not recent_promos:
            products_context += "No items currently in stock."
        else:
            for p in recent_promos:
                # Format: "- iPhone 12: N300,000 (Sold by TechGuy)"
                products_context += f"- {p.title} ({p.category}): ₦{p.price:,.0f} by {p.vendor.business_name}\n"

        # 4. CALL THE BRAIN (OpenAI)
        try:
            # We send the User's Name, Memory, Message, and the Product List
            ai_response = self.openai.smart_chat(
                user_name=user.name,
                user_memory=user.ai_memory or "",
                user_message=message,
                product_data=products_context
            )
            
            # Extract the reply and the new fact
            reply_text = ai_response.get('reply', "I'm having trouble connecting to the brain. Try again?")
            new_fact = ai_response.get('new_fact')

            # 5. SAVE MEMORY (Make the bot smarter)
            if new_fact:
                current_mem = user.ai_memory or ""
                # Append new fact (e.g., "Likes red shoes")
                user.ai_memory = f"{current_mem}; {new_fact}".strip('; ')
            
            # 6. UPDATE USAGE STATS
            user.daily_ai_count += 1
            user.last_ai_usage = now
            db.session.commit()

            # 7. SEND REPLY (Combine AI text + Reward notification)
            final_msg = f"{reply_text}{reward_msg}"
            self.whatsapp.send_text_message(phone_number, final_msg)

        except Exception as e:
            print(f"AI Chat Error: {e}")
            self.whatsapp.send_text_message(phone_number, "⚠️ My AI brain is offline momentarily. Please try 'Menu' to browse manually.")

        if user.is_vendor and user.is_subscriber:
            msg = f"Hi {user.name or 'there'}! 👋\n{checkin_msg}\nWhich dashboard would you like to access?"
            conversation.state = "SELECT_DASHBOARD"
            buttons = ["Vendor Dashboard", "Customer Dashboard"]
            self.whatsapp.send_button_message(phone_number, msg, buttons)
        elif user.is_vendor:
            conversation.state = "VENDOR_MENU"
            self.show_vendor_menu(phone_number)
        elif user.is_subscriber:
            msg = f"Hi {user.name or 'there'}! 👋\n{checkin_msg}\nWelcome to your dashboard."
            self.whatsapp.send_text_message(phone_number, msg)
            conversation.state = "CUSTOMER_MENU"
            self.send_customer_menu(phone_number)
        else:
            conversation.state = "WELCOME"
            self.send_welcome_message(phone_number, user)
        
        db.session.commit()

    def handle_dashboard_selection(self, phone_number, message, conversation, user):
        if "vendor" in message.lower() or message == "btn_0":
            user.current_mode = "vendor"
            conversation.state = "VENDOR_MENU"
            db.session.commit()
            self.show_vendor_menu(phone_number)

        elif "customer" in message.lower() or message == "btn_1":
            user.current_mode = "subscriber"
            if not user.interests:
                conversation.state = "CUSTOMER_GENDER"
                db.session.commit()
                buttons = ["Male", "Female"]
                self.whatsapp.send_button_message(phone_number, "Welcome! Step 1: Select your gender:", buttons)
            else:
                conversation.state = "CUSTOMER_MENU"
                db.session.commit()
                self.send_customer_menu(phone_number)

    def send_welcome_message(self, phone_number, user):
        buttons = ["Vendor", "Customer"]
        self.whatsapp.send_button_message(phone_number, "👋 Welcome to EasyEasy!\n\nRegister as:", buttons)

    def handle_role_selection(self, phone_number, message, conversation, user):
        msg_lower = message.lower()
        
        # --- CHECK BACK BUTTON ---
        if "back" in msg_lower:
             self.handle_global_entry(phone_number, user, conversation)
             return

        # --- BLOCK A: VENDOR CHECK ---
        # Note: We check for "btn_0" (Standard Vendor Button)
        if "vendor" in msg_lower or "become" in msg_lower or message == "btn_0":
            
            # 1. Check if user is ALREADY a vendor (Always let them in)
            if user.is_vendor:
                conversation.state = "VENDOR_MENU"
                db.session.commit()
                self.show_vendor_menu(phone_number)
                return
            
            # 2. Check Database Setting for "Lock"
            lock_setting = SystemSetting.query.get('vendor_lock')
            is_locked = lock_setting.value == 'true' if lock_setting else False
            
            if is_locked:
                # LOCKED: Show the "Sorry" message
                msg = "🚫 Sorry, Vendor Registration is currently CLOSED by the admin.\n\nYou can still register as a customer to buy items!"
                buttons = ["Register as Customer"]
                # FIX: Send a CUSTOM ID 'btn_force_customer' so it doesn't clash with btn_0
                self.whatsapp.send_button_message(phone_number, msg, buttons, button_ids=["btn_force_customer"])
                return
            else:
                # UNLOCKED: Start Registration
                conversation.state = "VENDOR_NAME"
                db.session.commit()
                self.whatsapp.send_text_message(phone_number, "Let's create your Vendor Profile! 🏪\n\nWhat is your Business Name?")
                return

        # --- BLOCK B: CUSTOMER CHECK ---
        # FIX: Added 'btn_force_customer' to this check
        elif "customer" in msg_lower or message == "btn_1" or message == "btn_force_customer":
            user.current_mode = "subscriber"
            conversation.state = "CUSTOMER_NAME"
            db.session.commit()
            self.whatsapp.send_text_message(phone_number, "Let's create your Customer Profile.\n\nWhat is your Full Name?")
        
        # --- VENDOR REGISTRATION ---
    def handle_vendor_name(self, phone_number, message, conversation, user):
        user.name = message.strip()
    
        if not user.referral_code:
            code_base = user.name[:3].upper().replace(" ", "X")
            user.referral_code = f"{code_base}{random.randint(100,999)}"
        
        conversation.state = "VENDOR_BUSINESS"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, f"Nice to meet you, {user.name}! 👋\n\nWhat's your business name?")

    def handle_vendor_business(self, phone_number, message, conversation, user):
        user.business_name = message.strip()
        conversation.state = "VENDOR_DESC"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, "Describe your business in one sentence (e.g. 'We sell affordable sneakers').")

    def handle_vendor_desc(self, phone_number, message, conversation, user):
        user.business_description = message.strip()
        
        # NEW: Redirect to Verification instead of menu
        conversation.state = "VENDOR_VERIFICATION"
        db.session.commit()
        
        msg = (
            "🔒 *Verification Required*\n\n"
            "To prevent fraud and ensure a safe marketplace, all vendors must verify their identity.\n\n"
            "Please upload a photo or PDF of one of the following (dated within last 6 months):\n"
            "• NIN Slip\n"
            "• Utility Bill\n"
            "• Bank Statement\n\n"
            "📎 *Reply by uploading the document now.*"
        )
        self.whatsapp.send_text_message(phone_number, msg)

    def show_vendor_menu(self, phone_number):
        sections = [{
            "title": "Vendor Options",
            "rows": [
                {"id": "upload_product", "title": "Upload Products"},
                {"id": "run_promo", "title": "Run Promotion"},
                {"id": "profile", "title": "Profile"},
                {"id": "promo_status", "title": "View Promotion Status"},
                {"id": "switch_customer", "title": "Switch to Customer"},
                {"id": "support", "title": "Support"}
            ]
        }]
        self.whatsapp.send_list_message(phone_number, "Vendor Dashboard", "Open Options", sections)

    def handle_vendor_menu(self, phone_number, message, conversation, user):
        msg_id = message.lower().strip()
        
        # --- FIX: HANDLE REJECTED VENDORS ---
        if msg_id in ["upload_product", "run_promo", "1", "2"]:
            
            if user.verification_status == "rejected":
                 self.whatsapp.send_text_message(phone_number, "❌ Your previous verification document was rejected.\n\nBut don't worry! You can try again.\n\n📎 *Please upload a new valid ID or Utility Bill now.*")
                 conversation.state = "VENDOR_VERIFICATION"
                 db.session.commit()
                 return

            if user.verification_status != "verified":
                 self.whatsapp.send_text_message(phone_number, f"⚠️ Your account status is: *{user.verification_status.upper()}*.\n\nPlease wait for admin approval before posting ads.")
                 return

            conversation.state = "PROMO_TITLE"
            conversation.context = json.dumps({})
            db.session.commit()
            intro_text = "🚀 *New Promotion*\n\nLet's get your product seen!\n\nFirst, please reply with the Title of your product."
            self.whatsapp.send_text_message(phone_number, intro_text)
            return

        
        elif msg_id == "profile":
            txt = (
                f"👤 *Vendor Profile*\n\n"
                f"🏪 *Business:* {user.business_name}\n"
                f"📛 *Owner:* {user.name}\n"
                f"🔐 *Status:* {user.verification_status.upper()}\n"
                f"📱 *Phone:* {user.phone_number}\n"
                f"💎 *Points:* {user.points}\n"
                f"📅 *Joined:* {user.created_at.strftime('%Y-%m-%d')}"
            )
            self.whatsapp.send_text_message(phone_number, txt)
            self.show_vendor_menu(phone_number)
            
        elif msg_id == "promo_status":
            promos = Promo.query.filter_by(vendor_id=user.id).order_by(Promo.created_at.desc()).limit(5).all()
            if not promos:
                self.whatsapp.send_text_message(phone_number, "📂 You haven't uploaded any products yet.")
            else:
                response = "📊 *Your Recent Promotions:*\n"
                for p in promos:
                    status_text = "✅ Accepted" if p.status in [PromoStatus.BROADCASTED, PromoStatus.APPROVED] else "❌ Rejected" if p.status == PromoStatus.REJECTED else "🕒 In Review"
                    response += f"\n📦 *{p.title}*\nStatus: {status_text}\n"
                self.whatsapp.send_text_message(phone_number, response)
            self.show_vendor_menu(phone_number)
        
        elif msg_id == "switch_customer":
            user.current_mode = "subscriber"
            if not user.interests:
                conversation.state = "CUSTOMER_GENDER"
                db.session.commit()
                buttons = ["Male", "Female"]
                self.whatsapp.send_button_message(phone_number, "Welcome to Customer View! Step 1: Select your gender:", buttons)
            else:
                conversation.state = "CUSTOMER_MENU"
                db.session.commit()
                self.whatsapp.send_text_message(phone_number, "🔄 Switching to Customer Mode...")
                self.send_customer_menu(phone_number)

        elif msg_id == "support":
            txt = (
                "🛠️ *Vendor Support*\n\n"
                "Need help with your ads? Contact us:\n"
                "📧 Email: support@easyeasy.app\n"
                "📞 WhatsApp: +234 800 000 0000"
            )
            self.whatsapp.send_text_message(phone_number, txt)
            
            self.whatsapp.send_text_message(phone_number, "👇 Or type your message/complaint below and we will receive it instantly:")
            
            conversation.state = "SUPPORT_MESSAGE"
            db.session.commit()

        else:
            self.show_vendor_menu(phone_number)

    def handle_support_message(self, phone_number, message, conversation, user):
        # Create ticket
        ticket = SupportTicket(
            user_id=user.id,
            message=message.strip(),
            status="open"
        )
        db.session.add(ticket)
        
        # Ack and return to menu
        if user.is_vendor and user.current_mode == "vendor":
            conversation.state = "VENDOR_MENU"
            self.whatsapp.send_text_message(phone_number, "✅ Complaint received! We will reach out to you shortly.")
            db.session.commit()
            self.show_vendor_menu(phone_number)
        else:
            conversation.state = "CUSTOMER_MENU"
            self.whatsapp.send_text_message(phone_number, "✅ Complaint received! We will reach out to you shortly.")
            db.session.commit()
            self.send_customer_menu(phone_number)

    # --- AD CREATION FLOW ---
    def handle_promo_title(self, phone_number, message, conversation):
        context = json.loads(conversation.context or "{}")
        context['title'] = message.strip()
        conversation.context = json.dumps(context)
        conversation.state = "PROMO_DESCRIPTION"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, "Great! Now describe your product.")

    def handle_promo_description(self, phone_number, message, conversation):
        context = json.loads(conversation.context or "{}")
        context['description'] = message.strip()
        conversation.context = json.dumps(context)
       
        conversation.state = "PROMO_CATEGORY"
        db.session.commit()
        
        msg = (
            "Select Categories for this ad (Reply e.g. 1, 3):\n"
            "1. Business\n2. Fashion\n3. Food\n4. Campus\n5. Jobs\n"
            "6. Tech\n7. Entertainment\n8. Real Estate\n9. Health\n10. Education"
        )
        self.whatsapp.send_text_message(phone_number, msg)

    def handle_promo_category(self, phone_number, message, conversation):
        # Handle Multi-Category
        raw_input = message.replace(" ", "").split(",")
        mapping = self.get_interest_map()
        selected_cats = []
        
        for item in raw_input:
            if item in mapping:
                selected_cats.append(mapping[item])
            elif item.lower() in [v.lower() for v in mapping.values()]:
                selected_cats.append(item.title())
        
        final_category_string = ", ".join(selected_cats) if selected_cats else "General"
        
        context = json.loads(conversation.context or "{}")
        context['category'] = final_category_string
        conversation.context = json.dumps(context)
        
        conversation.state = "PROMO_TARGET_GENDER"
        db.session.commit()
        buttons = ["All", "Male", "Female"]
        self.whatsapp.send_button_message(phone_number, "Who is this ad for?", buttons)

    def handle_promo_target_gender(self, phone_number, message, conversation):
        gender = message.strip().capitalize()
        if gender not in ["All", "Male", "Female"]:
            gender = "All"

        context = json.loads(conversation.context or "{}")
        context['target_gender'] = gender
        conversation.context = json.dumps(context)
        
        conversation.state = "PROMO_PRICE"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, "What's the price? (e.g. 5000, Negotiable or free)")

    def handle_promo_price(self, phone_number, message, conversation):
        context = json.loads(conversation.context or "{}")
        try:
            val = message.strip().lower()
            if val in ['free', '0', 'negotiable']:
                context['price'] = 0
                context['is_negotiable'] = True if val == 'negotiable' else False
            else:
                context['price'] = float(val.replace(',', '').replace('₦', ''))
                context['is_negotiable'] = False
        except:
            self.whatsapp.send_text_message(phone_number, "Invalid price format. Please send a number, 'Free', or 'Negotiable'.")
            return
        conversation.context = json.dumps(context)
        conversation.state = "PROMO_CONTACT"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, "How should customers contact you?")

    def handle_promo_contact(self, phone_number, message, conversation):
        context = json.loads(conversation.context or "{}")
        context['contact_info'] = message.strip()
        
        conversation.context = json.dumps(context)
        conversation.state = "PROMO_MEDIA" 
        db.session.commit()
        
        # Ask for media
        self.whatsapp.send_text_message(phone_number, "Please upload an image or video of your product 📸 (or type 'Skip' to use text only).")

    def handle_promo_media(self, phone_number, message, conversation, user):
        """Handles text input during the media upload state (e.g. 'Skip')"""
        msg_lower = message.lower().strip()
        
        if msg_lower == "skip":
            self.finalize_promo_creation(phone_number, conversation, user)
        else:
            self.whatsapp.send_text_message(phone_number, "⚠️ Please upload an image/video or type 'Skip' to proceed without media.")

    def finalize_promo_creation(self, phone_number, conversation, user):
        context = json.loads(conversation.context or "{}")
        
        self.whatsapp.send_text_message(phone_number, "✨ Generating the perfect ad caption for you... please wait.")
        
        ai_caption = self.openai.generate_ad_caption(
            title=context.get('title'),
            description=context.get('description'),
            price=context.get('price'),
            business_name=user.business_name
        )
        
        context['ai_caption'] = ai_caption
        conversation.context = json.dumps(context)
        conversation.state = "PROMO_REVIEW_AI"
        db.session.commit()

        msg = f"📝 *Draft Caption:*\n\n{ai_caption}\n\n🤖 *AI Assistant:* Do you like this vibe? You can reply 'Yes' to proceed, or tell me how to change it."
        self.whatsapp.send_text_message(phone_number, msg)
        
    def handle_promo_ai_review(self, phone_number, message, conversation, user):
        msg_lower = message.lower().strip()
        context = json.loads(conversation.context or "{}")

        if msg_lower in ['yes', 'ok', 'okay', 'good', 'i like it', 'proceed', 'next']:
            conversation.state = "PROMO_TYPE"
            db.session.commit()
            buttons = ["Paid Promotion", "Free Promotion"]
            self.whatsapp.send_button_message(phone_number, "Great! Now choose your promotion type:", buttons)
            return

        if not self.check_ai_limits(user):
             self.whatsapp.send_text_message(phone_number, "⚠️ You have reached your AI edit limit for today. We will proceed with the current caption.")
             conversation.state = "PROMO_TYPE"
             db.session.commit()
             buttons = ["Paid Promotion", "Free Promotion"]
             self.whatsapp.send_button_message(phone_number, "Choose promotion type:", buttons)
             return

        self.whatsapp.send_text_message(phone_number, "✨ Refining your ad based on your feedback...")
        
        current_caption = context.get('ai_caption', '')
        new_caption = self.openai.generate_ad_caption(
            title=context.get('title'),
            description=context.get('description'),
            price=context.get('price'),
            business_name=user.business_name,
            instruction=f"Refine this caption based on this feedback: {message}. Previous draft: {current_caption}"
        )
        
        context['ai_caption'] = new_caption
        conversation.context = json.dumps(context)
        user.daily_ai_count += 1
        user.last_ai_usage = datetime.utcnow()
        db.session.commit()

        msg = f"📝 *New Draft:*\n\n{new_caption}\n\n----------------\n🤖 *AI Assistant:* Better? Reply 'Yes' to proceed, or give more feedback."
        self.whatsapp.send_text_message(phone_number, msg)

    def handle_promo_type_selection(self, phone_number, message, conversation, user):
        msg = message.lower()
        if "paid" in msg or message == "btn_0":
             conversation.state = "PAID_IMPRESSIONS"
             self.whatsapp.send_text_message(phone_number, "How many people do you want to reach? (Minimum 500)")
        elif "free" in msg or message == "btn_1":
             if user.free_trials_used >= 2:
                 self.whatsapp.send_text_message(phone_number, "❌ You have used all 2 free trials. Please choose Paid.")
                 return
             conversation.state = "FREE_TASKS_SOCIAL"
             msg = (
                    "Step 1: Follow all our platforms to qualify:\n\n"
                    f"Instagram: {os.getenv('LINK_INSTAGRAM', '#')}\n"
                    f"TikTok: {os.getenv('LINK_TIKTOK', '#')}\n"
                    f"Facebook: {os.getenv('LINK_FACEBOOK', '#')}"
                )
             buttons = ["I have followed all"]
             self.whatsapp.send_button_message(phone_number, msg, buttons)
        db.session.commit()

    def handle_paid_impressions(self, phone_number, message, conversation, user):
        try:
            impressions = int(message.strip())
        except:
            self.whatsapp.send_text_message(phone_number, "Please enter a valid number (e.g. 1000).")
            return
        if impressions < 500:
             self.whatsapp.send_text_message(phone_number, "Minimum impressions is 500. Please try again.")
             return
        
        base_amount = impressions * 10
        service_fee = base_amount * 0.02
        total_amount = base_amount + service_fee
        
        context = json.loads(conversation.context or "{}")
        context['target_impressions'] = impressions
        context['promo_type'] = 'paid'
        context['price'] = total_amount 
        
        promo = self.create_promo_from_context(user, context)
        
        ref = f"PAY-{uuid.uuid4().hex[:10]}"
        link = PAYMENT_LINK 
        
        payment = Payment(
            user_id=user.id, 
            promo_id=promo.id, 
            amount=total_amount, 
            reference=ref, 
            status=PaymentStatus.PENDING
        )
        db.session.add(payment)
        
        msg = (f"Payment\n\n"
               f"🎯 Reach: {impressions}\n"
               f"💵 Total: ₦{total_amount:,.2f} (Inc. 2% Service Fee)\n\n"
               f"Pay here: {link}\n\n"
               f"⚠️ Please ensure the payment amount entered is correct.")
        
        buttons = ["I have made payment"]
        self.whatsapp.send_button_message(phone_number, msg, buttons)
        conversation.state = "PAID_PAYMENT_CONFIRM"
        conversation.context = json.dumps(context)
        db.session.commit()

    def handle_free_socials_done(self, phone_number, conversation):
        self.whatsapp.send_text_message(phone_number, "Please drop screenshots of your follows here for review.")
        conversation.state = "FREE_TASK_SCREENSHOT_1"
        db.session.commit()

    def handle_free_screenshot_1(self, phone_number, message, conversation, user):
        # 1. Ensure they have a referral code
        if not user.referral_code:
            code_base = (user.name or "USR")[:3].upper().replace(" ", "X")
            user.referral_code = f"{code_base}{random.randint(100,999)}"
            db.session.commit()

        # 2. Generate their unique link
        bot_phone = os.getenv("PHONE_NUMBER", "2349132887028")
        ref_text = f"I want to register using referral code {user.referral_code}"
        encoded_text = urllib.parse.quote(ref_text)
        referral_link = f"https://wa.me/{bot_phone}?text={encoded_text}"
        
        # Message 1: Targets Vendors (Business Owners)
        copy_text_1 = (
            "🚀 *SECRET REVEALED: How to Sell Out Your Market Without Stress!*\n\n"
            "Stop begging people to view your status! 🛑✋\n"
            "There is a new AI Bot called EasyEasy that blasts your advert to THOUSANDS of active buyers automatically.\n"
            "• No posting manually.\n"
            "• No saving contacts.\n"
            "• Just upload and relax.\n\n"
            "The crazy part? It is currently FREE for early vendors. Don't say I didn't update you o!\n"
            f"Tap here to register as a Vendor now: {referral_link}"
        )
        
        # Message 2: Targets Customers (Freebies)
        copy_text_2 = (
            "😳 *Wait o, so you guys are still buying data to waste time online?* 😳\n\n"
            "I just found a cheat code. EasyEasy AI pays you just to chat and view products!\n"
            "Yes! You earn points daily which you can use to buy *Phones, Hairs, Shoes, and Food* for FREE.\n"
            "• Chat with AI = Earn Money\n"
            "• View Ads = Earn Money\n"
            "• Refer Friends = Earn Money\n\n"
            "Sapa is a choice o! Join the smart ones cashing out now.\n"
            f"Click my link to start earning: {referral_link}"
        )

        # 4. Send instructions
        self.whatsapp.send_text_message(phone_number, "✅ Screenshot received! Now for the final step.")
        self.whatsapp.send_text_message(phone_number, "You need 10 referrals to unlock your Free Ad. Share these posts to your Status and Groups! 👇")
        
        self.whatsapp.send_text_message(phone_number, "--- COPY POST 1 (For Business Owners) ---")
        self.whatsapp.send_text_message(phone_number, copy_text_1)
        
        self.whatsapp.send_text_message(phone_number, "--- COPY POST 2 (For Everyone Else) ---")
        self.whatsapp.send_text_message(phone_number, copy_text_2)
        
        self.whatsapp.send_text_message(phone_number, "📸 Drop screenshots of your shared posts here to finish!")
        
        # 5. Move state forward
        conversation.state = "FREE_TASK_SCREENSHOT_2"
        db.session.commit()

    def handle_free_screenshot_2(self, phone_number, message, conversation, user):
        user.free_trials_used += 1
        trials_left = 2 - user.free_trials_used
        
        context = json.loads(conversation.context or "{}")
        self.create_promo_from_context(user, context)
        
        vendor_link = os.getenv('LINK_VENDOR_COMMUNITY', '#')
        msg = f"Application submitted! You have {trials_left} free trials left.\n\nJoin the Vendor Community to get your ad approved!\n\nVENDOR: {vendor_link}"
        
        buttons = ["I have joined"]
        self.whatsapp.send_button_message(phone_number, msg, buttons)
        conversation.state = "VENDOR_JOIN_COMMUNITY"
        db.session.commit()

    def handle_vendor_code_verification(self, phone_number, message, conversation, user):
        code = message.strip().upper()
        if code == COMMUNITY_CODE:
            self.whatsapp.send_text_message(phone_number, "✅ Code Verified! Your ad is already under review.")
            conversation.state = "VENDOR_MENU"
            db.session.commit()
            self.show_vendor_menu(phone_number)
        else:
            self.whatsapp.send_text_message(phone_number, "❌ Incorrect code. Please check the vendor group and try again.")

    def create_promo_from_context(self, user, context):
        final_caption = context.get('ai_caption')
        if not final_caption:
            final_caption = self.openai.generate_ad_caption(
                title=context.get('title'),
                description=context.get('description'),
                price=context.get('price'),
                business_name=user.business_name
            )
            
        promo = Promo(
            vendor_id=user.id,
            title=context.get('title', ''),
            description=context.get('description', ''),
            price=context.get('price', 0),
            contact_info=context.get('contact_info', ''),
            media_url=context.get('media_url', ''),
            media_type=context.get('media_type', 'image'),
            promo_type=context.get('promo_type', 'free'),
            target_impressions=context.get('target_impressions', 0),
            total_price=context.get('price', 0),
            ai_generated_caption=final_caption,
            category=context.get('category', 'General'), 
            target_gender=context.get('target_gender', 'All'),
            status=PromoStatus.PENDING
        )
        db.session.add(promo)
        db.session.commit()
        return promo

    # ---------------------------------------------------------
    # CUSTOMER FLOWS
    # ---------------------------------------------------------
    def handle_customer_name(self, phone_number, message, conversation, user):
        # FIX 2: Correct logic and indentation for Name & Referral Code
        # 1. Capture the name first!
        user.name = message.strip()
        
        # 2. Generate Referral Code 
        if not user.referral_code:
            clean_name = "".join(e for e in user.name if e.isalnum())
            base = (clean_name[:3] if len(clean_name) >= 3 else "USR").upper()
            
            unique = False
            while not unique:
                # Increased range to 1000-9999 for less collision
                rand_suffix = random.randint(1000, 9999) 
                new_code = f"{base}{rand_suffix}"
                
                # Check if this code exists
                existing = User.query.filter_by(referral_code=new_code).first()
                if not existing:
                    user.referral_code = new_code
                    unique = True
        
        # 3. Move to next state
        conversation.state = "CUSTOMER_GENDER"
        db.session.commit()
        buttons = ["Male", "Female"]
        self.whatsapp.send_button_message(phone_number, "Please select your gender:", buttons)

    def handle_customer_gender(self, phone_number, message, conversation, user):
        gender = message.strip().capitalize()
        if gender not in ["Male", "Female"]:
            gender = "All"
        
        user.gender = gender
        conversation.state = "CUSTOMER_INTERESTS"
        db.session.commit()
        
        msg = "Pick interests (Reply e.g., 1,3):\n1. Business\n2. Fashion\n3. Food\n4. Campus\n5. Jobs\n6. Tech\n7. Entertainment\n8. Real Estate\n9. Health\n10. Education"
        self.whatsapp.send_text_message(phone_number, msg)

    def handle_customer_interests(self, phone_number, message, conversation, user):
        raw_input = message.replace(" ", "").split(",")
        mapping = self.get_interest_map()
        selected_interests = []
        
        for item in raw_input:
            if item in mapping:
                selected_interests.append(mapping[item])
            elif item.lower() in [v.lower() for v in mapping.values()]:
                selected_interests.append(item.title())
        
        if selected_interests:
            user.interests = ", ".join(selected_interests)
        else:
            user.interests = message.strip()
            
        conversation.state = "CUSTOMER_REFERRAL"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, "Do you have a referral code? Type it or 'No'.")

    def handle_customer_referral(self, phone_number, message, conversation, user):
        if message.lower() != 'no':
            referrer = User.query.filter_by(referral_code=message.strip()).first()
            if referrer:
                user.referred_by_id = referrer.id
                referrer.points += 15
        conversation.state = "CUSTOMER_COMMUNITY_TASK"
        db.session.commit()
        user_link = os.getenv('LINK_USER_COMMUNITY', '#')
        msg = f"Join the customer community for updates and instantly earn 50 points! 🚀\n\nUSER: {user_link}\n\nClick 'I have joined' when done."
        buttons = ["I have joined"]
        self.whatsapp.send_button_message(phone_number, msg, buttons)

    def prompt_community_code(self, phone_number, conversation):
        conversation.state = "CUSTOMER_COMMUNITY_CODE"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, "🔐 Please enter the secret code found in our admin channel to verify:")

    def handle_community_code_verification(self, phone_number, message, conversation, user):
        code = message.strip().upper()
        if code == COMMUNITY_CODE:
            if not user.community_task_done:
                user.points += 50
                user.community_task_done = True
                db.session.commit()
                self.whatsapp.send_text_message(phone_number, "✅ Correct Code! 🎉 +50 Points Added!")
            else:
                self.whatsapp.send_text_message(phone_number, "✅ Code Verified.")
            user.is_subscriber = True 
            conversation.state = "CUSTOMER_MENU"
            db.session.commit()
            self.send_customer_menu(phone_number)
        else:
            self.whatsapp.send_text_message(phone_number, "❌ Incorrect code.")

    def send_customer_menu(self, phone_number):
        sections = [{
            "title": "Menu",
            "rows": [
                {"id": "earn", "title": "How to earn"},
                {"id": "status", "title": "Account status"},
                {"id": "update_interests", "title": "Update Interests"},
                {"id": "support", "title": "Support"},
                {"id": "unsub", "title": "Subscribe/Unsub"},
                {"id": "redeem", "title": "Redeem Points"},     
                {"id": "join_socials", "title": "Social Media"}
            ]
        }]
        user = User.query.filter_by(phone_number=phone_number).first()
        if user.is_vendor:
             sections[0]["rows"].append({"id": "switch_vendor", "title": "🔄 Switch to Vendor"})
        else:
             sections[0]["rows"].append({"id": "become_vendor", "title": "🆕 Become a Vendor"})
        
        body_text = "Customer Dashboard\n\n💡 Tip: You can also type any question to ask our AI Assistant about products!"
        button_text = "Open Menu"
        
        self.whatsapp.send_list_message(phone_number, body_text, button_text, sections)

    def handle_customer_menu(self, phone_number, message, conversation, user):
        # FIX 5: Defined 'msg' at the top to avoid UnboundLocalError
        msg = message.lower()
        
        if "earn" in msg:
             txt = (
                "💰 *THE EASYEASY WEALTH PLAN*\n\n"
                "💸 *HOW TO EARN*\n"
                "✅ *Daily Check-in:* 500 Pts (₦50)\n"
                "✅ *Chat with AI:* 1,000 Pts (₦100)\n"
                "✅ *Refer Friends:* 1,500 Pts (₦150)\n"
                "✅ *Patronize Vendors:* 5,000 Pts (₦500)\n\n"
                "🔓 *CASH OUT RULES*\n"
                "• Target: 100,000 Points (₦10,000)\n"
                "• First Cashout: Unconditional!\n"
                "• Patronize 5 Vendors/month to unlock."
             )
             self.whatsapp.send_text_message(phone_number, txt)
             self.send_customer_menu(phone_number)

        elif "status" in msg:
             pts = user.points if user.points else 0.0
             ref_count = len(user.referrals) if user.referrals else 0
             code = user.referral_code if user.referral_code else "None"
             txt = (
                f"📊 Status\n\n"
                f"Points: {pts}\n"
                f"Referrals: {ref_count}\n"
                f"Your Code: {code}\n"
                f"Gender: {user.gender}\n"
                f"Interests: {user.interests}"
             )
             self.whatsapp.send_text_message(phone_number, txt)
             self.send_customer_menu(phone_number) 

        elif "update" in msg or "interest" in msg:
             msg = (
                "Update Mode: Select *ADDITIONAL* interests to add to your list (Reply e.g., 1,3):\n"
                "1. Business\n"
                "2. Fashion\n"
                "3. Food\n"
                "4. Campus\n"
                "5. Jobs\n"
                "6. Tech\n"
                "7. Entertainment\n"
                "8. Real Estate\n"
                "9. Health\n"
                "10. Education"
             )
             self.whatsapp.send_text_message(phone_number, msg)
             conversation.state = "CUSTOMER_UPDATE_INTERESTS"
             db.session.commit()
        
        elif "redeem" in msg:
             if user.points >= 100000:
                 self.whatsapp.send_text_message(phone_number, f"🎉 You have {user.points} points! Please contact support to redeem.")
             else:
                 self.whatsapp.send_text_message(phone_number, f"❌ You need at least 100,000 points to redeem. You currently have {user.points}.")
             self.send_customer_menu(phone_number)
        
        elif "join" in msg and "social" in msg:
             txt = (
                 "📱 *Join our Social Media Community:*\n\n"
                 f"Facebook: {os.getenv('LINK_FACEBOOK', '#')}\n"
                 f"TikTok: {os.getenv('LINK_TIKTOK', '#')}\n"
                 f"Instagram: {os.getenv('LINK_INSTAGRAM', '#')}\n"
             )
             self.whatsapp.send_text_message(phone_number, txt)
             self.send_customer_menu(phone_number)

        elif "support" in msg:
             txt = (
                "🛠️ *Customer Support*\n\n"
                "Need help with your ads? Contact us:\n"
                "📧 Email: support@easyeasy.app\n"
                "📞 WhatsApp: +234 913 288 7028"
            )
             self.whatsapp.send_text_message(phone_number, txt)
             
             # 2. ASK FOR TICKET
             self.whatsapp.send_text_message(phone_number, "👇 Or type your message/complaint below and we will receive it instantly:")
             conversation.state = "SUPPORT_MESSAGE"
             db.session.commit()

        elif "subscribe" in msg or "unsub" in msg:

             if user.is_active:
                 user.is_active = False
                 txt = "❌ You have been unsubscribed from updates."
             else:
                 user.is_active = True
                 txt = "✅ You have been subscribed to updates!"
             
             db.session.commit()
             self.whatsapp.send_text_message(phone_number, txt)
             self.send_customer_menu(phone_number)
        
        elif "switch" in msg or "become" in msg or "vendor" in msg:
             
             # 1. STRICT CHECK: Only bypass lock if they are ALREADY a verified/pending vendor
             # If they are just a "user" who clicked vendor once before, we still want to block them if locked.
             if user.is_vendor and user.business_name:
                 user.current_mode = "vendor"
                 conversation.state = "VENDOR_MENU"
                 db.session.commit()
                 self.show_vendor_menu(phone_number)
                 return

             # 2. If they are NOT a fully set up vendor, apply the LOCK.
             lock_setting = SystemSetting.query.get('vendor_lock')
             is_locked = lock_setting.value == 'true' if lock_setting else False
             
             if is_locked:
                 msg = "🚫 Sorry, we are not accepting new Vendors at the moment.\n\nPlease continue enjoying our services as a customer!"
                 self.whatsapp.send_text_message(phone_number, msg)
                 # Re-send customer menu so they aren't stuck
                 self.send_customer_menu(phone_number)
             else:
                 # UNLOCKED: Start Registration
                 conversation.state = "VENDOR_NAME"
                 db.session.commit()
                 self.whatsapp.send_text_message(phone_number, "Let's create your Vendor Profile! 🏪\n\nWhat is your Business Name?")

    def handle_update_interests(self, phone_number, message, conversation, user):
        new_interest = message.strip()
        current = user.interests or ""
        user.interests = f"{current}, {new_interest}" if current else new_interest
        conversation.state = "CUSTOMER_MENU"
        db.session.commit()
        self.whatsapp.send_text_message(phone_number, f"✅ Interests updated! List: {user.interests}")
        self.send_customer_menu(phone_number)

    def handle_customer_buy_intent(self, phone_number, promo_id_str, user):
        """Called when user clicks 'Contact Vendor' on an ad"""
        try:
            promo_id = int(promo_id_str)
            promo = Promo.query.get(promo_id)
            if not promo:
                self.whatsapp.send_text_message(phone_number, "⚠️ Item not found.")
                return

            vendor = promo.vendor
            
            # 1. Create a Pending Order Record
            order = Order(
                buyer_id=user.id,
                vendor_id=vendor.id,
                promo_id=promo.id,
                amount=promo.price,
                status=OrderStatus.PENDING
            )
            db.session.add(order)
            db.session.commit()
            
            # 2. Send Contact Details to Buyer
            msg_to_buyer = (
                f"🛍️ *Contact Details for {promo.title}*\n\n"
                f"📞 Vendor Phone: {vendor.phone_number}\n"
                f"📝 Contact Info: {promo.contact_info}\n\n"
                f"👉 Please chat with the vendor to finalize payment and delivery.\n"
                f"⚠️ *Important:* Remind the vendor to click 'Confirm Sale' in their bot menu after you pay. That is the ONLY way you get your 5,000 Points!"
            )
            self.whatsapp.send_text_message(phone_number, msg_to_buyer)
            
            # 3. Send Alert to Vendor with CONFIRM Button
            msg_to_vendor = (
                f"🔔 *New Order Request!*\n\n"
                f"👤 Customer: {user.name} ({user.phone_number})\n"
                f"📦 Item: {promo.title}\n"
                f"💰 Price: ₦{promo.price:,.2f}\n\n"
                f"The customer has been given your contact details.\n"
                f"👉 Once you have received payment and delivered the item, CLICK the button below to confirm the sale and reward the customer."
            )
            # Create a unique ID for the button: "confirm_order_[order_id]"
            self.whatsapp.send_button_message(vendor.phone_number, msg_to_vendor, ["Confirm Sale"], button_ids=[f"confirm_order_{order.id}"])
            
        except Exception as e:
            print(f"Error in buy intent: {e}")
            self.whatsapp.send_text_message(phone_number, "❌ Error processing request.")

    def handle_vendor_confirm_sale(self, phone_number, order_id_str):
        """Called when Vendor clicks 'Confirm Sale'"""
        try:
            order_id = int(order_id_str)
            order = Order.query.get(order_id)
            
            if not order:
                self.whatsapp.send_text_message(phone_number, "⚠️ Order not found.")
                return
            
            if order.status == OrderStatus.CONFIRMED:
                self.whatsapp.send_text_message(phone_number, "✅ This order was already confirmed.")
                return
                
            # Execute Confirmation
            order.status = OrderStatus.CONFIRMED
            
            # Reward Buyer
            buyer = order.buyer
            buyer.points += 5000 
            buyer.vendors_patronized_month += 1 
            
            db.session.commit()
            
            # Success Messages
            self.whatsapp.send_text_message(phone_number, f"✅ Sale Confirmed! We have rewarded {buyer.name} with 5,000 Points.")
            
            self.whatsapp.send_text_message(buyer.phone_number, (
                f"🎉 *Purchase Verified!*\n\n"
                f"The vendor has confirmed your purchase of '{order.promo_id}'.\n"
                f"💰 *+5,000 Points Added!*\n"
                f"📊 Monthly Progress: You have patronized {buyer.vendors_patronized_month}/5 vendors."
            ))

        except Exception as e:
            print(f"Error confirming sale: {e}")

    # ... (Utils) ...
    def handle_button_reply(self, phone_number: str, button_id: str):
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.session.add(user)
            db.session.commit()

        if button_id.startswith("buy_promo_"):
            promo_id = button_id.split("_")[2]
            self.handle_customer_buy_intent(phone_number, promo_id, user)
            return
            
        if button_id.startswith("confirm_order_"):
            order_id = button_id.split("_")[2]
            self.handle_vendor_confirm_sale(phone_number, order_id)
            return
        
        conversation = Conversation.query.filter_by(phone_number=phone_number).first()
        if not conversation:
            conversation = Conversation(phone_number=phone_number, state="WELCOME", context="{}")
            db.session.add(conversation)
            db.session.commit()

        state = conversation.state

        if state == "WELCOME":
            if button_id == "btn_0": self.handle_role_selection(phone_number, "btn_0", conversation, user)
            elif button_id == "btn_1": self.handle_role_selection(phone_number, "btn_1", conversation, user)
        elif state == "SELECT_DASHBOARD":
            self.handle_dashboard_selection(phone_number, button_id, conversation, user)
        elif state == "PROMO_TYPE":
            if button_id == "btn_0": self.handle_promo_type_selection(phone_number, "btn_0", conversation, user)
            elif button_id == "btn_1": self.handle_promo_type_selection(phone_number, "btn_1", conversation, user)
        elif state == "PAID_PAYMENT_CONFIRM":
             vendor_link = os.getenv('LINK_VENDOR_COMMUNITY', '#')
             msg = f"Payment Notified! Join the Vendor Community to proceed:\n\nVENDOR: {vendor_link}"
             self.whatsapp.send_button_message(phone_number, msg, ["I have joined"])
             conversation.state = "VENDOR_JOIN_COMMUNITY"
             db.session.commit()
        elif state == "VENDOR_JOIN_COMMUNITY":
             self.whatsapp.send_text_message(phone_number, "🔐 Please enter the secret code found in the Vendor Group to verify:")
             conversation.state = "VENDOR_VERIFY_CODE"
             db.session.commit()
        elif state == "FREE_TASKS_SOCIAL":
             self.handle_free_socials_done(phone_number, conversation)
        elif state == "CUSTOMER_COMMUNITY_TASK":
             self.prompt_community_code(phone_number, conversation)
        elif state == "CUSTOMER_GENDER":
             if button_id in ["btn_0", "btn_1"]: # Male/Female
                gender = "Male" if button_id == "btn_0" else "Female"
                self.handle_customer_gender(phone_number, gender, conversation, user)
        elif state == "PROMO_TARGET_GENDER":
             # All, Male, Female
             if button_id == "btn_0": gender = "All"
             elif button_id == "btn_1": gender = "Male"
             elif button_id == "btn_2": gender = "Female"
             self.handle_promo_target_gender(phone_number, gender, conversation)

    def handle_media_message(self, phone_number, media_id, media_type, caption=""):
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.session.add(user)
            db.session.commit()

        conversation = Conversation.query.filter_by(phone_number=phone_number).first()
        if not conversation: return 

        if conversation.state == "PROMO_MEDIA":
            context = json.loads(conversation.context or "{}")
            context['media_url'] = media_id 
            context['media_type'] = media_type
            conversation.context = json.dumps(context)
            db.session.commit()
            
            self.finalize_promo_creation(phone_number, conversation, user)
            
        elif conversation.state == "FREE_TASK_SCREENSHOT_1":
            self.handle_free_screenshot_1(phone_number, "", conversation, user)
        elif conversation.state == "FREE_TASK_SCREENSHOT_2":
            self.handle_free_screenshot_2(phone_number, "", conversation, user)

        # --- Vendor Verification Document ---
        elif conversation.state == "VENDOR_VERIFICATION":
            user.verification_status = "pending"
            user.verification_doc = media_id
            user.is_vendor = True 
            
            conversation.state = "VENDOR_MENU"
            db.session.commit()
            
            self.whatsapp.send_text_message(phone_number, "✅ Document Received! Your account is now Pending Approval.\n\nYou can access the menu, but ad posting is restricted until verified.")
            self.show_vendor_menu(phone_number)