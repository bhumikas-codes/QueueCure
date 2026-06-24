[README.md](https://github.com/user-attachments/files/29289775/README.md)
# 🏥 QueueCure — Smart Clinic Queue Management System

> Built for **Queue Cure '26 Hackathon** hosted by Wooble × Unstop

---

## 💡 Problem Statement

76% of India's 1.5 million clinics still run on paper token slips and shouting. Patients wait 2–3 hours with zero visibility into when they'll be called. Doctors have no dashboard. Receptionists manage everything from memory.

**QueueCure fixes that.**

---

## ✨ Features

- 🔴 **Live Queue Updates** — Both screens sync instantly when "Call Next" is clicked — no page refresh needed!
- ⏱️ **Real Avg Time Calculation** — System auto-calculates average consultation time from actual doctor timings — not hardcoded!
- 🔐 **Receptionist Login** — Secure login so only authorized staff can manage the queue
- 👥 **Patient Display Board** — Patients see current token, tokens ahead, and estimated wait time in real time
- 📊 **Token Management** — Add patients, call next, track queue status (waiting/serving/served)
- 🏠 **Home Page** — Clean landing page with two clear entry points for patient and receptionist

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Real Time | Flask-SocketIO (WebSockets) |
| Database | SQLite |
| Frontend | HTML + CSS + JavaScript |
| Live Sync | Socket.IO (client) |

---

## 📁 Project Structure

```
QueueCure/
├── app.py                  # Main Flask + SocketIO server
├── database.py             # Database setup and connection
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html          # Home page (entry point)
│   ├── login.html          # Receptionist login
│   ├── receptionist.html   # Queue management panel
│   └── patient.html        # Patient waiting room display
└── static/
    └── style.css           # Styling
```

---

## 🚀 How to Run Locally

**1. Clone the repository:**
```bash
git clone https://github.com/bhumikas-codes/QueueCure.git
cd QueueCure
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run the app:**
```bash
python app.py
```

**4. Open in browser:**
- Home: `http://127.0.0.1:5000/`
- Patient View: `http://127.0.0.1:5000/patient`
- Receptionist: `http://127.0.0.1:5000/receptionist`

---

## 🔐 Login Credentials

| Role | Username | Password |
|---|---|---|
| Receptionist | `demo` | `demo123` |

---

## 🔄 Socket Event Flow

```
Receptionist clicks "Add Patient"
        ↓
emit("add_patient") → Flask Server
        ↓
Server saves patient to SQLite database
        ↓
emit("queue_update") broadcast → ALL connected screens
        ↓
Both receptionist + patient screens update INSTANTLY!

Receptionist clicks "Call Next"
        ↓
emit("call_next") → Flask Server
        ↓
Server updates current_token in database
        ↓
Server calculates real avg time from actual timestamps
        ↓
emit("queue_update") broadcast → ALL screens
        ↓
Patient screen shows new token, updated wait time!
```

---

## 📱 How It Works

**For Receptionist:**
1. Login with credentials
2. Add patient names as they arrive
3. Click "Call Next Token" when doctor is ready
4. System auto-tracks average consultation time

**For Patients:**
1. Open patient view on waiting room screen/TV
2. See current token being served
3. See how many patients are ahead
4. See estimated wait time — calculated from real data!

---

## 👩‍💻 Built By

**Bhumika S**
BCA Student | BGS First Grade College, Mysuru
- LinkedIn: linkedin.com/in/bhumika-s-a02248382
- GitHub: github.com/bhumikas-codes

---

*Built with ❤️ for Queue Cure '26 Hackathon*
