import requests
import time
import random
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

# إعداد وحدة التحكم
console = Console()

# طلب التوكين من المستخدم
def get_user_token():
    console.print("📌 Please enter your Authorization Token:", style="bold blue")
    return input("Token: ").strip()

# عرض معلومات مميزة
def display_dexter():
    dexter_text = Text()
    dexter_text.append("D", style="bold red")
    dexter_text.append("e", style="bold yellow")
    dexter_text.append("x", style="bold green")
    dexter_text.append("t", style="bold blue")
    dexter_text.append("e", style="bold magenta")
    dexter_text.append("r", style="bold cyan")
    
    dexter_panel = Panel(
        dexter_text,
        title="[bold white]Automation Tool[/bold white]",
        subtitle="[italic white]Mine $SSLX and Collect Gold Eagle Coins![/italic white]",
        border_style="bold white",
        padding=(1, 2),
        width=50
    )
    console.print(dexter_panel, justify="center")

# إعداد الرؤوس (headers) بناءً على التوكين
def get_headers(token):
    return {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

# دالة لجلب بيانات التقدم
def get_progress_data(headers):
    try:
        response = requests.get("https://gold-eagle-api.fly.dev/user/me/progress", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"❌ Failed to fetch progress data: {response.status_code}", style="bold red")
            return None
    except Exception as e:
        console.print(f"❌ Error fetching progress data: {e}", style="bold red")
        return None

# دالة لجمع العملات باستخدام دفعات
def collect_coins_in_batches(headers, batch_size):
    try:
        body = {
            "available_taps": batch_size,
            "count": batch_size,
            "timestamp": int(time.time()),
            "salt": str(random.randint(1000, 9999)),  # رقم عشوائي كسالت
        }
        response = requests.post("https://gold-eagle-api.fly.dev/tap", json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            coins = data.get("coins_amount", "Unknown")
            console.print(f"✅ Collected {batch_size} coins. Total coins: {coins}", style="bold green")
            return batch_size
        else:
            console.print(f"❌ Failed to collect coins: {response.status_code}", style="bold red")
            return 0
    except Exception as e:
        console.print(f"❌ Error collecting coins: {e}", style="bold red")
        return 0

# تأخير عشوائي
def random_delay():
    delay = random.uniform(3, 7)  # بين 3 و7 ثوانٍ
    console.print(f"⏳ Waiting for {delay:.2f} seconds...", style="bold yellow")
    time.sleep(delay)

# المنطق الرئيسي لجمع العملات
def main():
    token = get_user_token()
    headers = get_headers(token)
    display_dexter()

    while True:
        progress_data = get_progress_data(headers)
        if progress_data:
            energy = progress_data.get("energy", 0)
            max_energy = progress_data.get("max_energy", 1000)

            console.print(f"💡 Energy: {energy}/{max_energy}", style="bold cyan")

            if energy == max_energy:
                console.print("⚡ Energy is full! Starting collection...", style="bold green")
                while energy > 0:
                    batch_size = min(10, energy)  # دفعة من 10 عملات كحد أقصى
                    collected = collect_coins_in_batches(headers, batch_size)
                    energy -= collected
                    random_delay()
            else:
                console.print("⏳ Waiting for energy to recharge...", style="bold yellow")
                time.sleep(60)  # تحقق كل دقيقة
        else:
            console.print("❌ Unable to fetch progress data. Retrying in 1 minute...", style="bold red")
            time.sleep(60)

# تشغيل الكود
if __name__ == "__main__":
    main()
