import streamlit as st
import json
import os
import time

st.set_page_config(page_title="Furytoad IUT", layout="wide")

# Version (inscrite au moment du commit) — utile pour vérifier la version déployée
VERSION = "f79e91d"

SAVE_FILE = "savegame.json"

UPGRADES = {
    "Petite Pioche": {"cost": 10, "bonus": 1, "requires": [], "pos": (2, 0), "icon": "⛏️", "category": "tools"},
    
    "Grande Pioche": {"cost": 50, "bonus": 5, "requires": ["Petite Pioche"], "pos": (0, 1), "icon": "🪓", "category": "tools"},
    "Pelle": {"cost": 50, "bonus": 4, "requires": ["Petite Pioche"], "pos": (2, 1), "icon": "🔧", "category": "tools"},
    "Dynamite": {"cost": 75, "bonus": 8, "requires": ["Petite Pioche"], "pos": (4, 1), "icon": "🧨", "category": "explosives"},
    
    "Foreuse": {"cost": 150, "bonus": 15, "requires": ["Grande Pioche"], "pos": (0, 2), "icon": "🔩", "category": "machines"},
    "Excavatrice": {"cost": 200, "bonus": 20, "requires": ["Pelle"], "pos": (2, 2), "icon": "🚜", "category": "machines"},
    "TNT": {"cost": 250, "bonus": 25, "requires": ["Dynamite"], "pos": (4, 2), "icon": "💥", "category": "explosives"},
    
    "Machine": {"cost": 500, "bonus": 50, "requires": ["Foreuse"], "pos": (0, 3), "icon": "⚙️", "category": "machines"},
    "Tunnelier": {"cost": 600, "bonus": 60, "requires": ["Excavatrice"], "pos": (2, 3), "icon": "🚇", "category": "machines"},
    "Bombe Nucléaire": {"cost": 800, "bonus": 80, "requires": ["TNT"], "pos": (4, 3), "icon": "☢️", "category": "explosives"},
    
    "Usine": {"cost": 2000, "bonus": 200, "requires": ["Machine"], "pos": (0, 4), "icon": "🏭", "category": "industry"},
    "Mine Profonde": {"cost": 2500, "bonus": 250, "requires": ["Tunnelier"], "pos": (2, 4), "icon": "⬇️", "category": "mining"},
    "Laser": {"cost": 3000, "bonus": 300, "requires": ["Bombe Nucléaire"], "pos": (4, 4), "icon": "🔴", "category": "tech"},
    
    "Super Usine": {"cost": 8000, "bonus": 800, "requires": ["Usine"], "pos": (0, 5), "icon": "🏗️", "category": "industry"},
    "Noyau Terrestre": {"cost": 10000, "bonus": 1000, "requires": ["Mine Profonde"], "pos": (2, 5), "icon": "🌋", "category": "mining"},
    "Rayon Plasma": {"cost": 12000, "bonus": 1200, "requires": ["Laser"], "pos": (4, 5), "icon": "⚡", "category": "tech"},
    
    "Usine Robotique": {"cost": 30000, "bonus": 3000, "requires": ["Super Usine"], "pos": (0, 6), "icon": "🤖", "category": "industry"},
    "Extracteur Magma": {"cost": 40000, "bonus": 4000, "requires": ["Noyau Terrestre"], "pos": (2, 6), "icon": "🔥", "category": "mining"},
    "Canon Orbital": {"cost": 50000, "bonus": 5000, "requires": ["Rayon Plasma"], "pos": (4, 6), "icon": "🛰️", "category": "tech"},
    
    "IA Minière": {"cost": 100000, "bonus": 10000, "requires": ["Usine Robotique", "Extracteur Magma"], "pos": (1, 7), "icon": "🧠", "category": "ultimate"},
    "Station Spatiale": {"cost": 150000, "bonus": 15000, "requires": ["Canon Orbital"], "pos": (4, 7), "icon": "🚀", "category": "space"},
    
    "Colonie Lunaire": {"cost": 300000, "bonus": 30000, "requires": ["Station Spatiale"], "pos": (4, 8), "icon": "🌙", "category": "space"},
    "Méga-Complexe": {"cost": 400000, "bonus": 40000, "requires": ["IA Minière"], "pos": (1, 8), "icon": "🌆", "category": "ultimate"},
    
    "Mine Astéroïde": {"cost": 800000, "bonus": 80000, "requires": ["Colonie Lunaire", "Méga-Complexe"], "pos": (2, 9), "icon": "☄️", "category": "space"},
    
    "Dyson Sphere": {"cost": 2000000, "bonus": 200000, "requires": ["Mine Astéroïde"], "pos": (2, 10), "icon": "☀️", "category": "ultimate"},
    
    "Univers Parallèle": {"cost": 10000000, "bonus": 1000000, "requires": ["Dyson Sphere"], "pos": (2, 11), "icon": "🌌", "category": "ultimate"},
    # Nouveaux ajouts pour l'arbre
    "Réacteur d'Énergie Infinie": {"cost": 3000000, "bonus": 300000, "requires": ["Dyson Sphere"], "pos": (0, 12), "icon": "🔋", "category": "ultimate"},
    "Moteur Interdimensionnel": {"cost": 5000000, "bonus": 500000, "requires": ["Univers Parallèle"], "pos": (2, 12), "icon": "🛸", "category": "tech"},
    "Architecte de Réalités": {"cost": 8000000, "bonus": 800000, "requires": ["Moteur Interdimensionnel", "Réacteur d'Énergie Infinie"], "pos": (4, 12), "icon": "🏛️", "category": "ultimate"},
    "Collecteur Quantique": {"cost": 1200000, "bonus": 120000, "requires": ["Dyson Sphere"], "pos": (1, 13), "icon": "🧲", "category": "tech"},
    "Réseau d'IA Globale": {"cost": 2500000, "bonus": 250000, "requires": ["Collecteur Quantique"], "pos": (3, 13), "icon": "🌐", "category": "industry"},
}

