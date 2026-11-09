import uvicorn
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8000
    print("\n" + "=" * 60)
    print("🚀 Personal App Hub & Launchpad is starting!")
    print(f"💻 Local Laptop Access:   http://localhost:{port}")
    print(f"📱 Android Phone (LAN):   http://{local_ip}:{port}")
    print("=" * 60 + "\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

