import requests
import time
import socket
import sys
import argparse
from datetime import datetime
from options.header import *
from colorama import init, Fore, Style

init(autoreset=True)  # inisialisasi colorama

prev_data = {"ip": None, "server": None, "size": None, "time": []}

def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return "Tidak bisa resolve IP"

def spinner_animation(target, duration=3):
    spinner = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{Fore.CYAN}[{spinner[i % len(spinner)]}] Monitoring {target}...{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 60 + "\r")  # hapus spinner

def monitor(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        elapsed = time.time() - start
        size = len(response.content)
        server = response.headers.get("Server", "Unknown")
        content_type = response.headers.get("Content-Type", "Unknown")
        ip = get_ip(url.replace("https://", "").replace("http://", "").split("/")[0])

        status_color = Fore.GREEN if response.status_code == 200 else Fore.YELLOW
        print(f"{Fore.CYAN}[{datetime.now().strftime('%H:%M:%S')}] {Style.BRIGHT}Monitoring: {url}")
        print(f"{status_color}[{datetime.now().strftime('%H:%M:%S')}] Status       : {response.status_code} ({'OK' if response.status_code == 200 else 'WARN'})")
        print(f"{Fore.MAGENTA}[{datetime.now().strftime('%H:%M:%S')}] Waktu respon : {elapsed:.2f} detik")
        print(f"{Fore.BLUE}[{datetime.now().strftime('%H:%M:%S')}] Ukuran data  : {size} bytes")
        print(f"{Fore.YELLOW}[{datetime.now().strftime('%H:%M:%S')}] Server       : {server}")
        print(f"{Fore.CYAN}[{datetime.now().strftime('%H:%M:%S')}] Tipe konten  : {content_type}")
        print(f"{Fore.GREEN}[{datetime.now().strftime('%H:%M:%S')}] Alamat IP    : {ip}")

        anomalies = []
        if prev_data["ip"] and ip != prev_data["ip"]:
            anomalies.append("IP address berubah!")
        if prev_data["server"] and server != prev_data["server"]:
            anomalies.append("Server header berubah!")
        if prev_data["size"] and abs(size - prev_data["size"]) > prev_data["size"] * 0.3:
            anomalies.append("Ukuran halaman berubah signifikan!")
        if prev_data["time"]:
            avg_time = sum(prev_data["time"]) / len(prev_data["time"])
            if elapsed > avg_time * 2:
                anomalies.append("Waktu respon 2x lebih lambat dari rata-rata!")

        if anomalies:
            print(Fore.RED + Style.BRIGHT + "\n=== ANOMALI TERDETEKSI ===")
            for a in anomalies:
                print(Fore.RED + f"   >> {a}")
            print(Fore.RED + "="*60)

        prev_data["ip"] = ip
        prev_data["server"] = server
        prev_data["size"] = size
        prev_data["time"].append(elapsed)
        if len(prev_data["time"]) > 10:
            prev_data["time"].pop(0)

        with open("webpulse_log.txt", "a") as f:
            f.write(f"[{datetime.now()}] {url} | Status: {response.status_code} | "
                    f"Time: {elapsed:.2f}s | Size: {size} | IP: {ip}\n")
            if anomalies:
                f.write(f"  >> ANOMALY: {', '.join(anomalies)}\n")

    except requests.exceptions.RequestException as e:
        print(Fore.RED + Style.BRIGHT + "="*60)
        print(Fore.RED + f"[{datetime.now().strftime('%H:%M:%S')}] WEBSITE DOWN! {url}")
        print(Fore.RED + f"Error: {e}")
        print(Fore.RED + "="*60)
        with open("webpulse_log.txt", "a") as f:
            f.write(f"[{datetime.now()}] {url} | DOWN | Error: {e}\n")

def main():
    header()
    parser = argparse.ArgumentParser(description="WebMon - Monitoring website sederhana")
    parser.add_argument("-u", "--url", type=str, help="URL website yang ingin dimonitor", required=True)
    args = parser.parse_args()

    target = args.url.strip()
    print(Fore.GREEN + f"[+] Memulai monitoring {target}...\n")
    spinner_animation(target, duration=3)
    monitor(target)

if __name__ == "__main__":
    main()