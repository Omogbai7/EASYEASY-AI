# 🎯 EasyEasy WhatsApp Bot

> **AI-Powered WhatsApp E-Commerce & Promotion Automation System**

A production-ready WhatsApp chatbot that connects vendors with customers through automated promotions, AI-generated content, and intelligent broadcasting.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Business%20API-25D366)](https://developers.facebook.com/docs/whatsapp)

---

## 📸 Screenshots

### Admin Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Admin+Dashboard)

**Features visible in dashboard:**
- Real-time statistics (users, promos, revenue)
- Pending approval queue
- Broadcasting controls
- Payment tracking
- System status monitoring

---

## 🌟 Key Features

### For Vendors 👔
- **Easy Onboarding** - Set up business profile via WhatsApp
- **Promo Creation** - Upload images/videos with descriptions
- **AI Copywriting** - Auto-generate engaging ad captions with OpenAI
- **Payment Options** - Paid (₦500) or free promotions
- **Analytics** - Track views and clicks on promotions

### For Subscribers 📱
- **Interest-Based Targeting** - Receive relevant deals only
- **Direct Contact** - Connect with vendors instantly
- **No Spam** - Curated, admin-approved content

### For Admins 🎛️
- **Web Dashboard** - Full-featured management interface
- **Approval System** - Review and approve promotions
- **Broadcasting** - Send promotions to targeted audiences
- **Payment Tracking** - Monitor revenue from paid promotions
- **User Management** - Manage vendors and subscribers
- **Analytics** - View engagement metrics

---

## 🏗️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (upgradable to PostgreSQL)
- **ORM**: SQLAlchemy
- **APIs**:
  - WhatsApp Business Cloud API
  - Paystack Payment Gateway
  - OpenAI GPT-3.5 Turbo

### Frontend
- **Framework**: Next.js 15 (React)
- **Language**: TypeScript
- **UI Library**: shadcn/ui + Tailwind CSS
- **Icons**: Lucide React

### Infrastructure
- **Hosting**: Heroku / Railway / Render (Backend)
- **Frontend**: Netlify / Vercel
- **Webhooks**: WhatsApp & Paystack

---

## 📋 Prerequisites

1. **Python 3.9+** installed
2. **Node.js 18+** and Bun
3. **WhatsApp Business Account** ([Setup Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started))
4. **Paystack Account** ([Sign Up](https://paystack.com))
5. **OpenAI API Key** ([Get Key](https://platform.openai.com/api-keys))

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
cd EASYEASY AI
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment
```bash
cp .env
```

**Edit `.env` with your credentials:**
```env
WHATSAPP_API_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id_here
WHATSAPP_VERIFY_TOKEN=my_verify_token_123

PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

OPENAI_API_KEY=sk-xxxxx

DATABASE_URL=sqlite:///easyeasy.db
SECRET_KEY=your-secret-key-here
```

#### Run Backend
```bash
# Using the startup script
chmod +x run.sh
./run.sh

# Or manually
python app.py
```

Backend runs on: `http://localhost:5000`

### 3. Frontend Setup

```bash
# Install dependencies (if not already installed)
bun install

# Start development server
bun run dev
```

Dashboard runs on: `http://localhost:3000`

---

## 🔧 Configuration

### WhatsApp Business API Setup

1. **Create Meta Business Account**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create new app → Select "Business" type
   - Add "WhatsApp" product

2. **Get Credentials**
   - Phone Number ID
   - Access Token (generate permanent token)
   - Business Account ID

3. **Configure Webhook**
   - URL: `https://your-domain.com/webhook`
   - Verify Token: Match your `.env` value
   - Subscribe to: `messages` field

### Paystack Setup

1. **Create Account** at [paystack.com](https://paystack.com)
2. **Get API Keys** from Settings → API Keys
3. **Configure Webhook**:
   - URL: `https://your-domain.com/api/paystack/webhook`
   - Events: `charge.success`

### OpenAI Setup

1. **Create Account** at [platform.openai.com](https://platform.openai.com/)
2. **Add Payment Method** (required for API access)
3. **Generate API Key** from API Keys section
4. **Add to `.env`** file

---

## 🎭 How It Works

### User Flow Diagram

```
┌─────────────┐
│   User      │
│  Messages   │
│   Bot       │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  WhatsApp Webhook   │
│  (Flask Backend)    │
└──────┬──────────────┘
       │
       ├─► Vendor? ──► Create Promo ──► Payment ──► Admin Approval ──► Broadcast
       │
       └─► Subscriber? ──► Set Interests ──► Receive Targeted Promos
```

### Conversation States

**Vendor Journey:**
1. `WELCOME` → Select "Vendor"
2. `VENDOR_NAME` → Provide name
3. `VENDOR_BUSINESS` → Business details
4. `VENDOR_MENU` → Choose action
5. `PROMO_TITLE` → Upload media & title
6. `PROMO_DESCRIPTION` → Add description
7. `PROMO_PRICE` → Set price
8. `PROMO_CONTACT` → Contact info
9. `PROMO_TYPE` → Select paid/free
10. Payment (if paid) → Admin review → Broadcast

**Subscriber Journey:**
1. `WELCOME` → Select "Customer"
2. `SUBSCRIBER_INTERESTS` → Set interests
3. `SUBSCRIBER_MENU` → Receive promos

---

## 📊 Database Schema

### Tables

**users**
- Basic info (phone, name, role)
- Business details (for vendors)
- Interests (for subscribers)

**promos**
- Promotion details
- Media URLs
- AI-generated captions
- Status (pending/approved/rejected/broadcasted)
- Analytics (views, clicks)

**payments**
- Transaction records
- Paystack references
- Status tracking

**broadcasts**
- Campaign records
- Success metrics
- Recipient counts

**conversations**
- User conversation states
- Context data (JSON)
- Last activity tracking

---

## 🎨 Admin Dashboard Pages

### Dashboard (`/`)
- **Statistics Cards**: Users, Promos, Revenue
- **Quick Actions**: Pending approvals, Broadcasting
- **System Info**: Configuration status

### Vendors (`/vendors`)
- List all vendors
- View business details
- Activity status

### Subscribers (`/subscribers`)
- List all subscribers
- View interests
- Engagement metrics

### Promotions (`/promotions`)
- **Filter**: All, Pending, Approved, Rejected, Broadcasted
- **Actions**: Approve, Reject, Broadcast
- **View**: Full promo details with AI caption
- **Analytics**: Views and clicks

### Payments (`/payments`)
- Transaction history
- Revenue tracking
- Payment status

### Broadcasts (`/broadcasts`)
- Campaign history
- Delivery statistics
- Success rates

---

## 🧪 Testing

### Test Backend API

```bash
curl http://localhost:5000/health

curl http://localhost:5000/api/stats

curl http://localhost:5000/api/promos
```

### Test WhatsApp Integration

1. **Local Testing with ngrok**:
   ```bash
   ngrok http 5000
   ```
   Use ngrok URL for WhatsApp webhook

2. **Send Test Message** to your WhatsApp Business number
3. **Check Logs** for incoming webhook
4. **Verify** bot responds correctly

### Test Payment Flow

1. Create promotion as vendor
2. Choose paid option (₦500)
3. Use Paystack test card: `4084084084084081`
4. Verify payment webhook

---

## 🚢 Deployment

### Backend Deployment (Heroku)

```bash
cd backend

heroku login

heroku create easyeasy-api


heroku config:set WHATSAPP_API_TOKEN=xxx
heroku config:set PAYSTACK_SECRET_KEY=xxx
heroku config:set OPENAI_API_KEY=xxx

git init
git add .
git commit -m "Deploy backend"
heroku git:remote -a easyeasy-api
git push heroku main
```

### Frontend Deployment (Netlify)

```bash
bun run build

netlify deploy --prod
```

### Update Webhooks

After deployment, update:
1. **WhatsApp Webhook**: `https://your-api.herokuapp.com/webhook`
2. **Paystack Webhook**: `https://your-api.herokuapp.com/api/paystack/webhook`

---

## 🔐 Security Best Practices

✅ Never commit `.env` files
✅ Use strong `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
✅ Verify webhook signatures (implemented for Paystack)
✅ Use HTTPS in production (required for WhatsApp)
✅ Rotate API keys regularly
✅ Implement rate limiting (recommended for production)
✅ Keep dependencies updated

---

## 📈 Scaling for Production

### Database
- Migrate from SQLite to **PostgreSQL**
- Add connection pooling
- Implement database backups

### Caching
- Add **Redis** for session management
- Cache frequently accessed data
- Rate limiting with Redis

### Queue System
- Use **Celery** or **RQ** for background tasks
- Process broadcasts asynchronously
- Handle payment webhooks in queue

### Monitoring
- **Sentry** for error tracking
- **Prometheus** + **Grafana** for metrics
- **LogDNA** for log aggregation

### Performance
- Add CDN for media files (Cloudinary)
- Implement pagination for large datasets
- Add database indexes
- Use load balancer for multiple instances

---

## 🐛 Troubleshooting

### Backend Won't Start
- ✓ Check Python version: `python --version`
- ✓ Verify dependencies: `pip list`
- ✓ Check `.env` file exists and is configured

### WhatsApp Webhook Not Working
- ✓ Verify webhook URL is publicly accessible
- ✓ Check verify token matches
- ✓ Review Meta Business Manager logs
- ✓ Use ngrok for local testing

### Payment Issues
- ✓ Verify Paystack API keys
- ✓ Check webhook URL is correct
- ✓ Review Paystack dashboard logs
- ✓ Test with Paystack test cards

### OpenAI Errors
- ✓ Verify API key is valid
- ✓ Check account has credits
- ✓ Review rate limits

---

## 📚 API Documentation

### Backend Endpoints

#### Stats
```
GET /api/stats
Response: { total_users, total_vendors, total_promos, revenue, ... }
```

#### Users
```
GET /api/users?role=vendor&page=1&per_page=20
Response: { users: [...], total, pages }
```

#### Promotions
```
GET /api/promos?status=pending
POST /api/promos/{id}/approve
POST /api/promos/{id}/reject
POST /api/promos/{id}/broadcast
```

#### Payments
```
GET /api/payments
POST /api/paystack/webhook (Paystack only)
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **WhatsApp Business API** - Meta Platforms
- **Paystack** - Payment processing
- **OpenAI** - AI content generation
- **shadcn/ui** - Beautiful UI components
- **Flask** & **Next.js** - Excellent frameworks

---

## 📞 Support

For issues or questions:
- 📧 Email: support@easyeasy.app
- 📖 Documentation: See `SETUP.md`
- 🐛 Bug Reports: GitHub Issues

---

**Built with ❤️ for vendors and customers**

*Empowering businesses through intelligent automation*
