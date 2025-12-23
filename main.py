import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from TikTokLive import TikTokLiveClient

CHECK_INTERVAL_SECONDS = 5 * 60
TASK_TIMEOUT_SECONDS = 30
STATUS_FILE = "statuslive.json"


def log(msg: str):
    print(msg, flush=True)


async def check_user_live(username: str) -> bool | None:
    unique_id = username if username.startswith("@") else f"@{username}"
    client = TikTokLiveClient(unique_id=unique_id)
    try:
        return await asyncio.wait_for(client.is_live(), timeout=15)
    except Exception as e:
        log(f"⚠️ @{username}: ตรวจสอบไม่ได้ ({type(e).__name__})")
        return None


async def check_and_update_user(user: dict):
    username = user.get("name")
    result = await check_user_live(username)
    if result is None:
        user["status"] = "Offline"
    else:
        user["status"] = "Online" if result else "Offline"

    log(f"→ @{username}: {user['status']}")


async def run_check_cycle(cycle: int):
    th_tz = timezone(timedelta(hours=7))
    log("\n" + "=" * 40)
    log(f"🔄 รอบที่ {cycle}")
    log(f"🕒 {datetime.now(th_tz).strftime('%H:%M:%S')} (TH)")
    log("=" * 40)

    if not os.path.isfile(STATUS_FILE):
        log(f"❌ ไม่พบไฟล์ {STATUS_FILE}")
        return

    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    statuses = data.get("statuses", [])
    if not statuses:
        log("⚠️ ไม่มีรายชื่อผู้ใช้")
        return

    tasks = []
    for user in statuses:
        tasks.append(
            asyncio.wait_for(
                check_and_update_user(user),
                timeout=TASK_TIMEOUT_SECONDS
            )
        )

    await asyncio.gather(*tasks, return_exceptions=True)

    data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log("💾 อัปเดต statuslive.json สำเร็จ")


async def main():
    cycle = 0
    while True:
        cycle += 1
        await run_check_cycle(cycle)
        log(f"⏳ รอ {CHECK_INTERVAL_SECONDS // 60} นาที...\n")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
