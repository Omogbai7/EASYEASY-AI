# EasyEasy WhatsApp Bot - Setup Guide

## 📋 Project Overview

**EasyEasy** is an AI-powered WhatsApp chatbot for e-commerce and promotion automation. It connects vendors with customers through WhatsApp, enabling automated ad delivery, payment processing, and targeted broadcasting.

### Core Features
- ✅ WhatsApp Business API Integration
- ✅ Paystack Payment Processing
- ✅ OpenAI Ad Generation
- ✅ Vendor & Subscriber Management
- ✅ Admin Approval System
- ✅ Automated Broadcasting
- ✅ Interest-based Targeting
- ✅ Analytics & Reporting

---

## 🏗️ Architecture

### Backend (Python/Flask)
- **Framework**: Flask
- **Database**: SQLite (can upgrade to PostgreSQL)
- **APIs**: WhatsApp Business Cloud API, Paystack, OpenAI
- **Location**: `backend/`

### Frontend (Next.js)
- **Framework**: Next.js 14 with TypeScript
- **UI**: shadcn/ui + Tailwind CSS
- **Location**: `src/`

---

## 🚀 Quick Start

### Prerequisites
1. **Python 3.9+** installed
2. **Node.js 18+** and Bun installed
3. **WhatsApp Business Account** (Meta Business)
4. **Paystack Account** (for payments)
5. **OpenAI API Key**

---

## 📦 Installation

### 1. Clone or Download the Project
```bash
cd EASYEASY AI
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
cp .env
```

Edit `.env` file with your credentials:

```env
# WhatsApp Configuration
WHATSAPP_API_TOKEN=your_whatsapp_business_api_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=my_secure_verify_token_123
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# Paystack Configuration
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxx

# OpenAI Configuration
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Database
DATABASE_URL=sqlite:///easyeasy.db

# App Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this
WEBHOOK_URL=https://your-domain.com/webhook
```

#### Initialize Database
```bash
python app.py
```
This will create the SQLite database with all necessary tables.

### 3. Frontend Setup

```bash
bun install

bun run dev
```

The admin dashboard will be available at `http://localhost:3000`

---

## 🔧 WhatsApp Business API Setup

### Step 1: Create Meta Business Account
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new App → Choose "Business" type
3. Add "WhatsApp" product

### Step 2: Get API Credentials
1. In WhatsApp section, find:
   - **Phone Number ID** (e.g., `123456789012345`)
   - **Business Account ID**
   - **Access Token** (generate permanent token)

### Step 3: Configure Webhook
1. In WhatsApp settings → Configuration
2. Set Webhook URL: `https://your-server.com/webhook`
3. Set Verify Token: Same as `WHATSAPP_VERIFY_TOKEN` in `.env`
4. Subscribe to messages field

### Step 4: Test Connection
```bash
curl -X POST \
  "https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "2348012345678",
    "type": "text",
    "text": {
      "body": "Hello from EasyEasy!"
    }
  }'
```

---

## 💳 Paystack Setup

