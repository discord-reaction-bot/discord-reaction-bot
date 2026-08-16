import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "dat")
os.makedirs(DATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
MAX_USERS = 20

DEFAULT_GUILD_CONFIG = {
    "watched_users": {},   # { "user_id": {"emojis": [...], "chance": int} }
    "paused": False
}


def _load_raw():
    if not os.path.exists(CONFIG_FILE):
        _save_raw({})
        return {}

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            _save_raw({})
            return {}


def _save_raw(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_config(guild_id):
    guild_id = str(guild_id)
    data = _load_raw()

    if guild_id not in data:
        data[guild_id] = {"watched_users": {}, "paused": False}
        _save_raw(data)

    guild_config = data[guild_id]
    for key, value in DEFAULT_GUILD_CONFIG.items():
        if key not in guild_config:
            guild_config[key] = value.copy() if isinstance(value, dict) else value

    migrated = False
    for user_id, value in list(guild_config["watched_users"].items()):
        if isinstance(value, str):
            guild_config["watched_users"][user_id] = {"emojis": [value], "chance": 100}
            migrated = True
        elif isinstance(value, dict):
            if "emojis" not in value:
                value["emojis"] = ["👍"]
                migrated = True
            if "chance" not in value:
                value["chance"] = 100
                migrated = True

    if migrated:
        save_config(guild_id, guild_config)

    return guild_config


def save_config(guild_id, guild_config):
    guild_id = str(guild_id)
    data = _load_raw()
    data[guild_id] = guild_config
    _save_raw(data)


def add_watched_user(guild_id, user_id, emoji):
    config = load_config(guild_id)
    user_id = str(user_id)

    if user_id in config["watched_users"]:
        config["watched_users"][user_id]["emojis"] = [emoji]
        save_config(guild_id, config)
        return True, "Usuario actualizado: ahora reaccionará solo con ese emoji."

    if len(config["watched_users"]) >= MAX_USERS:
        return False, f"Ya hay {MAX_USERS} usuarios configurados (máximo permitido)."

    config["watched_users"][user_id] = {"emojis": [emoji], "chance": 100}
    save_config(guild_id, config)
    return True, "Usuario añadido correctamente."


def add_multi_users(guild_id, user_ids, emoji):
    config = load_config(guild_id)
    watched = config["watched_users"]

    añadidos = []
    actualizados = []
    rechazados_por_limite = []

    for user_id in user_ids:
        user_id = str(user_id)

        if user_id in watched:
            watched[user_id]["emojis"] = [emoji]
            actualizados.append(user_id)
            continue

        if len(watched) >= MAX_USERS:
            rechazados_por_limite.append(user_id)
            continue

        watched[user_id] = {"emojis": [emoji], "chance": 100}
        añadidos.append(user_id)

    save_config(guild_id, config)
    return añadidos, actualizados, rechazados_por_limite


def remove_watched_user(guild_id, user_id):
    config = load_config(guild_id)
    user_id = str(user_id)

    if user_id not in config["watched_users"]:
        return False, "Ese usuario no estaba en la lista."

    del config["watched_users"][user_id]
    save_config(guild_id, config)
    return True, "Usuario eliminado correctamente."


def edit_watched_user(guild_id, user_id, emoji):
    config = load_config(guild_id)
    user_id = str(user_id)

    if user_id not in config["watched_users"]:
        return False, "Ese usuario no está configurado. Usa /ruser para añadirlo primero."

    config["watched_users"][user_id]["emojis"] = [emoji]
    save_config(guild_id, config)
    return True, "Reacción actualizada correctamente."


def set_chance(guild_id, user_id, emoji, chance):
    config = load_config(guild_id)
    user_id = str(user_id)

    if user_id not in config["watched_users"]:
        if len(config["watched_users"]) >= MAX_USERS:
            return False, f"Ya hay {MAX_USERS} usuarios configurados (máximo permitido)."
        config["watched_users"][user_id] = {"emojis": [emoji], "chance": chance}
        save_config(guild_id, config)
        return True, f"Usuario añadido con emoji {emoji} y probabilidad {chance}%."

    config["watched_users"][user_id]["chance"] = chance
    save_config(guild_id, config)
    return True, f"Probabilidad actualizada a {chance}%. (El emoji indicado se ignoró porque el usuario ya estaba configurado; usa /redit o /rmulti para cambiar sus emojis)."


def set_multi(guild_id, user_id, emojis_list):
    config = load_config(guild_id)
    user_id = str(user_id)

    if user_id not in config["watched_users"]:
        if len(config["watched_users"]) >= MAX_USERS:
            return False, f"Ya hay {MAX_USERS} usuarios configurados (máximo permitido)."
        config["watched_users"][user_id] = {"emojis": emojis_list, "chance": 100}
        save_config(guild_id, config)
        return True, "Usuario añadido con esa lista de emojis (probabilidad 100%)."

    config["watched_users"][user_id]["emojis"] = emojis_list
    save_config(guild_id, config)
    return True, "Lista de emojis actualizada correctamente."


def toggle_pause(guild_id):
    config = load_config(guild_id)
    config["paused"] = not config["paused"]
    save_config(guild_id, config)
    return config["paused"]


def is_dm_notified(user_id):
    data = _load_raw()
    return str(user_id) in data.get("dm_notified_users", [])


def mark_dm_notified(user_id):
    data = _load_raw()
    lst = data.get("dm_notified_users", [])
    user_id = str(user_id)
    if user_id not in lst:
        lst.append(user_id)
    data["dm_notified_users"] = lst
    _save_raw(data)