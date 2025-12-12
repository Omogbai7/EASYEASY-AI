# -*- coding: utf-8 -*-
import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import SystemSetting
from models import db, User, Promo, Payment, Broadcast, Conversation, SupportTicket, PromoStatus, PaymentStatus
from bot_handler import BotHandler
from services.openai_service import OpenAIService
from sqlalchemy import text
from services.whatsapp_service import WhatsAppService
from datetime import datetime


load_dotenv()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

database_url = os.getenv('DATABASE_URL', 'sqlite:///easyeasy.db')

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

CORS(app)
db.init_app(app)

bot_handler = BotHandler()
whatsapp_service = WhatsAppService()

# Create tables
with app.app_context():
    db.create_all()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "EasyEasy WhatsApp Bot is running"}), 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """WhatsApp webhook endpoint"""

    if request.method == 'GET':
        # Webhook verification
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == verify_token:
            return str(challenge), 200
        else:
            return 'Forbidden', 403

    elif request.method == 'POST':
        # Handle incoming messages
        data = request.json

        try:
            if 'entry' in data:
                for entry in data['entry']:
                    for change in entry.get('changes', []):
                        value = change.get('value', {})

                        if 'messages' in value:
                            for message in value['messages']:
                                phone_number = message['from']
                                message_type = message['type']

                                if message_type == 'text':
                                    text = message['text']['body']
                                    bot_handler.handle_message(phone_number, text, message_type)

                                elif message_type == 'image':
                                    image_id = message['image']['id']
                                    caption = message['image'].get('caption', '')
                                    bot_handler.handle_media_message(phone_number, image_id, 'image', caption)

                                elif message_type == 'video':
                                    video_id = message['video']['id']
                                    caption = message['video'].get('caption', '')
                                    bot_handler.handle_media_message(phone_number, video_id, 'video', caption)
                                
                                # --- NEW: Handle Document Uploads (PDFs) ---
                                elif message_type == 'document':
                                    doc_id = message['document']['id']
                                    caption = message['document'].get('caption', '')
                                    bot_handler.handle_media_message(phone_number, doc_id, 'document', caption)

                                elif message_type == 'interactive':
                                    interactive_obj = message['interactive']
                                    
                                    # 1. Handle BUTTON Replies
                                    if 'button_reply' in interactive_obj:
                                        button_id = interactive_obj['button_reply']['id']
                                        bot_handler.handle_button_reply(phone_number, button_id)
                                    
                                    # 2. Handle LIST Replies
                                    elif 'list_reply' in interactive_obj:
                                        list_id = interactive_obj['list_reply']['id']
                                        bot_handler.handle_message(phone_number, list_id, 'interactive')

            return jsonify({"status": "success"}), 200

        except Exception as e:
            print("Webhook error: {}" .format(e))
            return jsonify({"status": "error", "message": str(e)}), 500

# API Routes
@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_users = User.query.count()
    total_vendors = User.query.filter_by(is_vendor=True).count()
    total_subscribers = User.query.filter_by(is_subscriber=True, is_active=True).count()
    
    total_promos = Promo.query.count()
    pending_promos = Promo.query.filter_by(status=PromoStatus.PENDING).count()
    approved_promos = Promo.query.filter_by(status=PromoStatus.APPROVED).count()
    broadcasted_promos = Promo.query.filter_by(status=PromoStatus.BROADCASTED).count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status=PaymentStatus.COMPLETED).scalar() or 0

    return jsonify({
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_subscribers': total_subscribers,
        'total_promos': total_promos,
        'pending_promos': pending_promos,
        'approved_promos': approved_promos,
        'broadcasted_promos': broadcasted_promos,
        'total_revenue': total_revenue
    })

@app.route('/fix_database_schema', methods=['GET'])
def fix_database_schema():
    """Temporary route to add missing columns to the database"""
    try:
        with app.app_context():
            # 1. Add AI Memory Columns
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS ai_memory TEXT;"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_interaction_summary TEXT;"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mood_score VARCHAR(20);"))
            
            # 2. Add Wealth Plan Columns (Just in case they are missing too)
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS vendors_patronized_month INTEGER DEFAULT 0;"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_ai_reward TIMESTAMP;"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS ai_points_today FLOAT DEFAULT 0.0;"))
            
            # 3. Create the Order table if it doesn't exist
            db.create_all()
            
            db.session.commit()
            return "✅ Database Schema Updated Successfully! You can close this page."
    except Exception as e:
        return f"❌ Error updating schema: {str(e)}"
    
@app.route('/api/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role', None)
    
    query = User.query
    if role == 'vendor':
        query = query.filter_by(is_vendor=True)
    elif role == 'subscriber':
        query = query.filter_by(is_subscriber=True)
        
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page
    })

# --- NEW: Verify Vendor Endpoint ---
@app.route('/api/users/<int:user_id>/verify', methods=['POST'])
def verify_user(user_id):
    """Admin verifies a vendor manually"""
    user = User.query.get_or_404(user_id)
    user.verification_status = "verified"
    db.session.commit()
    
    # Notify Vendor
    whatsapp_service.send_text_message(
        user.phone_number,
        "✅ Your Vendor Account is VERIFIED! \n\nYou can now run promotions without restrictions."
    )
    return jsonify({"success": True, "user": user.to_dict()})


