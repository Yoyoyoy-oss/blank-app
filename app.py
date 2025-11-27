import streamlit as st
import json
import os
import time

st.set_page_config(page_title="Incremental Game Ultime", layout="wide")

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
}

def load_game():
    default_data = {"points": 0, "points_per_click": 1, "unlocked": [], "last_idle_time": time.time()}
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
        idle_points = elapsed_seconds * data["points_per_click"]
        data["points"] += idle_points
        data["last_idle_time"] = current_time
        save_game(data)
        return idle_points
    return 0

def click():
    data = get_game_data()
    data["points"] += data["points_per_click"]
    data["last_idle_time"] = time.time()
    save_game(data)

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

init_session_state()

idle_earned = calculate_idle_points()

st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    .click-btn > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 24px;
        padding: 20px;
        border: none;
    }
    .click-btn > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: scale(1.02);
    }
    .owned-btn > button {
        background-color: #90EE90 !important;
        color: black !important;
    }
    .available-btn > button {
        background-color: #FFD700 !important;
        color: black !important;
    }
    .locked-btn > button {
        background-color: #FF6347 !important;
        color: white !important;
    }
    .points-display {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .ppc-display {
        font-size: 18px;
        text-align: center;
        color: #666;
        margin-bottom: 20px;
    }
    .upgrade-tree {
        background: #f0f0f0;
        border-radius: 15px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⛏️ Incremental Game Ultime")

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
        st.session_state.game_data = {"points": 0, "points_per_click": 1, "unlocked": [], "last_idle_time": time.time()}
        save_game(st.session_state.game_data)
        st.rerun()

st.markdown("---")
st.caption("💡 Le jeu sauvegarde automatiquement. Tu gagnes des points même quand tu es absent!")
