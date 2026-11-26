import keyboard
import asyncio
from bleak import BleakClient, BleakScanner

# --- Configurazione BLE ---
CHAR_UUID = "abcdef01-1234-5678-1234-56789abcdef0"
DEVICE_NAME = "ESP32_BLE_Server"


button_actions = {
    "BTN1": {"desc": "Play/Pausa", "key": "1"},
    "BTN2": {"desc": "Volume su", "key": "2"},
    "BTN3": {"desc": "Volume giù", "key": "3"},
    "BTN4": {"desc": "Avanti traccia", "key": "4"},
    "BTN5": {"desc": "Indietro traccia", "key": "5"},
    "BTN6": {"desc": "Muto", "key": "6"},
    "BTN7": {"desc": "Schermo intero", "key": "7"},
    "BTN8": {"desc": "Stop", "key": "8"},
}





def handle_button(code: str):
    """Gestisce il pulsante ricevuto via BLE"""
    code = code.strip()
    action = button_actions.get(code)
    if action:
        desc = action["desc"]
        key = action["key"]
        print(f"[BLE] {code} → {desc}")
        try:
            keyboard.press_and_release(key)
        except Exception as e:
            print(f"[Errore uinput] {e}")
    else:
        print(f"[BLE] Codice sconosciuto: {code}")


# --- Callback per la ricezione notifiche ---
async def handle_notify(sender, data):
    """Callback chiamata quando arriva una notifica BLE"""
    try:
        msg = data.decode("utf-8").strip()
        handle_button(msg)
    except Exception as e:
        print(f"[Errore decodifica BLE] {e}")


# --- Ricerca dispositivo BLE ---
async def find_device():
    print("Scanning BLE devices...")
    devices = await BleakScanner.discover()

    for d in devices:
        if d.name == DEVICE_NAME:
            print(f"Trovato dispositivo: {d.address}")
            return d.address

    return None


# --- Ciclo principale di connessione ---
async def connect_loop():
    while True:
        address = await find_device()

        if not address:
            print("Dispositivo non trovato, riprovo tra 5 secondi...")
            await asyncio.sleep(5)
            continue

        try:
            async with BleakClient(address) as client:
                print(f"Connesso a {address}")
                await client.start_notify(CHAR_UUID, handle_notify)

                # Mantiene la connessione attiva
                while client.is_connected:
                    await asyncio.sleep(1)

                print("Disconnesso, riconnessione in corso...")

        except Exception as e:
            print(f"Errore connessione: {e}, riprovo tra 5 secondi...")

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(connect_loop())