@app.route('/api/users/<int:user_id>/reject_verification', methods=['POST'])
def reject_user_verification(user_id):
    """Admin rejects a vendor verification"""
    user = User.query.get_or_404(user_id)
    user.verification_status = "rejected"
    # Optional: Reset doc so they can upload again if needed
    # user.verification_doc = None 
    db.session.commit()
    
    # Notify Vendor
    whatsapp_service.send_text_message(
        user.phone_number,
        "❌ Verification Failed.\n\nThe document you uploaded was rejected. Please ensure it is clear, valid, and recent (NIN, Utility Bill, or Bank Statement). \n\nPlease upload a new document to try again."
    )
    return jsonify({"success": True, "user": user.to_dict()})


@app.route('/api/promos', methods=['GET'])
def get_promos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)
    query = Promo.query
    if status:
        query = query.filter_by(status=status)
    promos = query.order_by(Promo.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'promos': [promo.to_dict() for promo in promos.items],
        'total': promos.total,
        'pages': promos.pages,
        'current_page': promos.page
    })

@app.route('/api/promos/<int:promo_id>/approve', methods=['POST'])
def approve_promo(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    promo.status = PromoStatus.APPROVED
    promo.approved_at = datetime.utcnow()
    db.session.commit()
    vendor = promo.vendor
    whatsapp_service.send_text_message(
        vendor.phone_number,
        "✅ Great news! Your promotion '{}' has been approved!\n\nIt will be broadcasted to interested users soon. 🚀". format (promo.title)
    )
    return jsonify({"success": True, "promo": promo.to_dict()})

@app.route('/api/promos/<int:promo_id>/reject', methods=['POST'])
def reject_promo(promo_id):
    data = request.json
    reason = data.get('reason', 'Does not meet our guidelines')
    promo = Promo.query.get_or_404(promo_id)
    promo.status = PromoStatus.REJECTED
    db.session.commit()
    vendor = promo.vendor
    whatsapp_service.send_text_message(
        vendor.phone_number,
        "❌ Your promotion '{}' was not approved.\n\nReason: {}\n\nPlease create a new promotion that follows our guidelines.". format (promo.title, reason)
    )
    return jsonify({"success": True, "promo": promo.to_dict()})

def send_broadcast_background(promo_id, app_context):
    """Runs broadcast in background thread with STRICT formatting"""
    with app_context:
        promo = Promo.query.get(promo_id)
        if not promo: return
        
        subscribers = User.query.filter_by(is_subscriber=True, is_active=True).all()
        
        promo_cats = [c.strip().lower() for c in (promo.category or "general").split(',')]
        target_gender = promo.target_gender 
        
        broadcast = Broadcast(
            promo_id=promo.id,
            total_recipients=0,
            status='in_progress'
        )
        db.session.add(broadcast)
        db.session.commit()
        
        sent_count = 0
        failed_count = 0
        
        message = promo.ai_generated_caption
        message += "\n\n---------------------------------------------------------------\n"
        if promo.price > 0:
            message += "💰 Price: ₦{:,.2f}".format(promo.price)
        else:
            message += "💰 Price: Negotiable"
        message += "\n📞 Contact: {}".format(promo.contact_info)
        message += "\n---------------------------------------------------------------"
        
        whatsapp_svc = WhatsAppService()
        valid_recipients = 0

        for subscriber in subscribers:
            if subscriber.current_mode == 'vendor':
                continue
            
            if target_gender != 'All' and subscriber.gender:
                if subscriber.gender != 'All' and subscriber.gender != target_gender:
                    continue 

            user_interests = (subscriber.interests or "").lower()
            match_found = False
            
            if "general" in promo_cats:
                match_found = True
            else:
                for cat in promo_cats:
                    if cat in user_interests:
                        match_found = True
                        break
            
            if not match_found:
                continue
            
            valid_recipients += 1
            
            try:
                if promo.media_url:
                    if promo.media_type == 'image':
                        result = whatsapp_svc.send_image_message(subscriber.phone_number, promo.media_url, message)
                    elif promo.media_type == 'video':
                        result = whatsapp_svc.send_video_message(subscriber.phone_number, promo.media_url, message)
                    else:
                        result = whatsapp_svc.send_text_message(subscriber.phone_number, message)
                else:
                    result = whatsapp_svc.send_text_message(subscriber.phone_number, message)
                
                if result and result.get('success'):
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Error sending to {subscriber.phone_number}: {e}")
                failed_count += 1
                
        broadcast.total_recipients = valid_recipients
        broadcast.sent_count = sent_count
        broadcast.failed_count = failed_count
        broadcast.status = 'completed'
        broadcast.completed_at = datetime.utcnow()
        
        promo.status = PromoStatus.BROADCASTED
        promo.broadcasted_at = datetime.utcnow()
        db.session.commit()
        
        whatsapp_svc.send_text_message(
            promo.vendor.phone_number,
            "🎉 Your promotion has been broadcasted!\n\n📊 Sent to {} active customers.".format(sent_count)
        )

@app.route('/api/promos/<int:promo_id>/broadcast', methods=['POST'])
def broadcast_promo(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    if promo.status != PromoStatus.APPROVED:
        return jsonify({"success": False, "error": "Promo must be approved first"}), 400
    
    thread = threading.Thread(target=send_broadcast_background, args=(promo_id, app.app_context()))
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "Broadcast started in background. Check status later."
    })

