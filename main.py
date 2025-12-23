import time
import json
import datetime
import requests

STATUS_FILE = "statuslive.json"
CHECK_INTERVAL = 30  # วินาที


def check_tiktok_live():
    """
    🔍 ใส่ logic ตรวจ live ของคุณตรงนี้
    return True / False
    """
    try:
        # ตัวอย่าง dummy (ให้เปลี่ยนเป็นโค้ดจริงของคุณ)
        # response = requests.get("https://example.com")
        # return response.status_code == 200

        return False  # ← ค่าเริ่มต้น (ยังไม่ live)

    except Exception as e:
        print("❌ check error:", e)
        return False


def save_status(is_live):
    data = {
        "is_live": is_live,
        "last_check": datetime.datetime.utcnow().isoformat()
    }

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_last_status():
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("is_live", None)
    except:
        return None


def monitor():
    last_status = load_last_status()
    current_status = check_tiktok_live()

    if current_status != last_status:
        print("🔔 status changed:", current_status)
        save_status(current_status)
    else:
        print("⏱ no change | live =", current_status)


# ===============================
# 🚀 ENTRY POINT
# ===============================
print("🚀 TikTok Live Monitor started")

while True:
    try:
        monitor()
        time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("🛑 stopped by user")
        break

    except Exception as e:
        print("🔥 unexpected error:", e)
        time.sleep(10)
