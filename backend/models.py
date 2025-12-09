from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(str, Enum):
    VENDOR = "vendor"
    SUBSCRIBER = "subscriber"
    ADMIN = "admin"

class PromoStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BROADCASTED = "broadcasted"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    
    # --- DUAL ROLE FLAGS ---
    is_vendor = db.Column(db.Boolean, default=False)
    is_subscriber = db.Column(db.Boolean, default=False)
    current_mode = db.Column(db.String(20), default="subscriber") 

    # --- VERIFICATION (NEW) ---
    verification_status = db.Column(db.String(20), default="unverified") # unverified, pending, verified, rejected
    verification_doc = db.Column(db.String(255)) # Media ID of the uploaded doc
    
    # --- POINTS & LIMITS ---
    points = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(20), unique=True)
    referred_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    free_trials_used = db.Column(db.Integer, default=0)
    community_task_done = db.Column(db.Boolean, default=False)
    last_checkin = db.Column(db.DateTime)
    
    # --- USER PROFILE DATA ---
    gender = db.Column(db.String(10), default="All") 
    interests = db.Column(db.Text)
    
    # --- VENDOR SPECIFIC ---
    business_name = db.Column(db.String(200))
    business_category = db.Column(db.String(100))
    business_description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    last_ai_usage = db.Column(db.DateTime)
    daily_ai_count = db.Column(db.Integer, default=0)

    # Relationships
    promos = db.relationship('Promo', backref='vendor', lazy=True, foreign_keys='Promo.vendor_id')
    payments = db.relationship('Payment', backref='user', lazy=True)
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))
    tickets = db.relationship('SupportTicket', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'name': self.name,
            'is_vendor': self.is_vendor,
            'is_subscriber': self.is_subscriber,
            'verification_status': self.verification_status,
            'verification_doc': self.verification_doc,
            'points': self.points,
            'referral_code': self.referral_code,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'interests': self.interests if self.interests else "No interests set",
            'gender': self.gender,
            'business_name': self.business_name if self.business_name else "No Business Name",
            'business_description': self.business_description if self.business_description else "No description",
            'business_category': self.business_category
        }

class Promo(db.Model):
    __tablename__ = 'promos'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_impressions = db.Column(db.Integer, default=0)
    total_price = db.Column(db.Float, default=0.0)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    contact_info = db.Column(db.String(200))
    media_url = db.Column(db.String(500))
    media_type = db.Column(db.String(20))
    promo_type = db.Column(db.String(20))
    ai_generated_caption = db.Column(db.Text)
    status = db.Column(db.String(20), default=PromoStatus.PENDING)
    category = db.Column(db.String(100)) 
    target_gender = db.Column(db.String(10), default="All")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    broadcasted_at = db.Column(db.DateTime)
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'target_impressions': self.target_impressions,
            'total_price': self.total_price,
            'status': self.status,
            'category': self.category,
            'target_gender': self.target_gender,
            'vendor_name': self.vendor.business_name if self.vendor else "Unknown",
            'created_at': self.created_at.isoformat()
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    promo_id = db.Column(db.Integer, db.ForeignKey('promos.id'))
    amount = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default=PaymentStatus.PENDING)
    payment_method = db.Column(db.String(50))
    provider_reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'reference': self.reference,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="open") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user.name if self.user else "Unknown",
            'user_phone': self.user.phone_number if self.user else "Unknown",
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(50))
    context = db.Column(db.Text)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)

class Broadcast(db.Model):
    __tablename__ = 'broadcasts'
    id = db.Column(db.Integer, primary_key=True)
    promo_id = db.Column(db.Integer, db.ForeignKey('promos.id'), nullable=False)
    total_recipients = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    promo = db.relationship('Promo', backref='broadcasts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'sent_count': self.sent_count,
            'total_recipients': self.total_recipients,
            'created_at': self.created_at.isoformat()
        }