@app.route('/api/payments/<int:payment_id>/confirm', methods=['POST'])
def confirm_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.status == PaymentStatus.COMPLETED:
        return jsonify({"success": False, "message": "Payment already completed"}), 400

    payment.status = PaymentStatus.COMPLETED
    payment.completed_at = datetime.utcnow()
    db.session.commit()
    
    if payment.user:
        whatsapp_service.send_text_message(
            payment.user.phone_number,
            "✅ Payment Confirmed! Your promotion is now being reviewed."
        )

    return jsonify({"success": True, "payment": payment.to_dict()})

@app.route('/api/payments', methods=['GET'])
def get_payments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    payments = Payment.query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'payments': [payment.to_dict() for payment in payments.items],
        'total': payments.total,
        'pages': payments.pages,
        'current_page': payments.page
    })

@app.route('/api/broadcasts', methods=['GET'])
def get_broadcasts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    broadcasts = Broadcast.query.order_by(Broadcast.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'broadcasts': [broadcast.to_dict() for broadcast in broadcasts.items],
        'total': broadcasts.total,
        'pages': broadcasts.pages,
        'current_page': broadcasts.page
    })

@app.route('/api/support', methods=['GET'])
def get_tickets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)
    
    query = SupportTicket.query
    if status:
        query = query.filter_by(status=status)
        
    tickets = query.order_by(SupportTicket.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'tickets': [t.to_dict() for t in tickets.items],
        'total': tickets.total,
        'pages': tickets.pages,
        'current_page': tickets.page
    })

@app.route('/api/support/<int:ticket_id>/resolve', methods=['POST'])
def resolve_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    ticket.status = "resolved"
    db.session.commit()
    return jsonify({"success": True, "ticket": ticket.to_dict()})

@app.route('/api/settings/vendor-lock', methods=['GET'])
def get_vendor_lock_status():
    """Check if vendor registration is locked"""
    setting = SystemSetting.query.get('vendor_lock')
    # Default to False (Not locked) if setting doesn't exist yet
    is_locked = setting.value == 'true' if setting else False
    return jsonify({"locked": is_locked})

@app.route('/api/settings/vendor-lock', methods=['POST'])
def set_vendor_lock_status():
    """Turn vendor registration ON or OFF"""
    data = request.json
    should_lock = data.get('locked', False)
    
    setting = SystemSetting.query.get('vendor_lock')
    if not setting:
        setting = SystemSetting(key='vendor_lock', value='true' if should_lock else 'false')
        db.session.add(setting)
    else:
        setting.value = 'true' if should_lock else 'false'
    
    db.session.commit()
    return jsonify({"success": True, "locked": should_lock})

@app.route('/reset_database_secret_key_123', methods=['GET'])
def reset_database():
    """Wipes the entire database and recreates it. DANGEROUS!"""
    try:
        with app.app_context():
            db.drop_all()   # Deletes all tables
            db.create_all() # Recreates them with new schema
            
            # Optional: Create a default admin user immediately
            # admin = User(phone_number="234...", name="Admin", is_vendor=True)
            # db.session.add(admin)
            # db.session.commit()
            
        return "✅ Database has been completely reset!"
    except Exception as e:
        return f"❌ Error resetting DB: {str(e)}"

@app.route('/api/media/<media_id>', methods=['GET'])
def get_media(media_id):
    """Proxy to fetch media from WhatsApp and serve it to the frontend"""
    import requests
    
    # 1. Validate ID format (basic check)
    if not media_id or len(media_id) < 5 or media_id == "12345":
        return jsonify({"error": "Invalid Media ID"}), 400

    # 2. Get the URL from WhatsApp
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_API_TOKEN')}"
    }
    
    try:
        # Step 1: Get the download URL
        meta_response = requests.get(url, headers=headers)
        
        # Check specifically for 400/404 from Facebook
        if meta_response.status_code == 400:
            return jsonify({"error": "Media ID invalid or expired"}), 400
            
        meta_response.raise_for_status()
        media_url = meta_response.json().get('url')
        
        if not media_url:
            return "Media URL not found", 404

        # Step 2: Download the actual file binary
        # Note: We must pass the headers again to download the binary
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()
        
        # Step 3: Serve it back to the browser
        from flask import Response
        return Response(
            media_response.content, 
            mimetype=media_response.headers.get('Content-Type')
        )

    except Exception as e:
        print(f"Error fetching media: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)