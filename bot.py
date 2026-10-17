import os, re, json, requests
from datetime import datetime
from zoneinfo import ZoneInfo

URL = os.environ["EVENT_URL"]
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ARCHIVO = "vistos.json"

PATRON = re.compile(r'\\"name\\":\\"(.{1,80}?)\\",\\"slug\\":\\"(.{1,60}?)\\",\\"startingTime\\":(\d+)')

def avisar(texto):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": texto},
        timeout=10,
    )

def cargar():
    if os.path.exists(ARCHIVO):
        try:
            return json.load(open(ARCHIVO, encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None

def guardar(vistos):
    json.dump(vistos, open(ARCHIVO, "w", encoding="utf-8"), ensure_ascii=False)

def obtener_eventos():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    r.raise_for_status()
    eventos = {}
    for nombre, slug, ts in PATRON.findall(r.text):
        fecha = datetime.fromtimestamp(int(ts), ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M")
        eventos[slug] = f"{nombre} ({fecha})"
    return eventos

actuales = obtener_eventos()
if not actuales:
    print("Sin eventos leídos")
else:
    vistos = cargar()
    if vistos is None:
        guardar(actuales)
        print(f"Inicial: {len(actuales)} eventos guardados")
    else:
        nuevos = {s: n for s, n in actuales.items() if s not in vistos}
        for slug, nombre in nuevos.items():
            avisar(f"🎟️ Nuevo evento: {nombre}\n{URL}")
        if nuevos:
            vistos.update(nuevos)
            guardar(vistos)
        print(f"Nuevos: {len(nuevos)}")
