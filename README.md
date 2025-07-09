# 🤖 PharmaBidBot

**PharmaBidBot** is a Telegram-based bidding system designed for the pharmaceutical industry. It connects medical organizations (like pharmacies or clinics) with pharmaceutical suppliers or couriers. The bot enables smooth order creation, offer submissions, and streamlined communication between clients and service providers — all within Telegram.

---

## 🚀 Features

- 📝 Create orders with photo and location
- 🧑‍⚕️ Allow multiple staff to submit offers for each order
- 💬 Customers receive offers and choose the best one
- ✅ Upon acceptance, the selected staff is notified
- 📍 Location sharing and viewing via Google Maps
- 📊 View order history (both for customers and staff)
- 🔒 Role-based access: staff vs customer
- 🌐 Multilingual support (e.g., Russian, Uzbek)

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Aiogram 2/3** – Telegram Bot Framework
- **Django** – Admin panel and backend logic
- **SQLite/PostgreSQL** – Database
- **Pillow** – Image handling
- **Async/Await** – High performance

---

## 📦 Setup

### 1. **Clone the repository**

```bash
git clone https://github.com/your-username/PharmaBidBot.git
cd PharmaBidBot
```
### 2. **Create and activate virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
```
### 3. **Install dependencie**

```bash
pip install -r requirements.txt
```

### 4. **Configure environment variables**

Create a .env file and set:

BOT_TOKEN=your_telegram_bot_token
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True

### 5. **Apply migrations**

```bash
python manage.py migrate
```

Run the bot and server

```bash
python bot.py  # For Telegram bot
python manage.py runserver  # For Django admin
```

## 🧪 Example Use Case
#### 1. A pharmacy sends an order with a photo and location.
#### 2. Multiple staff members receive the request and send offers (price + comment).
#### 3. The customer receives offers and clicks ✅ Accept on the best one.
#### 4. The chosen staff is notified and proceeds with delivery.

📂 Folder Structure
```bash
PharmaBidBot/
├── apps/
│   ├── orders/              # Order models & logic
│   ├── telegram_users/      # User roles and profiles
├── bot/                     # Aiogram handlers and states
├── media/                   # Uploaded images
├── manage.py
└── README.md
```

## 🛡 Security
User data is protected and accessible only by authorized users.
All Telegram interactions follow best practices for privacy and integrity.

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change or improve.

## 👨‍💻 Developed By

**Muhammad Nur Suxbatullayev**  
🎓 Back-End Developer with 1+ years of hands-on experience  
🏫 Full Scholarship Recipient at PDP University  
🧠 Skilled in building scalable and secure back-end systems using:  

🔗 **GitHub:** [github.com/muhammadnuruz](https://github.com/muhammadnuruz)  
📬 **Telegram:** [@TheMuhammadNur](https://t.me/TheMuhammadNur)

---

## ⭐ Support the Project

If this project helped you, inspired you, or you simply liked it — please consider giving it a **⭐ on GitHub**.  
Your support boosts the project's visibility and motivates continued improvements and future updates.

Thank you for being part of the journey!
