import asyncio
import json
import requests
import os
import random
from conversations import SCENARIOS # Đảm bảo file này nằm cùng thư mục

TOKENS_RAW = os.getenv("TOKEN", "")
GUILD_ID = os.getenv("SERVER_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")

TARGET_CHANNEL_NAME = "# 5 • 👥 Team Starry's Channel"
TOKEN_JOIN_DELAYS = [ (i * (i + 1) // 2) * 60 for i in range(8) ]
API = "https://discord.com/api/v10"

MEMBER_NAMES = [
    "TeamStarry", "Bocchi", "Nijika", "Ryo", 
    "Kita", "Kikuri", "HitoriGotou2102", "PA-san"
]

class TokenClient:
    def __init__(self, token, index, name, guild_id, channel_id):
        self.token = token
        self.name = name
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def join_voice(self):
        try:
            requests.patch(f"{API}/channels/{self.channel_id}", 
                           headers={"Authorization": self.token}, 
                           json={"name": TARGET_CHANNEL_NAME})
        except: pass
        print(f"[*] {self.name} đã vào voice.")

    async def chat_loop(self):
        """Logic chat với thời gian random để trông giống người thật"""
        s_idx = 0
        while True:
            scenario = SCENARIOS[s_idx]
            for speaker, content in scenario:
                if speaker == self.name:
                    # Random delay trước khi nhắn: 20-45 giây
                    await asyncio.sleep(random.uniform(20, 45))
                    
                    headers = {"Authorization": self.token, "Content-Type": "application/json"}
                    requests.post(f"{API}/channels/{self.channel_id}/messages", 
                                  headers=headers, json={"content": content})
                    print(f"[{self.name}] Đã nhắn: {content}")
            
            # Random nghỉ giữa các kịch bản: 80-100 phút
            rest_time = random.randint(4800, 6000)
            print(f"[*] {self.name} nghỉ kịch bản {s_idx+1}, chờ {rest_time//60} phút.")
            await asyncio.sleep(rest_time)
            
            s_idx = (s_idx + 1) % len(SCENARIOS)

async def run_token(token, i, gid, cid):
    client = TokenClient(token, i, MEMBER_NAMES[i], gid, cid)
    
    delay = TOKEN_JOIN_DELAYS[i]
    print(f"[*] {client.name} sẽ join sau {delay//60} phút")
    await asyncio.sleep(delay)
    
    # Chạy song song Voice (giữ kết nối) và Chat (theo kịch bản)
    await asyncio.gather(
        client.join_voice(),
        client.chat_loop()
    )

async def main():
    tokens = [t.strip() for t in TOKENS_RAW.split(",") if t.strip()]
    if not tokens: return
    
    tasks = [asyncio.create_task(run_token(tokens[i], i, GUILD_ID, CHANNEL_ID)) 
             for i in range(min(len(tokens), len(MEMBER_NAMES)))]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
