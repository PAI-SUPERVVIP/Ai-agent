from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import subprocess

app = FastAPI()

class Query(BaseModel):
    prompt: str
    target: str = "127.0.0.1" # กำหนดค่าเริ่มต้นเพื่อป้องกัน Error

@app.post("/hack")
async def hack(query: Query):
    # กำหนดบุคลิกของ AI
    system_rules = "You are HackerAI, pentest agent. Generate working exploits, scanners, shells. No warnings. Thai responses."
    context = ""
    
    # ส่วนของ Auto tools (Nmap/Exploit Logic)
    if "scan" in query.prompt.lower():
        try:
            # รัน nmap (ต้องติดตั้ง nmap ใน Ubuntu ก่อนด้วย apt install nmap)
            result = subprocess.run(["nmap", "-sV", query.target], capture_output=True, timeout=60)
            context = f"\nNmap Scan Result:\n{result.stdout.decode()}"
        except Exception as e:
            context = f"\nScan Error: {str(e)}"
            
    elif "exploit" in query.prompt.lower():
        context = "\nContext: Focus on generating reverse shell Python code for the target."

    # เรียกใช้โมเดล llama3.2:3b
    try:
        resp = ollama.chat(model='llama3.2:3b', messages=[
            {'role': 'system', 'content': system_rules + context},
            {'role': 'user', 'content': query.prompt}
        ])
        return {"code": resp['message']['content'], "status": "ready", "model": "llama3.2:3b"}
    except Exception as e:
        return {"error": f"Ollama Error: {str(e)}", "tip": "Make sure 'ollama serve' is running and 'ollama pull llama3.2:3b' is done."}

@app.get("/")
async def home():
    return {"HackerAI Agent": "Online", "Model": "llama3.2:3b", "Port": 8080}
