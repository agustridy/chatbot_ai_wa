# AI Chatbot Customer Service dengan Twilio API

## 📋 Deskripsi Aplikasi
AI Chatbot Customer Service adalah aplikasi chatbot pintar untuk bisnis yang dapat melayani pelanggan 24/7 melalui WhatsApp/SMS. Chatbot ini dilengkapi dengan fitur-fitur canggih seperti auto-reply, pemrosesan pesanan otomatis, integrasi database produk, dan multi-language support.

## ✨ Fitur Utama
- ✅ **Auto-reply 24/7**: Melayani pelanggan kapan saja
- ✅ **Pemrosesan Pesanan Otomatis**: Handle order dengan format sederhana
- ✅ **Integrasi Database**: SQLite untuk menyimpan data produk dan stok
- ✅ **Multi-language Support**: Indonesia dan Inggris
- ✅ **Handoff ke Human Agent**: Untuk kasus yang kompleks
- ✅ **AI-powered Responses**: Menggunakan Deepseek API untuk jawaban cerdas

## 🛠️ Tech Stack
- **Python 3.8+**
- **Flask**: Web framework
- **Twilio API**: Integrasi WhatsApp/SMS
- **Deepseek API**: AI untuk natural language processing
- **SQLite**: Database lokal
- **Requests**: HTTP client

## 📦 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd chatbot_ai_wa
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Buat file `.env` di root folder:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
HUMAN_AGENT_NUMBER=+6281234567890
```

### 4. Setup Twilio
1. Daftar di [Twilio](https://www.twilio.com)
2. Dapatkan Account SID dan Auth Token
3. Setup WhatsApp Sandbox atau SMS number
4. Configure webhook URL ke `http://your-domain.com/webhook`

### 5. Setup Deepseek API
1. Daftar di [Deepseek Platform](https://platform.deepseek.com)
2. Dapatkan API Key
3. Masukkan ke file `.env`

## 🚀 Cara Penggunaan

### 1. Jalankan Aplikasi
```bash
python main.py
```

### 2. Akses Aplikasi
- **Local**: http://localhost:5000
- **Webhook**: http://localhost:5000/webhook

### 3. Testing dengan Twilio Sandbox
1. Kirim pesan ke nomor Twilio WhatsApp Sandbox
2. Format pesan yang didukung:
   - `halo` / `hello` → Salam pembuka
   - `stok Produk A` → Cek stok produk
   - `beli 2 Produk B` → Pesan produk
   - `agent manusia` → Handoff ke human agent
   - Pertanyaan umum lainnya → Dijawab oleh AI

### 4. Contoh Interaksi
```
User: halo
Bot: Halo! Ada yang bisa saya bantu hari ini?

User: stok Produk A
Bot: Stok Produk A: 10 unit. Harga: Rp 100,000

User: beli 3 Produk B
Bot: Pesanan Anda untuk 3 Produk B telah diproses. Total harga: Rp 600,000

User: bagaimana cara return produk?
Bot: (AI Response) Untuk proses return produk, silakan...
```

## 📁 Struktur File
```
chatbot_ai_wa/
├── main.py              # Aplikasi utama
├── requirements.txt     # Dependencies
├── product_stock.db    # Database SQLite
├── .env               # Environment variables
├── README.md          # Dokumentasi ini

```

## 🔧 Konfigurasi Database
Database SQLite otomatis dibuat dengan struktur:
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL,
    price REAL NOT NULL
);
```

Data contoh yang tersedia:
- Produk A: Stok 10, Harga Rp 100,000
- Produk B: Stok 5, Harga Rp 200,000

## 🌐 Deployment

### 1. Local Development
```bash
python main.py
```

### 2. Production (Menggunakan Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 3. Cloud Deployment (Heroku/ Railway)
```bash
# Procfile
web: gunicorn -w 4 -b 0.0.0.0:$PORT main:app
```

## 🔍 Troubleshooting

### 1. Port 5000 sudah digunakan
```bash
# Ganti port di main.py
app.run(debug=True, port=5001)
```

### 2. Error Twilio Webhook
- Pastikan webhook URL benar di Twilio Console
- Gunakan ngrok untuk testing lokal: `ngrok http 5000`

### 3. API Key tidak valid
- Periksa file `.env`
- Pastikan API key aktif di platform Deepseek

### 4. Database error
```bash
# Hapus database dan restart
rm product_stock.db
python main.py
```

## 📈 Pengembangan Lebih Lanjut

### Fitur yang bisa ditambahkan:
1. **Payment Gateway Integration**: Integrasi dengan Midtrans/Xendit
2. **Analytics Dashboard**: Monitoring performa chatbot
3. **Sentiment Analysis**: Analisis mood pelanggan
4. **Multi-channel Support**: Instagram, Telegram, Email
5. **CRM Integration**: Hubungkan dengan sistem CRM existing
6. **Machine Learning**: Model custom untuk industry-specific queries

### Optimasi Performance:
1. **Caching**: Redis untuk cache respons
2. **Async Processing**: Celery untuk task berat
3. **Load Balancing**: Multiple worker instances
4. **Database Scaling**: PostgreSQL/MySQL untuk production

## 📝 Lisensi
Proyek ini open-source di bawah lisensi MIT.
