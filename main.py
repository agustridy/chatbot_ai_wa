from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import sqlite3
from dotenv import load_dotenv
import os
load_dotenv()

# ============================================
# 1. SETUP DATABASE SQLITE (PRODUK DAN STOK)
# ============================================

def init_db():
    """Inisialisasi database produk dan stok"""
    conn = sqlite3.connect('product_stock.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    # Tambahkan data produk contoh
    c.execute("INSERT OR IGNORE INTO products (name, stock, price) VALUES ('Produk A', 10, 100000)")
    c.execute("INSERT OR IGNORE INTO products (name, stock, price) VALUES ('Produk B', 5, 200000)")
    conn.commit()
    conn.close()

init_db()

# ============================================
# 2. FLASK APP UNTUK WEBHOOK WHATSAPP / SMS
# ============================================

app = Flask(__name__)

# API endpoints dan keys
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
HUMAN_AGENT_NUMBER = os.getenv('HUMAN_AGENT_NUMBER')  # Nomor agen manusia
ENG_LANG = ['en', 'english']
ID_LANG = ['id', 'indonesia']

def detect_language(text):
    """Deteksi bahasa sederhana berdasarkan kata kunci"""
    text_lower = text.lower()
    if any(word in text_lower for word in ['hello', 'how', 'what', 'order', 'product']):
        return 'en'
    elif any(word in text_lower for word in ['halo', 'apa', 'bagaimana', 'pesan', 'produk']):
        return 'id'
    return 'en'  # default

def get_product_list():
    """Ambil daftar produk dari database"""
    conn = sqlite3.connect('product_stock.db')
    c = conn.cursor()
    c.execute("SELECT name, stock, price FROM products")
    products = c.fetchall()
    conn.close()
    product_list = "\n".join([f"- {name}: {stock} tersedia, Harga: Rp {price:,}" for name, stock, price in products])
    return product_list

def query_deepseek(question, lang='en'):
    """Query ke Deepseek API untuk mendapatkan jawaban AI"""
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    daftar_produk = get_product_list()
    
    # Konteks berdasarkan bahasa
    context = "You are a helpful customer service assistant. " if lang == 'en' else f"Anda adalah asisten layanan pelanggan yang membantu. Daftar Produk yang tersedia: {daftar_produk}."
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': context},
            {'role': 'user', 'content': question}
        ],
        'max_tokens': 500
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return "Maaf, terjadi kesalahan pada sistem." if lang == 'id' else "Sorry, there was a system error."
    except Exception as e:
        return f"Error: {str(e)}"

def check_product_stock(product_name):
    """Cek stok produk dari database"""
    conn = sqlite3.connect('product_stock.db')
    c = conn.cursor()
    c.execute("SELECT stock, price FROM products WHERE name LIKE ?", ('%' + product_name + '%',))
    result = c.fetchone()
    conn.close()
    return result  # (stock, price)

def process_order(product_name, quantity):
    """Proses pesanan dan update stok"""
    stock_info = check_product_stock(product_name)
    if stock_info:
        stock, price = stock_info
        if stock >= quantity:
            # Update stok
            conn = sqlite3.connect('product_stock.db')
            c = conn.cursor()
            c.execute("UPDATE products SET stock = stock - ? WHERE name LIKE ?", (quantity, '%' + product_name + '%'))
            conn.commit()
            conn.close()
            total_price = price * quantity
            return f"Pesanan Anda untuk {quantity} {product_name} telah diproses. Total harga: Rp {total_price:,}."
        else:
            return f"Maaf, stok untuk {product_name} tidak cukup. Stok tersedia: {stock}."
    else:
        return "Produk tidak ditemukan."

def get_opening_message():
    """Script opening hook untuk engagement"""
    return ("👋 Hai! Selamat datang di layanan pelanggan kami. "
            "Kami siap membantu Anda 24/7. "
            "Tanyakan apa saja tentang produk, stok, atau pemesanan. "
            "Mari kita buat pengalaman belanja Anda menyenangkan! 😊")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint webhook untuk menerima pesan dari Twilio"""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    response = MessagingResponse()
    msg = response.message()

    # Deteksi bahasa
    lang = detect_language(incoming_msg)

    # Logic auto-reply & pemrosesan
    if any(keyword in incoming_msg.lower() for keyword in ['pesan', 'order', 'beli', 'buy']):
        # Format: "Beli 2 Produk A" atau "Order 3 Product B"
        parts = incoming_msg.lower().split()
        try:
            qty_index = next(i for i, word in enumerate(parts) if word.isdigit())
            quantity = int(parts[qty_index])
            product_name = ' '.join(parts[qty_index + 1:])
            order_response = process_order(product_name, quantity)
            msg.body(order_response)
        except (StopIteration, ValueError):
            if lang == 'id':
                msg.body("Format pesanan tidak dikenali. Contoh: 'Beli 2 Produk A'")
            else:
                msg.body("Order format not recognized. Example: 'Buy 2 Product A'")
    
    elif any(keyword in incoming_msg.lower() for keyword in ['stok', 'stock', 'tersedia']):
        # Cek stok
        parts = incoming_msg.lower().split()
        product_keywords = ['stok', 'stock', 'tersedia']
        product_name = ' '.join([word for word in parts if word not in product_keywords])
        stock_info = check_product_stock(product_name)
        if stock_info:
            stock, price = stock_info
            if lang == 'id':
                msg.body(f"Stok {product_name}: {stock} unit. Harga: Rp {price:,}")
            else:
                msg.body(f"Stock for {product_name}: {stock} units. Price: Rp {price:,}")
        else:
            if lang == 'id':
                msg.body(f"Produk '{product_name}' tidak ditemukan.")
            else:
                msg.body(f"Product '{product_name}' not found.")
    
    elif any(keyword in incoming_msg.lower() for keyword in ['halo', 'hi', 'hello']):
        if lang == 'id':
            msg.body(get_opening_message())
        else:
            msg.body("Hello! How can I help you today?")
    
    elif any(keyword in incoming_msg.lower() for keyword in ['agent', 'manusia', 'human']):
        # Hand off ke human agent
        if lang == 'id':
            msg.body("Sedang menghubungkan Anda ke agen manusia. Mohon tunggu sebentar...")
        else:
            msg.body("Connecting you to a human agent. Please wait a moment...")
    
    else:
        # Query AI untuk pertanyaan umum
        answer = query_deepseek(incoming_msg, lang=lang)
        msg.body(answer)

    return str(response)

@app.route('/')
def index():
    """Halaman utama untuk testing"""
    return """
    <h1>AI Chatbot Customer Service</h1>
    <p>Webhook aktif di: /webhook</p>
    <p>Database produk: product_stock.db</p>
    <p>API: Deepseek + Twilio</p>
    """

if __name__ == '__main__':
    print("=" * 50)
    print("AI CHATBOT CUSTOMER SERVICE")
    print("=" * 50)
    print("Server berjalan di: http://localhost:5000")
    print("Webhook endpoint: /webhook")
    print("Opening message:", get_opening_message())
    print("=" * 50)
    app.run(debug=True, port=5000)