PRESTIGE_UPGRADES = {
    "Boost de Prestige I": {"cost": 1, "bonus_multiplier": 0.1, "requires": [], "pos": (0, 0), "icon": "⭐", "category": "prestige"},
    "Boost de Prestige II": {"cost": 3, "bonus_multiplier": 0.2, "requires": ["Boost de Prestige I"], "pos": (0, 1), "icon": "✨", "category": "prestige"},
    "Boost de Prestige III": {"cost": 8, "bonus_multiplier": 0.3, "requires": ["Boost de Prestige II"], "pos": (0, 2), "icon": "💫", "category": "prestige"},
    
    "Collecteur de Points": {"cost": 2, "points_gain": 5, "requires": [], "pos": (2, 0), "icon": "📦", "category": "prestige"},
    "Collecteur Amélioré": {"cost": 6, "points_gain": 15, "requires": ["Collecteur de Points"], "pos": (2, 1), "icon": "📫", "category": "prestige"},
    "Collecteur Ultime": {"cost": 15, "points_gain": 40, "requires": ["Collecteur Amélioré"], "pos": (2, 2), "icon": "📪", "category": "prestige"},
    
    "Accélérateur Passif": {"cost": 4, "passive_gain": 1, "requires": [], "pos": (4, 0), "icon": "⚡", "category": "prestige"},
    "Accélérateur Renforcé": {"cost": 10, "passive_gain": 3, "requires": ["Accélérateur Passif"], "pos": (4, 1), "icon": "⚙️", "category": "prestige"},
    "Accélérateur Extrême": {"cost": 25, "passive_gain": 8, "requires": ["Accélérateur Renforcé"], "pos": (4, 2), "icon": "🔥", "category": "prestige"},
    
    "Multiplicateur Stellaire": {"cost": 50, "bonus_multiplier": 1.0, "requires": ["Boost de Prestige III", "Collecteur Ultime", "Accélérateur Extrême"], "pos": (2, 3), "icon": "🌟", "category": "prestige"},
}

# Arbre alternatif (débloquer après 5 renaissances)
MAGIC_TREE_UPGRADES = {
    "Magie Naturelle I": {"cost": 2, "bonus": 10, "requires": [], "pos": (0, 0), "icon": "🍀", "category": "magic"},
    "Magie Naturelle II": {"cost": 5, "bonus": 25, "requires": ["Magie Naturelle I"], "pos": (0, 1), "icon": "🌿", "category": "magic"},
    "Magie Naturelle III": {"cost": 12, "bonus": 60, "requires": ["Magie Naturelle II"], "pos": (0, 2), "icon": "🌳", "category": "magic"},
    
    "Cristaux Magiques I": {"cost": 3, "bonus": 15, "requires": [], "pos": (2, 0), "icon": "💎", "category": "magic"},
    "Cristaux Magiques II": {"cost": 8, "bonus": 40, "requires": ["Cristaux Magiques I"], "pos": (2, 1), "icon": "🔮", "category": "magic"},
    "Cristaux Magiques III": {"cost": 20, "bonus": 100, "requires": ["Cristaux Magiques II"], "pos": (2, 2), "icon": "✨", "category": "magic"},
    
    "Ancien Pouvoir I": {"cost": 4, "bonus": 20, "requires": [], "pos": (4, 0), "icon": "🦉", "category": "magic"},
    "Ancien Pouvoir II": {"cost": 10, "bonus": 50, "requires": ["Ancien Pouvoir I"], "pos": (4, 1), "icon": "🧙", "category": "magic"},
    "Ancien Pouvoir III": {"cost": 25, "bonus": 150, "requires": ["Ancien Pouvoir II"], "pos": (4, 2), "icon": "👑", "category": "magic"},
    
    "Harmonie Suprême": {"cost": 100, "bonus": 500, "requires": ["Magie Naturelle III", "Cristaux Magiques III", "Ancien Pouvoir III"], "pos": (2, 3), "icon": "🌈", "category": "magic"},
}

