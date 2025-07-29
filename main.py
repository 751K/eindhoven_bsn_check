import requests
from datetime import datetime
import time
from pushplus import send_pushplus_msg
from config import PUSHPLUS_TOKEN, INTERVAL, EARLIEST_TIME_FILE


def check_eindhoven_slot(headers):
    url = ("https://online3.jccsoftware.nl/JCC/Afspraakgeleiding%20Productie/JCC-Afspraakgeleiding/Api/api/proxy/warp"
           "/appointment/firstAvailableAppointmentTime?toDate=2025-10-12&activityId=3b1d2828-c105-485e-93e3-2ea261784"
           "74d&amount=1&locationNumber=1")
    resp = requests.get(url, headers=headers)
    print("Status code:", resp.status_code)
    print("Response text:", resp.text)
    try:
        data = resp.json()
        if data.get("success") and data.get("data"):
            slot = data["data"][0]
            time_str = slot.get("firstAvailableTime")
            if time_str:
                dt = datetime.fromisoformat(time_str)
                print(f"有空位！最早时间：{dt.strftime('%Y-%m-%d %H:%M')}")
                return dt
        print("当前无可预约空位")
        return None
    except Exception as e:
        print("解析 JSON 失败，原始响应如上。错误：", e)
        return None


def main():
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "authorization": "Bearer e171c5c5-03cd-4deb-be00-d3f8241e234f",
        "connection-source-id": "f59ddbf9-9158-42d0-ac39-f6065c003da4",
        "id": "651a9a86-0f44-43ec-a626-3bdb11d31118",
        "language": "nl",
        "origin": "https://eindhoven.mijnafspraakmaken.nl",
        "priority": "u=1, i",
        "referer": "https://eindhoven.mijnafspraakmaken.nl/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-storage-access": "active",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "warp-api-version": "1",
        "cookie": "__Host-.JCC-Afspraakgeleiding.Session=CfDJ8LTp7o4MS41Bp87%2Bf6JT60580zhayVdtwJekoRJXbaEeNfvj86MoAWIt37m8%2BhQIsB79s2dkfXQoow2dOheVoJvK%2BkYWIyEGELC3jq8nNiXmaF%2FMjRG2ebfKLH8Q%2F%2Fu%2BLEfazFjV1mfMQ1p3np4ZoOogP2Ey%2FF717Nq45fQOMsd4"
    }
    last_push_time = None
    last_slot_time = None

    # 读取之前记录的最早时间
    def load_earliest_time():
        try:
            with open(EARLIEST_TIME_FILE, 'r') as f:
                time_str = f.read().strip()
                return datetime.fromisoformat(time_str)
        except (FileNotFoundError, ValueError):
            return None

    def save_earliest_time(dt):
        try:
            with open(EARLIEST_TIME_FILE, 'w') as f:
                f.write(dt.isoformat())
        except Exception as e:
            print(f"保存最早时间失败: {e}")

    # 初始化最早时间
    earliest_time = load_earliest_time()
    if earliest_time:
        print(f"已记录的最早时间: {earliest_time.strftime('%Y-%m-%d %H:%M')}")

    while True:
        dt = check_eindhoven_slot(headers)
        if dt:
            should_notify = False
            if earliest_time is None:
                should_notify = True
                earliest_time = dt
                save_earliest_time(dt)
                print(f"首次发现空位，记录最早时间: {dt.strftime('%Y-%m-%d %H:%M')}")
            elif dt < earliest_time:
                should_notify = True
                old_time = earliest_time
                earliest_time = dt
                save_earliest_time(dt)
                print(f"发现更早时间！从 {old_time.strftime('%Y-%m-%d %H:%M')} 更新为 {dt.strftime('%Y-%m-%d %H:%M')}")
            elif dt == earliest_time and (last_slot_time is None or dt != last_slot_time):
                should_notify = True
                print(f"发现相同的最早时间: {dt.strftime('%Y-%m-%d %H:%M')}")

            if should_notify:
                time_str = dt.strftime('%Y-%m-%d %H:%M')

                if dt < earliest_time:
                    # 推送更早时间的通知
                    send_pushplus_msg(
                        PUSHPLUS_TOKEN,
                        f"发现更早时间！- {time_str}",
                        f"发现更早的可预约时间：{time_str}"
                    )
                    # 推送当前最早时间的通知
                    send_pushplus_msg(
                        PUSHPLUS_TOKEN,
                        f"有空位 - {time_str}",
                        f"最早可预约时间：{time_str}"
                    )
                else:
                    # 正常推送一条消息
                    send_pushplus_msg(
                        PUSHPLUS_TOKEN,
                        f"有空位 - {time_str}",
                        f"最早可预约时间：{time_str}"
                    )

                last_push_time = datetime.now()
                last_slot_time = dt
        print(f"等待 {INTERVAL} 秒后再次查询...\n")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