### Step 1: Create Account
1. Sign up at [Paystack](https://paystack.com)
2. Complete KYC verification (for live keys)

### Step 2: Get API Keys
1. Go to Settings → API Keys
2. Copy **Public Key** and **Secret Key**
3. Use test keys for development (starts with `pk_test_` and `sk_test_`)

### Step 3: Configure Webhook
1. Go to Settings → Webhooks
2. Add URL: `https://your-server.com/api/paystack/webhook`
3. Subscribe to `charge.success` event

---

## 🤖 OpenAI Setup

### Get API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account and add payment method
3. Generate API Key from [API Keys page](https://platform.openai.com/api-keys)
4. Copy key to `.env` file

---

## 🌐 Deployment

### Option 1: Deploy to Heroku (Backend)

#### Create Heroku App
```bash
cd backend
heroku create EASYEASY AI
```

#### Set Environment Variables
```bash
heroku config:set WHATSAPP_API_TOKEN=your_token
heroku config:set PAYSTACK_SECRET_KEY=your_key
heroku config:set OPENAI_API_KEY=your_key
# ... set all other env 
```

#### Create Procfile
```
web: gunicorn app:app
```

#### Deploy
```bash
git add .
git commit -m "Deploy backend"
git push heroku main
```

#### Update Webhook URL
Update WhatsApp webhook to: `https://easyeasy-bot-api.herokuapp.com/webhook`

---

### Option 2: Deploy to Railway (Backend)

1. Go to [Railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Select backend folder
4. Add environment variables in settings
5. Deploy!

---

### Frontend Deployment (Netlify/Vercel)

#### Deploy to Netlify (recommended)
```bash

bun run build

netlify deploy --prod
```

#### Or Deploy to Vercel
```bash
vercel --prod
```

---

## 📱 Bot Usage Flow

### For Vendors:
1. Message the bot on WhatsApp
2. Select "Vendor" role
3. Provide business details
4. Create promotion with:
   - Image/video upload
   - Title & description
   - Price & contact info
5. Choose paid (₦500) or free promotion
6. Complete payment (if paid)
7. Wait for admin approval
8. Promotion broadcasted to subscribers

### For Subscribers:
1. Message the bot
2. Select "Customer" role
3. Set interests (Fashion, Food, etc.)
4. Receive targeted promotions
5. Click to contact vendors

### For Admins:
1. Access dashboard at `http://localhost:3000`
2. Review pending promotions
3. Approve or reject
4. Broadcast approved promotions
5. Monitor analytics

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` template
2. **Use strong SECRET_KEY** - Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
3. **Verify webhook signatures** - Implemented for Paystack
4. **Use HTTPS in production** - Required for WhatsApp webhooks
5. **Rotate API keys regularly**
6. **Implement rate limiting** (add to production)

---

## 📊 Database Schema

### Users Table
- `id`, `phone_number`, `name`, `role`, `interests`
- `business_name`, `business_description`
- `created_at`, `is_active`

### Promos Table
- `id`, `vendor_id`, `title`, `description`, `price`
- `media_url`, `media_type`, `promo_type`
- `ai_generated_caption`, `status`, `category`
- `views`, `clicks`, `created_at`, `approved_at`

### Payments Table
- `id`, `user_id`, `promo_id`, `amount`
- `reference`, `status`, `paystack_reference`
- `created_at`, `completed_at`

### Broadcasts Table
- `id`, `promo_id`, `total_recipients`
- `sent_count`, `failed_count`, `status`
- `created_at`, `completed_at`

### Conversations Table
- `id`, `phone_number`, `state`, `context`
- `last_message_at`

---

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:5000/health

# Get stats
curl http://localhost:5000/api/stats

# Get promotions
curl http://localhost:5000/api/promos
```

### Test WhatsApp Integration
1. Send message to your WhatsApp Business number
2. Check backend logs for incoming webhook
3. Verify bot responds correctly

### Test Payment Flow
1. Create promotion as vendor
2. Choose paid option
3. Use Paystack test card: `4084084084084081`
4. Verify webhook receives payment confirmation

---

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version`
- Verify all dependencies installed: `pip list`
- Check database permissions

### WhatsApp webhook not receiving messages
- Verify webhook URL is publicly accessible (use ngrok for local testing)
- Check verify token matches in Meta console and `.env`
- Review Meta Business Manager logs

### Paystack webhook fails
- Verify webhook URL is correct
- Check signature validation in code
- Review Paystack dashboard logs

### OpenAI API errors
- Verify API key is valid
- Check account has credits
- Review rate limits

---

## 📈 Scaling Considerations

### For Production:
1. **Switch to PostgreSQL** - Better for concurrent writes
2. **Add Redis** - For caching and rate limiting
3. **Implement queues** - For broadcast processing (Celery/RQ)
4. **Add monitoring** - Sentry for error tracking
5. **Use CDN** - For media file hosting
6. **Load balancing** - For high traffic

---

## 🤝 Support

For issues or questions:
- Review this documentation
- Check backend logs: `tail -f backend/logs/app.log`
- Test API endpoints with Postman
- Review WhatsApp Business API documentation

---

## 📝 License

This project is for educational and commercial use.

---

## 🎯 Next Steps

1. ✅ Configure all API credentials
2. ✅ Test locally with ngrok
3. ✅ Deploy backend to cloud
4. ✅ Deploy frontend
5. ✅ Configure production webhooks
6. ✅ Test end-to-end flow
7. ✅ Launch! 🚀

---

**Built with ❤️ for vendors and customers**