def load_game():
    default_data = {
        "points": 0,
        "points_per_click": 1,
        "unlocked": [],
        "last_idle_time": time.time(),
        "prestige_points": 0,
        "prestige_level": 0,
        "prestige_unlocked": [],
        "magic_unlocked": [],
        "total_earned": 0,
        "highest_points": 0,
        "theme": "dark",
        "tree_type": "normal",
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                loaded = json.load(f)
                for key in default_data:
                    if key not in loaded:
                        loaded[key] = default_data[key]
                return loaded
        except:
            pass
    return default_data

def save_game(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def export_save_json(data):
    """Retourne la sauvegarde sous forme JSON formaté pour téléchargement, avec validation."""
    try:
        if not isinstance(data, dict):
            raise ValueError("Les données à exporter doivent être un dictionnaire.")
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Erreur export: {e}"}, ensure_ascii=False)


def import_save_from_bytes(b: bytes):
    """Tente de charger une sauvegarde depuis des bytes, retourne tuple (ok, data_or_error)."""
    try:
        text = b.decode("utf-8")
        loaded = json.loads(text)
        # Validation stricte
        if not isinstance(loaded, dict):
            return False, "Format invalide : la racine doit être un objet JSON."
        required_keys = {"points", "points_per_click", "unlocked"}
        if not required_keys.issubset(set(loaded.keys())):
            return False, f"Fichier manquant des clés essentielles : {', '.join(required_keys - set(loaded.keys()))}."
        # Vérification des types
        if not isinstance(loaded["points"], int) or not isinstance(loaded["points_per_click"], int) or not isinstance(loaded["unlocked"], list):
            return False, "Types de données invalides dans la sauvegarde."
        return True, loaded
    except Exception as e:
        return False, f"Erreur lors du parsing JSON : {e}"

def init_session_state():
    if "game_data" not in st.session_state:
        st.session_state.game_data = load_game()
    if "last_save" not in st.session_state:
        st.session_state.last_save = time.time()

def get_game_data():
    return st.session_state.game_data

def calculate_idle_points():
    data = get_game_data()
    current_time = time.time()
    last_time = data.get("last_idle_time", current_time)
    elapsed_seconds = int(current_time - last_time)
    if elapsed_seconds > 0:
        multiplier = get_prestige_multiplier(data)
        idle_points = int(elapsed_seconds * data["points_per_click"] * multiplier)
        # Ajouter les gains passifs de prestige
        passive_gain = 0
        if "Accélérateur Passif" in data.get("prestige_unlocked", []):
            passive_gain += 1 * elapsed_seconds
        if "Accélérateur Renforcé" in data.get("prestige_unlocked", []):
            passive_gain += 3 * elapsed_seconds
        if "Accélérateur Extrême" in data.get("prestige_unlocked", []):
            passive_gain += 8 * elapsed_seconds
        data["prestige_points"] = data.get("prestige_points", 0) + int(passive_gain)
        data["points"] += idle_points
        data["total_earned"] = data.get("total_earned", 0) + idle_points
        if data["points"] > data.get("highest_points", 0):
            data["highest_points"] = data["points"]
        data["last_idle_time"] = current_time
        save_game(data)
        return idle_points
    return 0

def click():
    data = get_game_data()
    multiplier = get_prestige_multiplier(data)
    gained = int(data["points_per_click"] * multiplier)
    data["points"] += gained
    data["total_earned"] = data.get("total_earned", 0) + gained
    if data["points"] > data.get("highest_points", 0):
        data["highest_points"] = data["points"]
    data["last_idle_time"] = time.time()
    save_game(data)

def get_prestige_multiplier(data):
    """Calcule le multiplicateur de prestige basé sur les améliorations débloquées."""
    multiplier = 1.0
    if "Boost de Prestige I" in data.get("prestige_unlocked", []):
        multiplier += 0.1
    if "Boost de Prestige II" in data.get("prestige_unlocked", []):
        multiplier += 0.2
    if "Boost de Prestige III" in data.get("prestige_unlocked", []):
        multiplier += 0.3
    if "Multiplicateur Stellaire" in data.get("prestige_unlocked", []):
        multiplier += 1.0
    # Bonus magique
    magic_bonus = len(data.get("magic_unlocked", [])) * 0.05  # 5% par upgrade magique débloquée
    return multiplier + magic_bonus

def calculate_prestige_reward(data):
    """Calcule combien de points de prestige le joueur obtiendrait en renaissant.
    Formule simple : 1 point de prestige pour chaque tranche de 100000 points totaux gagnés.
    Utilise le meilleur des points actuels et total_earned pour encourager progression.
    """
    base = max(data.get("points", 0), data.get("highest_points", 0), data.get("total_earned", 0))
    reward = int(base // 100000)
    return reward

def buy_upgrade(name):
    data = get_game_data()
    upgrade = UPGRADES[name]
    
    if name in data["unlocked"]:
        return False, "Déjà acheté!"
    
    requirements_met = all(req in data["unlocked"] for req in upgrade["requires"])
    if not requirements_met:
        return False, f"Débloque d'abord: {', '.join(upgrade['requires'])}"
    
    if data["points"] < upgrade["cost"]:
        return False, f"Pas assez de points! Il te faut {upgrade['cost']} points."
    
    data["points"] -= upgrade["cost"]
    data["points_per_click"] += upgrade["bonus"]
    data["unlocked"].append(name)
    save_game(data)
    return True, f"+{upgrade['bonus']} points par clic!"

def is_upgrade_available(name):
    data = get_game_data()
    if name in data["unlocked"]:
        return "owned"
    upgrade = UPGRADES[name]
    requirements_met = all(req in data["unlocked"] for req in upgrade["requires"])
    if requirements_met:
        return "available"
    return "locked"

def is_prestige_upgrade_available(name):
    data = get_game_data()
    if name in data.get("prestige_unlocked", []):
        return "owned"
    upgrade = PRESTIGE_UPGRADES[name]
    requirements_met = all(req in data.get("prestige_unlocked", []) for req in upgrade["requires"])
    if requirements_met:
        return "available"
    return "locked"

def buy_prestige_upgrade(name):
    data = get_game_data()
    upgrade = PRESTIGE_UPGRADES[name]
    
    if name in data.get("prestige_unlocked", []):
        return False, "Déjà acheté!"
    
    requirements_met = all(req in data.get("prestige_unlocked", []) for req in upgrade["requires"])
    if not requirements_met:
        return False, f"Débloque d'abord: {', '.join(upgrade['requires'])}"
    
    if data["prestige_points"] < upgrade["cost"]:
        return False, f"Pas assez de points de prestige! Il te faut {upgrade['cost']} pts."
    
    data["prestige_points"] -= upgrade["cost"]
    data["prestige_unlocked"] = data.get("prestige_unlocked", []) + [name]
    save_game(data)
    return True, f"Améliorations débloquées!"

def is_magic_tree_available(data):
    """Vérifie si l'arbre magique est débloqué (après 5 renaissances)."""
    return data.get("prestige_level", 0) >= 5

def buy_magic_upgrade(name):
    data = get_game_data()
    upgrade = MAGIC_TREE_UPGRADES[name]
    
    if name in data.get("magic_unlocked", []):
        return False, "Déjà acheté!"
    
    requirements_met = all(req in data.get("magic_unlocked", []) for req in upgrade["requires"])
    if not requirements_met:
        return False, f"Débloque d'abord: {', '.join(upgrade['requires'])}"
    
    if data["prestige_points"] < upgrade["cost"]:
        return False, f"Pas assez de points de prestige! Il te faut {upgrade['cost']} pts."
    
    data["prestige_points"] -= upgrade["cost"]
    data["magic_unlocked"] = data.get("magic_unlocked", []) + [name]
    save_game(data)
    return True, f"Magie débloquée!"

def is_magic_upgrade_available(name):
    data = get_game_data()
    if name in data.get("magic_unlocked", []):
        return "owned"
    upgrade = MAGIC_TREE_UPGRADES[name]
    requirements_met = all(req in data.get("magic_unlocked", []) for req in upgrade["requires"])
    if requirements_met:
        return "available"
    return "locked"

init_session_state()

idle_earned = calculate_idle_points()

# Thème (light/dark)
theme = st.session_state.get("theme", "dark")
if theme == "light":
    dark_bg = "linear-gradient(180deg, #f5f5dc 0%, #fffacd 50%, #f0e68c 100%)"
    dark_bg_container = "linear-gradient(180deg, #fffaf0 0%, #ffffe0 50%, #ffefd5 100%)"
    text_color = "#2d5016"
    text_light = "#4a7c3c"
    border_color = "#8bc34a"
    button_dark = "#7cb342"
    button_light = "#9ccc65"
else:
    dark_bg = "linear-gradient(180deg, #0d3d1f 0%, #1a5a2a 50%, #0f3620 100%)"
    dark_bg_container = "linear-gradient(180deg, #0d3d1f 0%, #1a5a2a 50%, #0f3620 100%)"
    text_color = "#d4e8d9"
    text_light = "#e8f5e9"
    border_color = "#4caf50"
    button_dark = "#558b2f"
    button_light = "#9ccc65"

st.markdown(f"""
<style>
    * {{
        font-family: 'Arial', sans-serif;
    }}
    
    /* Fond général - ambiance forestière */
    .main {{
        background: {dark_bg};
        color: {text_color};
    }}
    
    [data-testid="stAppViewContainer"] {{
        background: {dark_bg_container};
    }}
    
    /* Animations */
    @keyframes glow {{
        0% {{ box-shadow: 0 0 5px rgba(156, 204, 101, 0.3); }}
        50% {{ box-shadow: 0 0 20px rgba(156, 204, 101, 0.7); }}
        100% {{ box-shadow: 0 0 5px rgba(156, 204, 101, 0.3); }}
    }}
    
    @keyframes click-effect {{
        0% {{ transform: scale(1); opacity: 1; }}
        100% {{ transform: scale(1.5); opacity: 0; }}
    }}
    
    @keyframes grow {{
        from {{ transform: scaleY(0); }}
        to {{ transform: scaleY(1); }}
    }}
    
    /* Texte principal */
    h1, h2, h3 {{
        color: {text_light} !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        font-weight: bold;
    }}
    
    p, span, div {{
        color: {text_color};
    }}
    
    /* Boutons */
    .stButton > button {{
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        border: 2px solid {border_color};
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
    }}
    
    /* Bouton de clic principal */
    .click-btn > button {{
        background: linear-gradient(135deg, {button_dark} 0%, #33691e 100%) !important;
        color: #ffeb3b !important;
        font-size: 24px;
        padding: 30px 20px !important;
        border: 3px solid {button_light} !important;
        box-shadow: inset 0 -4px 0 rgba(0,0,0,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        animation: glow 2s ease-in-out infinite;
    }}
    
    .click-btn > button:hover {{
        background: linear-gradient(135deg, #689f38 0%, {button_dark} 100%) !important;
        box-shadow: 0 0 30px rgba(156, 204, 101, 0.8), inset 0 -4px 0 rgba(0,0,0,0.3) !important;
    }}
    
    .click-btn > button:active {{
        transform: scale(0.98);
    }}
    
    /* Buttons d'améliorations - possédé (vert foncé) */
    .owned-btn > button {{
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
        color: #c8e6c9 !important;
        border: 2px solid #4caf50 !important;
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.1);
    }}
    
    .owned-btn > button:hover {{
        background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%) !important;
    }}
    
    /* Buttons d'améliorations - disponible (or/jaune) */
    .available-btn > button {{
        background: linear-gradient(135deg, #f57f17 0%, #e65100 100%) !important;
        color: #fff3e0 !important;
        border: 2px solid #ffb74d !important;
        box-shadow: 0 0 10px rgba(255, 183, 77, 0.3);
        animation: glow 1.5s ease-in-out infinite;
    }}
    
    .available-btn > button:hover {{
        background: linear-gradient(135deg, #fbc02d 0%, #f57f17 100%) !important;
        box-shadow: 0 0 20px rgba(255, 235, 59, 0.6) !important;
    }}
    
    /* Buttons d'améliorations - verrouillé (rouge/gris) */
    .locked-btn > button {{
        background: linear-gradient(135deg, #5f5f5f 0%, #3a3a3a 100%) !important;
        color: #a0a0a0 !important;
        border: 2px solid #757575 !important;
        opacity: 0.6;
    }}
    
    .locked-btn > button:hover {{
        background: linear-gradient(135deg, #5f5f5f 0%, #3a3a3a 100%) !important;
        opacity: 0.8;
    }}
    
    /* Affichage des points */
    .points-display {{
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        border: 3px solid #4caf50;
        border-radius: 20px;
        margin-bottom: 20px;
        color: #ffeb3b;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        box-shadow: 0 8px 16px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2);
        animation: grow 0.5s ease-out;
    }}
    
    .ppc-display {{
        font-size: 20px;
        text-align: center;
        color: #b3e5fc;
        margin-bottom: 20px;
        padding: 15px;
        background: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4caf50;
        border-radius: 5px;
        font-weight: bold;
    }}
    
    /* Conteneur de l'arbre */
    .upgrade-tree {{
        background: rgba(46, 125, 50, 0.2);
        border: 2px solid #4caf50;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        animation: grow 0.6s ease-out;
    }}
    
    /* Séparateur */
    hr {{
        border-color: #4caf50 !important;
        border-top: 2px solid #4caf50 !important;
        margin: 30px 0 !important;
    }}
    
    /* Messages et info */
    .stSuccess {{
        background-color: #1b5e20 !important;
        color: #c8e6c9 !important;
        border-left: 4px solid #4caf50 !important;
        animation: click-effect 0.6s ease-out;
    }}
    
    .stWarning {{
        background-color: #f57f17 !important;
        color: #fff3e0 !important;
        border-left: 4px solid #ffb74d !important;
    }}
    
    .stInfo {{
        background-color: #0d3d1f !important;
        color: #81c784 !important;
        border-left: 4px solid #4caf50 !important;
    }}
    
    .stError {{
        background-color: #6d1f1f !important;
        color: #ffcdd2 !important;
        border-left: 4px solid #ef5350 !important;
    }}
    
    /* Caption */
    .stCaption {{
        color: #a1d581 !important;
        font-size: 14px;
        font-style: italic;
    }}
    
    /* Inputs et file uploader */
    .stFileUploader {{
        background: rgba(46, 125, 50, 0.1) !important;
        border: 2px dashed #4caf50 !important;
        border-radius: 10px !important;
    }}
    
    .stRadio > div > div {{
        color: {text_color} !important;
    }}
    
    /* JSON display */
    .stJson {{
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #4caf50 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }}
    
    /* Ligne de séparation verticale */
    .separator-line {{
        text-align: center;
        font-size: 18px;
        color: #4caf50;
        margin: 10px 0;
    }}
</style>
""", unsafe_allow_html=True)

st.title("🌳 Furytoad IUT")

# Petit badge de version fixe en coin pour vérification rapide
html = '''
<style>
.version-badge {
    position: fixed;
    top: 12px;
    right: 12px;
    background: rgba(0, 0, 0, 0.45);
    color: #fff;
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 12px;
    z-index: 9999;
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.08);
}
@media (prefers-color-scheme: light) {
    .version-badge { background: rgba(0,0,0,0.12); color: #13320f; }
}
</style>
<div class="version-badge">v'''+ VERSION + '''</div>
'''
st.markdown(html, unsafe_allow_html=True)

# Bouton de prestige et thème en haut à droite
col_title, col_theme, col_prestige = st.columns([4, 1, 1])
with col_theme:
    if st.button("🌙" if st.session_state.get("theme", "dark") == "dark" else "☀️", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.get("theme", "dark") == "dark" else "dark"
        st.rerun()

with col_prestige:
    if st.button("✨ Prestige", use_container_width=True):
        # Ouvre la pop-up (force à True)
        st.session_state.show_prestige = True
        st.rerun()

if idle_earned > 0:
    st.success(f"🎉 Tu as gagné {idle_earned} points pendant ton absence!")

data = get_game_data()

st.markdown(f'<div class="points-display">💰 Points: {data["points"]:,}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="ppc-display">⚡ {data["points_per_click"]} points par clic</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="click-btn">', unsafe_allow_html=True)
    if st.button("⛏️ CLIQUE!", key="main_click", use_container_width=True):
        click()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("🌳 Arbre d'Améliorations")

if "message" in st.session_state and "message_type" in st.session_state:
    if st.session_state.message_type == "success":
        st.success(st.session_state.message)
    else:
        st.warning(st.session_state.message)
    del st.session_state.message
    del st.session_state.message_type

rows = {}
max_col = 0
for name, upgrade in UPGRADES.items():
    row = upgrade["pos"][1]
    col = upgrade["pos"][0]
    max_col = max(max_col, col)
    if row not in rows:
        rows[row] = {}
    rows[row][col] = name

num_cols = max_col + 1

for row_idx in sorted(rows.keys()):
    cols = st.columns(num_cols)
    row_data = rows[row_idx]
    
    for col_idx in range(num_cols):
        with cols[col_idx]:
            if col_idx in row_data:
                name = row_data[col_idx]
                upgrade = UPGRADES[name]
                status = is_upgrade_available(name)
                icon = upgrade.get("icon", "")
                
                if status == "owned":
                    st.markdown('<div class="owned-btn">', unsafe_allow_html=True)
                    button_text = f"✅ {icon} {name}"
                    disabled = True
                elif status == "available":
                    st.markdown('<div class="available-btn">', unsafe_allow_html=True)
                    button_text = f"💰 {icon} {name}\n({upgrade['cost']:,} pts)"
                    disabled = False
                else:
                    st.markdown('<div class="locked-btn">', unsafe_allow_html=True)
                    button_text = f"🔒 {icon} {name}"
                    disabled = True
                
                if st.button(button_text, key=f"upgrade_{name}", disabled=disabled, use_container_width=True):
                    success, message = buy_upgrade(name)
                    st.session_state.message = message
                    st.session_state.message_type = "success" if success else "warning"
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if status != "locked":
                    st.caption(f"+{upgrade['bonus']:,} pts/clic")
            else:
                st.write("")
    
    if row_idx < max(rows.keys()):
        st.markdown("<div style='text-align: center; font-size: 18px; color: #888;'>│</div>", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Sauvegarder", use_container_width=True):
        save_game(data)
        st.success("Partie sauvegardée!")

with col2:
    if st.button("🔄 Nouvelle Partie", use_container_width=True):
        # Nouvelle partie sans supprimer les points de prestige
        preserved = {
            "prestige_points": data.get("prestige_points", 0),
            "prestige_level": data.get("prestige_level", 0),
            "prestige_unlocked": data.get("prestige_unlocked", []),
        }
        st.session_state.game_data = {"points": 0, "points_per_click": 1, "unlocked": [], "last_idle_time": time.time(), **preserved, "total_earned": 0, "highest_points": 0}
        save_game(st.session_state.game_data)
        st.rerun()

# Section Renaissances (Prestige) - Modal Streamlit
if st.session_state.get("show_prestige", False):
    potential = calculate_prestige_reward(data)

    # Use Streamlit's modal component to render a true pop-up with interactive widgets
    try:
        with st.modal("✨ Améliorations de Prestige"):
            st.markdown(f"**Points de prestige:** {data.get('prestige_points', 0)} — **Niveau:** {data.get('prestige_level', 0)}")

            if "prestige_message" in st.session_state and "prestige_message_type" in st.session_state:
                if st.session_state.prestige_message_type == "success":
                    st.success(st.session_state.prestige_message)
                else:
                    st.warning(st.session_state.prestige_message)
                del st.session_state.prestige_message
                del st.session_state.prestige_message_type

            st.subheader("🌟 Arbre de Prestige")
            prestige_rows = {}
            prestige_max_col = 0
            for name, upgrade in PRESTIGE_UPGRADES.items():
                row = upgrade["pos"][1]
                col = upgrade["pos"][0]
                prestige_max_col = max(prestige_max_col, col)
                if row not in prestige_rows:
                    prestige_rows[row] = {}
                prestige_rows[row][col] = name

            prestige_num_cols = prestige_max_col + 1
            for row_idx in sorted(prestige_rows.keys()):
                cols = st.columns(prestige_num_cols)
                row_data = prestige_rows[row_idx]
                for col_idx in range(prestige_num_cols):
                    with cols[col_idx]:
                        if col_idx in row_data:
                            name = row_data[col_idx]
                            upgrade = PRESTIGE_UPGRADES[name]
                            status = is_prestige_upgrade_available(name)
                            icon = upgrade.get("icon", "")

                            if status == "owned":
                                st.markdown('<div class="owned-btn">', unsafe_allow_html=True)
                                button_text = f"✅ {icon} {name}"
                                disabled = True
                            elif status == "available":
                                st.markdown('<div class="available-btn">', unsafe_allow_html=True)
                                button_text = f"💎 {icon} {name}\n({upgrade['cost']} pts prestige)"
                                disabled = False
                            else:
                                st.markdown('<div class="locked-btn">', unsafe_allow_html=True)
                                button_text = f"🔒 {icon} {name}"
                                disabled = True

                            if st.button(button_text, key=f"prestige_{name}", disabled=disabled, use_container_width=True):
                                success, message = buy_prestige_upgrade(name)
                                st.session_state.prestige_message = message
                                st.session_state.prestige_message_type = "success" if success else "warning"
                                st.experimental_rerun()

                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.write("")

            st.markdown("---")
            st.subheader("🔁 Effectuer une Renaissance")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Récompense de renaissance:** {potential} point(s) de prestige")
            with col2:
                if potential > 0:
                    if st.button("🔁 RENAÎTRE!", use_container_width=True, key="prestige_button_modal"):
                        reward = potential
                        data["prestige_points"] = data.get("prestige_points", 0) + reward
                        data["prestige_level"] = data.get("prestige_level", 0) + 1
                        # Réinitialiser la progression normale mais garder les améliorations de prestige
                        data["points"] = 0
                        data["points_per_click"] = 1
                        data["unlocked"] = []
                        data["last_idle_time"] = time.time()
                        data["total_earned"] = 0
                        data["highest_points"] = 0
                        save_game(data)
                        st.success(f"🎉 Tu as gagné {reward} point(s) de prestige ! Points totaux: {data['prestige_points']}")
                        st.experimental_rerun()
                else:
                    st.info("Pas encore assez de progression pour renaître. Atteins plus de points!")

            # Close button
            if st.button("✖️ Fermer", key="prestige_close_modal"):
                st.session_state.show_prestige = False
                st.experimental_rerun()
    except Exception:
        # Fallback si la version de Streamlit ne supporte pas st.modal()
        st.warning("Ton environnement Streamlit ne supporte pas les modaux natifs — la fenêtre de prestige s'affiche inline.")
        st.markdown("---")
        st.subheader("✨ Améliorations de Prestige")
        st.write(f"Points de prestige: {data.get('prestige_points', 0)} — Niveau: {data.get('prestige_level', 0)}")
        # (Le rendu inline est conservé pour compatibilité)

st.markdown("---")
st.caption(f"💡 Le jeu sauvegarde automatiquement. Tu gagnes des points même quand tu es absent! — Version: {VERSION}")

# Affichage de l'arbre magique (débloqué après 5 renaissances)
if is_magic_tree_available(data):
    st.markdown("---")
    st.subheader("🔮 Arbre Magique (Débloqué!)")
    st.markdown(f"**Accessible après {data.get('prestige_level', 0)}/5 renaissances**")
    
    if "magic_message" in st.session_state and "magic_message_type" in st.session_state:
        if st.session_state.magic_message_type == "success":
            st.success(st.session_state.magic_message)
        else:
            st.warning(st.session_state.magic_message)
        del st.session_state.magic_message
        del st.session_state.magic_message_type
    
    # Affichage de l'arbre magique
    magic_rows = {}
    magic_max_col = 0
    for name, upgrade in MAGIC_TREE_UPGRADES.items():
        row = upgrade["pos"][1]
        col = upgrade["pos"][0]
        magic_max_col = max(magic_max_col, col)
        if row not in magic_rows:
            magic_rows[row] = {}
        magic_rows[row][col] = name
    
    magic_num_cols = magic_max_col + 1
    
    for row_idx in sorted(magic_rows.keys()):
        cols = st.columns(magic_num_cols)
        row_data = magic_rows[row_idx]
        
        for col_idx in range(magic_num_cols):
            with cols[col_idx]:
                if col_idx in row_data:
                    name = row_data[col_idx]
                    upgrade = MAGIC_TREE_UPGRADES[name]
                    status = is_magic_upgrade_available(name)
                    icon = upgrade.get("icon", "")
                    
                    if status == "owned":
                        st.markdown('<div class="owned-btn">', unsafe_allow_html=True)
                        button_text = f"✅ {icon} {name}"
                        disabled = True
                    elif status == "available":
                        st.markdown('<div class="available-btn">', unsafe_allow_html=True)
                        button_text = f"💎 {icon} {name}\n({upgrade['cost']} pts prestige)"
                        disabled = False
                    else:
                        st.markdown('<div class="locked-btn">', unsafe_allow_html=True)
                        button_text = f"🔒 {icon} {name}"
                        disabled = True
                    
                    if st.button(button_text, key=f"magic_{name}", disabled=disabled, use_container_width=True):
                        success, message = buy_magic_upgrade(name)
                        st.session_state.magic_message = message
                        st.session_state.magic_message_type = "success" if success else "warning"
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write("")

# Import / Export UI amélioré
st.markdown("---")
st.subheader("🔄 Import / Export de la sauvegarde")
col_exp, col_imp = st.columns([1, 1])
with col_exp:
    export_str = export_save_json(data)
    st.download_button(
        "⬇️ Exporter la sauvegarde",
        data=export_str,
        file_name="savegame_export.json",
        mime="application/json"
    )

with col_imp:
    uploaded = st.file_uploader("⬆️ Importer une sauvegarde (.json)", type=["json"])
    if uploaded is not None:
        try:
            ok, result = import_save_from_bytes(uploaded.read())
        except Exception as e:
            ok, result = False, f"Erreur lors de l'import : {e}"
        if not ok:
            st.error(f"Erreur d'import : {result}")
        else:
            st.write("Aperçu de la sauvegarde importée :")
            st.json(result)
            mode = st.radio("Mode d'importation", ("merge", "overwrite"), index=0)
            if st.button("📥 Appliquer la sauvegarde importée"):
                default = load_game()
                if mode == "overwrite":
                    merged = default.copy()
                    merged.update(result)
                    st.session_state.game_data = merged
                    save_game(st.session_state.game_data)
                    st.success("Sauvegarde importée (overwrite).")
                    st.rerun()
                else:
                    cur = get_game_data()
                    for k, v in result.items():
                        cur[k] = v
                    for k, v in default.items():
                        if k not in cur:
                            cur[k] = v
                    st.session_state.game_data = cur
                    save_game(st.session_state.game_data)
                    st.success("Sauvegarde importée (merge).")
                    st.rerun()

st.markdown("---")
