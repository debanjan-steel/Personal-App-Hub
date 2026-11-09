# 🚀 Universal Personal App Hub & Launchpad

A modern, mobile-first dashboard and launchpad to access, monitor, and share all your self-built online apps (**ITR Smart Assistant**, **MF Tracker and Advisor**, **Spam Email Deleter**, and more) from your laptop, Android device, or anywhere in the world.

---

## 🌟 Key Features

- **📱 Mobile-First & Android Ready**:
  - Touch-friendly responsive layout optimized for Android and laptop screens.
  - **PWA (Progressive Web App)** support: Open in Chrome on Android and tap **"Add to Home screen"** to install it like a native app.
- **⚡ Instant QR Code & Link Sharing**:
  - Click the **QR Code** button on any app to pop up a high-resolution QR code for quick scanning with phone cameras.
  - Native **Web Share API** integration (triggers Android's native share sheet) with 1-click clipboard fallback.
- **🛰️ Live Health & Status Monitoring**:
  - Asynchronously pings online hosted URLs to show live uptime badges (**Online 🟢** with response time in ms, or **Offline 🔴**).
- **🛠️ Zero-Code App Management**:
  - Add, edit, reorder, tag, or delete applications directly through the interactive UI modal.
- **🌙 Dark & Light Modes**:
  - Modern glassmorphic theme with persistent local storage toggle.

---

## 🏃 Quick Start (Local Run)

The project is configured with a **Python 3.13** virtual environment (`.venv`) that activates automatically in VS Code.

To run the hub locally:

```powershell
# Run using the virtual environment
.\.venv\Scripts\python.exe run.py
```

You'll see:
```text
🚀 Personal App Hub & Launchpad is starting!
💻 Local Laptop Access:   http://localhost:8000
📱 Android Phone (LAN):   http://192.168.x.x:8000
```

---

## 🌐 24/7 Remote / Internet Deployment (Free Tier)

Since your apps are hosted online, you can also host this dashboard online so you and your friends can access it anytime from any network without your laptop needing to be on:

### Option 1: Render.com (Recommended & Free)
1. Push this repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com) -> **New Web Service**.
3. Connect your repository.
4. Render will auto-detect the `Dockerfile` (or set **Build Command**: `pip install -r requirements.txt` and **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`).
5. Your dashboard is live at `https://your-hub.onrender.com`!

### Option 2: Railway.app / Fly.io / Hugging Face Spaces
- The included [`Dockerfile`](Dockerfile) runs out-of-the-box on Railway, Fly.io, or Hugging Face Docker spaces with zero configuration.

---

## 📁 Project Structure

```text
├── app/
│   ├── main.py        # FastAPI application, routing & API endpoints
│   ├── models.py      # Pydantic data schemas
│   ├── storage.py     # Thread-safe JSON app registry store
│   └── health.py      # Concurrent async uptime/ping monitor
├── data/
│   └── apps.json      # App metadata & registry (ITR, MF Tracker, etc.)
├── static/
│   ├── index.html     # Modern mobile-first dashboard UI
│   ├── manifest.json  # PWA manifest for Android home screen install
│   └── sw.js          # Service worker for offline shell caching
├── .vscode/
│   └── settings.json  # Auto-activates Python 3.13 .venv in VS Code
├── Dockerfile         # Cloud container deployment file
├── PROJECT PLANNER.md # Dynamic project plan & roadmap
├── requirements.txt   # Python 3.13 dependencies
└── run.py             # Single-command launcher
```

