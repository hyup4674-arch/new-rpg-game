import streamlit as st
import json
import random
import os
import time

# 페이지 설정
st.set_page_config(page_title="AI 텍스트 RPG", page_icon="⚔️", layout="wide")

# 순수 외부 파일(game_data.json) 로드 함수 (캐시 제거로 파일 수정 즉시 반영)
def load_game_data():
    if os.path.exists("game_data.json"):
        try:
            with open("game_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data
        except Exception as e:
            st.error(f"game_data.json 파일 로드 중 오류 발생: {e}")
    return {}

game_data = load_game_data()

# 설정값 단축 참조
SETTINGS = game_data.get("settings", {
    "combat_delay": 3,
    "min_damage": 1,
    "random_variance_min": -2,
    "random_variance_max": 2,
    "magic_damage_multiplier": 0.5,
    "default_mp_cost": 5,
    "hp_potion_heal": 50,
    "mp_potion_heal": 30,
    "inn_cost": 50,
    "hire_cost": 100
})

# 자동 저장 함수
def save_game_state():
    if st.session_state.get("game_started", False):
        save_data = {
            "game_started": st.session_state.game_started,
            "char_name": st.session_state.char_name,
            "char_class": st.session_state.char_class,
            "stats": st.session_state.stats,
            "level": st.session_state.level,
            "exp": st.session_state.exp,
            "max_exp": st.session_state.max_exp,
            "stat_points": st.session_state.stat_points,
            "hp": st.session_state.hp,
            "max_hp": st.session_state.max_hp,
            "mp": st.session_state.mp,
            "max_mp": st.session_state.max_mp,
            "gold": st.session_state.gold,
            "companions": st.session_state.companions,
            "in_combat": st.session_state.in_combat,
            "combat_monster": st.session_state.combat_monster,
            "combat_turn": st.session_state.combat_turn,
            "last_combat_msg": st.session_state.last_combat_msg,
            "player_double_damage": st.session_state.player_double_damage,
            "equipped_weapon": st.session_state.equipped_weapon,
            "equipped_armor": st.session_state.equipped_armor,
            "equipped_shield": st.session_state.equipped_shield,
            "inventory": st.session_state.inventory,
            "item_inventory": st.session_state.item_inventory,
            "logs": st.session_state.logs,
            "last_mp_regen_time": st.session_state.last_mp_regen_time
        }
        try:
            with open("autosave.json", "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

# 세션 상태 초기화 및 자동 불러오기
if "initialized" not in st.session_state:
    loaded_auto = False
    if os.path.exists("autosave.json"):
        try:
            with open("autosave.json", "r", encoding="utf-8") as f:
                auto_data = json.load(f)
                if auto_data and auto_data.get("game_started", False):
                    for k, v in auto_data.items():
                        st.session_state[k] = v
                    if "companions" not in st.session_state:
                        st.session_state.companions = []
                    if "level" not in st.session_state:
                        st.session_state.level = 1
                        st.session_state.exp = 0
                        st.session_state.max_exp = 100
                        st.session_state.stat_points = 0
                    if "last_mp_regen_time" not in st.session_state:
                        st.session_state.last_mp_regen_time = time.time()
                    st.session_state["initialized"] = True
                    loaded_auto = True
        except Exception as e:
            pass

    if not loaded_auto:
        st.session_state.game_started = False
        st.session_state.char_name = ""
        st.session_state.char_class = ""
        st.session_state.stats = {"str": 5, "dex": 5, "vit": 5, "int": 5}
        st.session_state.level = 1
        st.session_state.exp = 0
        st.session_state.max_exp = 100
        st.session_state.stat_points = 0
        st.session_state.bonus_points = 10
        st.session_state.hp = 100
        st.session_state.max_hp = 100
        st.session_state.mp = 50
        st.session_state.max_mp = 50
        st.session_state.gold = 100
        
        st.session_state.companions = [] 
        st.session_state.in_combat = False
        st.session_state.combat_monster = None
        st.session_state.combat_turn = "player"
        st.session_state.last_combat_msg = "<span style='color: #31333F;'>⚔️ 사냥터에서 사냥을 시작하면 실시간 전투 결과가 여기에 표시됩니다.</span>"
        st.session_state.player_double_damage = False
        
        st.session_state.equipped_weapon = None
        st.session_state.equipped_armor = None
        st.session_state.equipped_shield = None
        
        st.session_state.inventory = {"hp_potion": 2, "mp_potion": 2}
        st.session_state.item_inventory = []
        st.session_state.last_mp_regen_time = time.time()
        
        st.session_state.logs = ["모험의 세계에 오신 것을 환영합니다! 캐릭터를 생성해주세요."]
        st.session_state.initialized = True
else:
    if "item_inventory" not in st.session_state:
        st.session_state.item_inventory = []
    if "in_combat" not in st.session_state:
        st.session_state.in_combat = False
    if "combat_monster" not in st.session_state:
        st.session_state.combat_monster = None
    if "combat_turn" not in st.session_state:
        st.session_state.combat_turn = "player"
    if "last_combat_msg" not in st.session_state:
        st.session_state.last_combat_msg = "<span style='color: #31333F;'>⚔️ 전투 대기 중...</span>"
    if "companions" not in st.session_state:
        st.session_state.companions = []
    if "player_double_damage" not in st.session_state:
        st.session_state.player_double_damage = False
    if "level" not in st.session_state:
        st.session_state.level = 1
        st.session_state.exp = 0
        st.session_state.max_exp = 100
        st.session_state.stat_points = 0
    if "last_mp_regen_time" not in st.session_state:
        st.session_state.last_mp_regen_time = time.time()

def add_log(msg):
    st.session_state.logs.insert(0, msg)
    if len(st.session_state.logs) > 30:
        st.session_state.logs.pop()
    save_game_state()

# 능력치 계산 함수 (플레이어)
def get_derived_stats(stats=None, char_class=None, eq_weapon=None, eq_armor=None, eq_shield=None):
    if stats is None: stats = st.session_state.stats
    if char_class is None: char_class = st.session_state.char_class
    if eq_weapon is None: eq_weapon = st.session_state.get("equipped_weapon")
    if eq_armor is None: eq_armor = st.session_state.get("equipped_armor")
    if eq_shield is None: eq_shield = st.session_state.get("equipped_shield")
    
    weapon_atk = 0
    if eq_weapon:
        if eq_weapon in game_data.get("weapons", {}):
            weapon_atk = game_data["weapons"][eq_weapon]["attack"]
        elif eq_weapon in game_data.get("daggers", {}):
            weapon_atk = game_data["daggers"][eq_weapon]["attack"]
        elif eq_weapon in game_data.get("spells", {}):
            weapon_atk = game_data["spells"][eq_weapon]["base_damage"] + stats["int"] // 2
            
    armor_def = 0
    if eq_armor:
        if eq_armor in game_data.get("armors", {}):
            armor_def = game_data["armors"][eq_armor]["defense"]
            
    shield_def = 0
            
    total_atk = stats["str"] + weapon_atk
    total_def = (stats["dex"] // 2) + armor_def + shield_def
    max_hp = 50 + (stats["vit"] * 10)
    max_mp = 30 + (stats["int"] * 8)
    
    return total_atk, total_def, max_hp, max_mp

# 능력치 계산 함수 (동료)
def get_companion_derived_stats(comp):
    stats = comp['stats']
    eq_w = comp.get('equipped_weapon')
    eq_a = comp.get('equipped_armor')
    
    weapon_atk = 0
    if eq_w:
        if eq_w in game_data.get("weapons", {}):
            weapon_atk = game_data["weapons"][eq_w]["attack"]
        elif eq_w in game_data.get("daggers", {}):
            weapon_atk = game_data["daggers"][eq_w]["attack"]
        elif eq_w in game_data.get("spells", {}):
            weapon_atk = game_data["spells"][eq_w]["base_damage"] + stats["int"] // 2
            
    armor_def = 0
    if eq_a:
        if eq_a in game_data.get("armors", {}):
            armor_def = game_data["armors"][eq_a]["defense"]
            
    total_atk = stats["str"] + weapon_atk
    total_def = (stats["dex"] // 2) + armor_def
    max_hp = 50 + (stats["vit"] * 10)
    max_mp = 30 + (stats["int"] * 8)
    return total_atk, total_def, max_hp, max_mp

# 마나 자동 회복 함수 (5초에 1씩 일괄 적용, 맥스면 회복 안 함)
def check_and_apply_mp_regen():
    now = time.time()
    elapsed = now - st.session_state.last_mp_regen_time
    ticks = int(elapsed // 5)
    if ticks > 0:
        st.session_state.last_mp_regen_time += ticks * 5
        _, _, _, max_mp = get_derived_stats()
        if st.session_state.mp < max_mp:
            added = min(ticks, max_mp - st.session_state.mp)
            st.session_state.mp += added
            
        for comp in st.session_state.companions:
            _, _, _, c_max_mp = get_companion_derived_stats(comp)
            if comp['mp'] < c_max_mp:
                added = min(ticks, c_max_mp - comp['mp'])
                comp['mp'] += added

# 경험치 및 레벨업 처리 함수
def add_exp(exp_amount):
    st.session_state.exp += exp_amount
    leveled_up = False
    while st.session_state.exp >= st.session_state.max_exp:
        st.session_state.exp -= st.session_state.max_exp
        st.session_state.level += 1
        st.session_state.max_exp = int(st.session_state.max_exp * 1.5)
        st.session_state.stat_points += 4 
        leveled_up = True
        add_log(f"🎉 플레이어가 레벨 업 했습니다! (현재 레벨: {st.session_state.level}) 스탯 포인트 4개가 지급되었습니다.")
        
    for comp in st.session_state.companions:
        comp['exp'] += exp_amount
        while comp['exp'] >= comp['max_exp']:
            comp['exp'] -= comp['max_exp']
            comp['level'] += 1
            comp['max_exp'] = int(comp['max_exp'] * 1.5)
            comp['stat_points'] += 4
            add_log(f"🎉 동료 [{comp['name']}]이(가) 레벨 업 했습니다! (현재 레벨: {comp['level']}) 스탯 포인트 4개가 지급되었습니다.")
            
    if leveled_up:
        _, _, max_hp, max_mp = get_derived_stats()
        st.session_state.max_hp = max_hp
        st.session_state.hp = max_hp
        st.session_state.max_mp = max_mp
        st.session_state.mp = max_mp

# 아이템 카테고리 및 능력치 텍스트 헬퍼
ITEM_CATEGORY_SLOTS = {
    "weapons": "weapon",
    "daggers": "weapon",
    "spells": "weapon",
    "armors": "armor",
    "shields": "shield"
}

def get_item_category(item_name):
    for cat in ["weapons", "daggers", "spells", "armors", "shields"]:
        if item_name in game_data.get(cat, {}):
            return cat
    return None

def get_item_value(item_name):
    cat = get_item_category(item_name)
    if not cat: return 0
    if cat in ["weapons", "daggers"]:
        return game_data[cat][item_name]["attack"]
    elif cat == "spells":
        return game_data[cat][item_name]["base_damage"]
    elif cat == "armors":
        return game_data[cat][item_name]["defense"]
    elif cat == "shields":
        sh_data = game_data[cat][item_name]
        return sh_data.get("block_rate", 30)
    return 0

def get_item_sell_price(item_name):
    cat = get_item_category(item_name)
    if not cat: return 10
    item_info = game_data.get(cat, {}).get(item_name, {})
    for key in ["sell_price", "price", "cost", "value"]:
        if key in item_info:
            price_val = item_info[key]
            if key in ["price", "cost"] and price_val > 100:
                return price_val // 2
            return price_val
    val = get_item_value(item_name)
    return max(10, val * 10)

def get_shield_block_chance(shield_name):
    if not shield_name:
        return 0.0
    sh_data = game_data.get("shields", {}).get(shield_name, {})
    br = sh_data.get("block_rate", 30)
    if br > 1:
        br = br / 100.0
    return br if br > 0 else 0.0

def get_item_requirements(item_name):
    cat = get_item_category(item_name)
    if not cat: return 0, 0
    item_data = game_data.get(cat, {}).get(item_name, {})
    min_str = item_data.get("min_str", item_data.get("req_str", item_data.get("required_str", 0)))
    min_vit = item_data.get("min_vit", item_data.get("req_vit", item_data.get("required_vit", 0)))
    
    if min_str == 0 and min_vit == 0:
        val = get_item_value(item_name)
        if cat in ["weapons", "daggers"]:
            if val >= 10:
                min_str = val // 2
        elif cat in ["armors", "shields"]:
            if val >= 10:
                min_vit = val // 2
    return min_str, min_vit

def can_equip(char_class, item_name, stats=None):
    cat = get_item_category(item_name)
    if not cat: return False, None, "존재하지 않는 아이템입니다."
    
    if char_class == "힐러":
        return False, None, "[힐러] 직업은 장비를 착용할 수 없습니다."
        
    rules = game_data.get("class_equipment_rules", {}).get(char_class, {})
    allowed = rules.get("allowed_categories", [])
    if cat not in allowed:
        return False, None, f"[{char_class}] 직업은 이 장비 카테고리를 착용할 수 없습니다."
        
    if stats:
        min_str, min_vit = get_item_requirements(item_name)
        current_str = stats.get("str", 0)
        current_vit = stats.get("vit", 0)
        
        if current_str < min_str:
            return False, None, f"힘(STR)이 부족합니다! (필요 힘: {min_str}, 현재 힘: {current_str})"
        if current_vit < min_vit:
            return False, None, f"체력(VIT)이 부족합니다! (필요 체력: {min_vit}, 현재 체력: {current_vit})"
            
    return True, ITEM_CATEGORY_SLOTS[cat], "착용 가능"

def get_item_stat_text(item_name, item_type):
    if not item_name:
        return "없음"
    cat = get_item_category(item_name)
    if cat in ["weapons", "daggers"]:
        return f"{item_name} (공격력: {game_data[cat][item_name]['attack']})"
    elif cat == "spells":
        return f"{item_name} (마법력: {game_data[cat][item_name]['base_damage']})"
    elif cat == "armors":
        return f"{item_name} (방어력: {game_data[cat][item_name]['defense']})"
    elif cat == "shields":
        sh_data = game_data[cat][item_name]
        br = sh_data.get("block_rate", 30)
        return f"{item_name} (블록율: {br}%)"
    return item_name

def process_auto_equip():
    inventory_items = list(st.session_state.item_inventory)
    c_class = st.session_state.char_class
    p_stats = st.session_state.stats
    
    for itm in inventory_items:
        is_ok, slot, _ = can_equip(c_class, itm, p_stats)
        if is_ok:
            curr = None
            if slot == "weapon": curr = st.session_state.equipped_weapon
            elif slot == "armor": curr = st.session_state.equipped_armor
            elif slot == "shield": curr = st.session_state.equipped_shield
            
            if curr == itm:
                continue
                
            curr_val = get_item_value(curr) if curr else 0
            new_val = get_item_value(itm)
            
            if new_val > curr_val:
                if slot == "weapon": st.session_state.equipped_weapon = itm
                elif slot == "armor": st.session_state.equipped_armor = itm
                elif slot == "shield": st.session_state.equipped_shield = itm
                if itm in st.session_state.item_inventory:
                    st.session_state.item_inventory.remove(itm)
                if curr:
                    st.session_state.item_inventory.append(curr)
                add_log(f"✨ 플레이어가 인벤토리에서 더 우수한 **{itm}**(을)를 자동 장착했습니다.")

    for comp in st.session_state.companions:
        if comp['type'] == "힐러":
            continue
        c_type = comp['type']
        c_stats = comp['stats']
        inventory_items_comp = list(st.session_state.item_inventory)
        for itm in inventory_items_comp:
            is_ok, slot, _ = can_equip(c_type, itm, c_stats)
            if is_ok:
                curr = None
                if slot == "weapon": curr = comp["equipped_weapon"]
                elif slot == "armor": curr = comp["equipped_armor"]
                elif slot == "shield": comp["equipped_shield"]
                
                if curr == itm:
                    continue
                    
                curr_val = get_item_value(curr) if curr else 0
                new_val = get_item_value(itm)
                
                if new_val > curr_val:
                    if slot == "weapon": comp["equipped_weapon"] = itm
                    elif slot == "armor": comp["equipped_armor"] = itm
                    elif slot == "shield": comp["equipped_shield"] = itm
                    if itm in st.session_state.item_inventory:
                        st.session_state.item_inventory.remove(itm)
                    if curr:
                        st.session_state.item_inventory.append(curr)
                    add_log(f"✨ 동료 [{comp['name']}]이(가) 인벤토리에서 더 우수한 **{itm}**(을)를 자동 장착했습니다.")
    save_game_state()

def handle_item_drop(m_atk, m_def):
    if random.random() >= 0.50:
        return 
        
    drop_type = random.choice(["weapon_or_spell", "armor_or_shield"])
    dropped_item = None
    
    if drop_type == "weapon_or_spell":
        candidates = []
        for cat in ["weapons", "daggers", "spells"]:
            for w_n, w_d in game_data.get(cat, {}).items():
                val = w_d.get("attack") or w_d.get("base_damage", 0)
                if val == m_atk: candidates.append(w_n)
        if candidates: dropped_item = random.choice(candidates)
    else:
        candidates = []
        for cat in ["armors", "shields"]:
            for a_n, a_d in game_data.get(cat, {}).items():
                if cat == "armors" and a_d.get("defense") == m_def:
                    candidates.append(a_n)
                elif cat == "shields":
                    candidates.append(a_n)
        if candidates: dropped_item = random.choice(candidates)
            
    if dropped_item:
        add_log(f"🎁 필드 드롭 아이템 발견: **{dropped_item}**!")
        st.session_state.item_inventory.append(dropped_item)
        process_auto_equip()

if not game_data:
    st.error("⚠️ 루트 디렉토리에 `game_data.json` 파일이 존재하지 않거나 내용이 비어 있습니다.")

# 사이드바: 저장 및 불러오기 메뉴
with st.sidebar:
    st.title("💾 게임 데이터 관리")
    
    if st.session_state.game_started:
        save_data = {
            "game_started": st.session_state.game_started,
            "char_name": st.session_state.char_name,
            "char_class": st.session_state.char_class,
            "stats": st.session_state.stats,
            "level": st.session_state.level,
            "exp": st.session_state.exp,
            "max_exp": st.session_state.max_exp,
            "stat_points": st.session_state.stat_points,
            "hp": st.session_state.hp,
            "max_hp": st.session_state.max_hp,
            "mp": st.session_state.mp,
            "max_mp": st.session_state.max_mp,
            "gold": st.session_state.gold,
            "companions": st.session_state.companions,
            "in_combat": st.session_state.in_combat,
            "combat_monster": st.session_state.combat_monster,
            "combat_turn": st.session_state.combat_turn,
            "last_combat_msg": st.session_state.last_combat_msg,
            "player_double_damage": st.session_state.player_double_damage,
            "equipped_weapon": st.session_state.equipped_weapon,
            "equipped_armor": st.session_state.equipped_armor,
            "equipped_shield": st.session_state.equipped_shield,
            "inventory": st.session_state.inventory,
            "item_inventory": st.session_state.item_inventory,
            "logs": st.session_state.logs,
            "last_mp_regen_time": st.session_state.last_mp_regen_time
        }
        json_bytes = json.dumps(save_data, ensure_ascii=False, indent=4).encode("utf-8")
        st.download_button(
            label="📥 내 기기에 게임 저장하기",
            data=json_bytes,
            file_name=f"rpg_save_{st.session_state.char_name}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.markdown("---")
        if st.button("🔄 캐릭터 초기화 (새로 시작)", type="secondary", use_container_width=True):
            if os.path.exists("autosave.json"):
                try:
                    os.remove("autosave.json")
                except:
                    pass
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("게임이 초기화되었습니다. 새로 시작합니다.")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    uploaded_save_file = st.file_uploader("📂 저장 파일 불러오기", type=["json"])
    if uploaded_save_file is not None:
        try:
            loaded_data = json.load(uploaded_save_file)
            for k, v in loaded_data.items():
                st.session_state[k] = v
            if "companions" not in st.session_state:
                st.session_state.companions = []
            if "level" not in st.session_state:
                st.session_state.level = 1
                st.session_state.exp = 0
                st.session_state.max_exp = 100
                st.session_state.stat_points = 0
            if "last_mp_regen_time" not in st.session_state:
                st.session_state.last_mp_regen_time = time.time()
            st.session_state["initialized"] = True
            save_game_state()
            st.success("🎉 게임 데이터를 성공적으로 불러왔습니다!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"저장 파일을 읽는 중 오류가 발생했습니다: {e}")

# 캐릭터 생성 화면
if not st.session_state.game_started:
    st.title("⚔️ AI 텍스트 RPG: 모험의 시작")
    
    col1, col2 = st.columns(2)
    with col1:
        char_name = st.text_input("캐릭터 이름", value="모험가")
        char_class = st.selectbox("직업 선택", list(game_data.get("class_equipment_rules", {"전사":{}, "암살자":{}, "마법사":{}}).keys()))
        
        st.markdown("---")
        st.subheader("스탯 분배 (기본 각 5점)")
        
        if "alloc" not in st.session_state:
            st.session_state.alloc = {"str": 0, "dex": 0, "vit": 0, "int": 0}
            
        s_str = st.slider("힘 (STR)", 0, 10, st.session_state.alloc["str"], key="s_str_slider")
        s_dex = st.slider("민첩 (DEX)", 0, 10, st.session_state.alloc["dex"], key="s_dex_slider")
        s_vit = st.slider("체력 (VIT)", 0, 10, st.session_state.alloc["vit"], key="s_vit_slider")
        s_int = st.slider("지능 (INT)", 0, 10, st.session_state.alloc["int"], key="s_int_slider")
        
        current_sum = s_str + s_dex + s_vit + s_int
        remaining = 10 - current_sum
        st.write(f"남은 보너스 포인트: **{remaining}** / 10")
        
        if current_sum <= 10:
            st.session_state.alloc["str"] = s_str
            st.session_state.alloc["dex"] = s_dex
            st.session_state.alloc["vit"] = s_vit
            st.session_state.alloc["int"] = s_int
        else:
            st.error("보너스 포인트 10점을 초과할 수 없습니다!")

    with col2:
        st.info("""
        ### 🛡️ 직업별 특징 및 착용 제한
        * **전사 (Warrior)**: 일반 무기, 방패, 갑옷 장착 가능 (단, 충분한 힘/체력 필요)
        * **암살자 (Assassin)**: 단검, 갑옷 장착 가능
        * **마법사 (Mage)**: 마법(스펠), 갑옷 장착 가능
        *(힘 또는 체력이 부족할 경우 상위 장비를 착용할 수 없습니다.)*
        """)
        
        if st.button("🚀 모험 시작하기", type="primary", use_container_width=True):
            if current_sum != 10:
                st.warning("보너스 포인트 10점을 모두 분배해주세요!")
            elif not game_data:
                st.error("game_data.json 데이터가 로드되지 않았습니다.")
            else:
                st.session_state.char_name = char_name
                st.session_state.char_class = char_class
                st.session_state.stats = {
                    "str": 5 + st.session_state.alloc["str"],
                    "dex": 5 + st.session_state.alloc["dex"],
                    "vit": 5 + st.session_state.alloc["vit"],
                    "int": 5 + st.session_state.alloc["int"]
                }
                st.session_state.level = 1
                st.session_state.exp = 0
                st.session_state.max_exp = 100
                st.session_state.stat_points = 0
                st.session_state.companions = []
                
                _, _, max_hp, max_mp = get_derived_stats()
                st.session_state.max_hp = max_hp
                st.session_state.hp = max_hp
                st.session_state.max_mp = max_mp
                st.session_state.mp = max_mp
                st.session_state.last_mp_regen_time = time.time()
                
                rules = game_data.get("class_equipment_rules", {}).get(char_class, {}).get("allowed_categories", [])
                init_stats = st.session_state.stats
                for cat in rules:
                    if cat in game_data and game_data[cat]:
                        for first_item in game_data[cat].keys():
                            ok, slot, _ = can_equip(char_class, first_item, init_stats)
                            if ok:
                                if slot == "weapon": st.session_state.equipped_weapon = first_item
                                elif slot == "armor": st.session_state.equipped_armor = first_item
                                elif slot == "shield": st.session_state.equipped_shield = first_item
                                break
                    
                st.session_state.game_started = True
                add_log(f"[{char_name}] ({char_class}) 모험가가 탄생했습니다!")
                save_game_state()
                st.rerun()

else:
    # 턴 시작 전 마나 자동 회복 체크
    check_and_apply_mp_regen()
    process_auto_equip()
    total_atk, total_def, max_hp, max_mp = get_derived_stats()
    
    with st.sidebar:
        st.markdown("---")
        st.title(f"👤 {st.session_state.char_name}")
        st.caption(f"직업: **{st.session_state.char_class}** | 레벨: **Lv.{st.session_state.level}**")
        st.text(f"EXP: {st.session_state.exp} / {st.session_state.max_exp}")
        st.markdown("---")
        
        st.subheader("📊 스탯")
        st.text(f"힘 (STR): {st.session_state.stats['str']}")
        st.text(f"민첩 (DEX): {st.session_state.stats['dex']}")
        st.text(f"체력 (VIT): {st.session_state.stats['vit']}")
        st.text(f"지능 (INT): {st.session_state.stats['int']}")
        
        if st.session_state.stat_points > 0:
            st.info(f"사용 가능한 스탯 포인트: **{st.session_state.stat_points}**")
            col_sp1, col_sp2 = st.columns(2)
            with col_sp1:
                if st.button("힘 +1"):
                    st.session_state.stats['str'] += 1
                    st.session_state.stat_points -= 1
                    _, _, max_hp, max_mp = get_derived_stats()
                    st.session_state.max_hp = max_hp
                    save_game_state()
                    st.rerun()
                if st.button("민첩 +1"):
                    st.session_state.stats['dex'] += 1
                    st.session_state.stat_points -= 1
                    save_game_state()
                    st.rerun()
            with col_sp2:
                if st.button("체력 +1"):
                    st.session_state.stats['vit'] += 1
                    st.session_state.stat_points -= 1
                    _, _, max_hp, max_mp = get_derived_stats()
                    st.session_state.max_hp = max_hp
                    st.session_state.hp = min(max_hp, st.session_state.hp + 10)
                    save_game_state()
                    st.rerun()
                if st.button("지능 +1"):
                    st.session_state.stats['int'] += 1
                    st.session_state.stat_points -= 1
                    _, _, _, max_mp = get_derived_stats()
                    st.session_state.max_mp = max_mp
                    st.session_state.mp = min(max_mp, st.session_state.mp + 8)
                    save_game_state()
                    st.rerun()

        st.markdown("---")
        st.text(f"⚔️ 공격력: {total_atk}")
        st.text(f"🛡️ 방어력: {total_def}")
        st.text(f"❤️ HP: {st.session_state.hp} / {max_hp}")
        st.text(f"💙 MP: {st.session_state.mp} / {max_mp}")
        st.text(f"💰 소지금: {st.session_state.gold} G")
        
        if st.session_state.companions:
            st.markdown("---")
            st.subheader("🤝 동료 관리")
            for c_idx, comp in enumerate(st.session_state.companions):
                c_atk, c_def, c_max_hp, c_max_mp = get_companion_derived_stats(comp)
                st.markdown(f"**[{c_idx+1}] {comp['name']} (Lv.{comp['level']})**")
                st.text(f"EXP: {comp['exp']} / {comp['max_exp']}")
                st.text(f"❤️ HP: {comp['hp']} / {c_max_hp} | 💙 MP: {comp['mp']} / {c_max_mp}")
                st.text(f"스탯 - 힘:{comp['stats']['str']} 민:{comp['stats']['dex']} 체:{comp['stats']['vit']} 지:{comp['stats']['int']}")
                
                if comp['stat_points'] > 0:
                    st.info(f"동료 스탯 포인트: {comp['stat_points']}")
                    col_csp1, col_csp2 = st.columns(2)
                    with col_csp1:
                        if st.button(f"동료 힘+1_{c_idx}"):
                            comp['stats']['str'] += 1
                            comp['stat_points'] -= 1
                            save_game_state()
                            st.rerun()
                        if st.button(f"동료 민+1_{c_idx}"):
                            comp['stats']['dex'] += 1
                            comp['stat_points'] -= 1
                            save_game_state()
                            st.rerun()
                    with col_csp2:
                        if st.button(f"동료 체+1_{c_idx}"):
                            comp['stats']['vit'] += 1
                            comp['stat_points'] -= 1
                            _, _, c_max_hp, _ = get_companion_derived_stats(comp)
                            comp['max_hp'] = c_max_hp
                            comp['hp'] = min(c_max_hp, comp['hp'] + 10)
                            save_game_state()
                            st.rerun()
                        if st.button(f"동료 지+1_{c_idx}"):
                            comp['stats']['int'] += 1
                            comp['stat_points'] -= 1
                            _, _, _, c_max_mp = get_companion_derived_stats(comp)
                            comp['max_mp'] = c_max_mp
                            comp['mp'] = min(c_max_mp, comp['mp'] + 8)
                            save_game_state()
                            st.rerun()
                
                if st.button(f"동료 해고하기 [{comp['name']}]", key=f"dismiss_comp_{c_idx}"):
                    st.session_state.companions.pop(c_idx)
                    add_log(f"동료 [{comp['name']}]을(를) 방출했습니다.")
                    save_game_state()
                    st.rerun()
                st.markdown("---")
        
        st.markdown("---")
        st.subheader("🎒 장착 장비 및 능력치")
        st.markdown("**[플레이어]**")
        st.text(f"무기/마법: {get_item_stat_text(st.session_state.equipped_weapon, 'weapon')}")
        st.text(f"갑옷: {get_item_stat_text(st.session_state.equipped_armor, 'armor')}")
        st.text(f"방패: {get_item_stat_text(st.session_state.equipped_shield, 'shield')}")

        for c_idx, comp in enumerate(st.session_state.companions):
            st.markdown(f"**[동료: {comp['name']}]**")
            if comp['type'] == "힐러":
                st.text("힐러 직업은 장비를 착용하지 않습니다.")
            else:
                st.text(f"무기/마법: {get_item_stat_text(comp.get('equipped_weapon'), 'weapon')}")
                st.text(f"갑옷: {get_item_stat_text(comp.get('equipped_armor'), 'armor')}")
                st.text(f"방패: {get_item_stat_text(comp.get('equipped_shield'), 'shield')}")
        
        st.markdown("---")
        st.subheader("🧪 인벤토리 및 포션")
        st.text(f"HP 포션: {st.session_state.inventory['hp_potion']}개")
        st.text(f"MP 포션: {st.session_state.inventory['mp_potion']}개")
        
        st.markdown("---")
        st.subheader("🎒 보유 중인 추가 장비")
        if st.session_state.item_inventory:
            for idx, itm in enumerate(list(st.session_state.item_inventory)):
                stat_desc = get_item_stat_text(itm, "")
                sell_p = get_item_sell_price(itm)
                st.text(f"- {stat_desc} (판매가: {sell_p} G)")
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    if st.button("플레이어 착용", key=f"equip_p_{idx}"):
                        is_ok, slot, reason = can_equip(st.session_state.char_class, itm, st.session_state.stats)
                        if is_ok:
                            curr = None
                            if slot == "weapon": curr = st.session_state.equipped_weapon
                            elif slot == "armor": curr = st.session_state.equipped_armor
                            elif slot == "shield": curr = st.session_state.equipped_shield
                            
                            if slot == "weapon": st.session_state.equipped_weapon = itm
                            elif slot == "armor": st.session_state.equipped_armor = itm
                            elif slot == "shield": st.session_state.equipped_shield = itm
                            
                            st.session_state.item_inventory.remove(itm)
                            if curr:
                                st.session_state.item_inventory.append(curr)
                            add_log(f"✨ 플레이어가 **{itm}**(을)를 직접 착용했습니다.")
                            save_game_state()
                            st.rerun()
                        else:
                            st.warning(f"⚠️ {reason}")
                
                if st.session_state.companions:
                    comp_options = {f"{c['name']} ({c_i})": c_i for c_i, c in enumerate(st.session_state.companions) if c['type'] != "힐러"}
                    if comp_options:
                        selected_comp_key = st.selectbox("동료 선택", list(comp_options.keys()), key=f"sel_comp_{idx}")
                        comp_idx = comp_options[selected_comp_key]
                        with col_e2:
                            comp = st.session_state.companions[comp_idx]
                            if st.button("동료 착용", key=f"equip_c_{idx}_{comp_idx}"):
                                is_ok, slot, reason = can_equip(comp["type"], itm, comp['stats'])
                                if is_ok:
                                    curr = None
                                    if slot == "weapon": curr = comp["equipped_weapon"]
                                    elif slot == "armor": curr = comp["equipped_armor"]
                                    elif slot == "shield": comp["equipped_shield"]
                                    
                                    if slot == "weapon": comp["equipped_weapon"] = itm
                                    elif slot == "armor": comp["equipped_armor"] = itm
                                    elif slot == "shield": comp["equipped_shield"] = itm
                                    
                                    st.session_state.item_inventory.remove(itm)
                                    if curr:
                                        st.session_state.item_inventory.append(curr)
                                    add_log(f"✨ 동료 [{comp['name']}]이(가) **{itm}**(을)를 직접 착용했습니다.")
                                    save_game_state()
                                    st.rerun()
                                else:
                                    st.warning(f"⚠️ {reason}")
                st.markdown("---")
        else:
            st.text("보유 중인 추가 장비 없음")
            
        st.markdown("---")
        potion_targets = ["플레이어"] + [f"동료: {c['name']}" for c in st.session_state.companions]
        potion_target = st.selectbox("포션 사용 대상 선택", potion_targets)
        
        hp_heal = SETTINGS.get("hp_potion_heal", 50)
        mp_heal = SETTINGS.get("mp_potion_heal", 30)

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("HP 포션 사용"):
                if st.session_state.inventory['hp_potion'] > 0:
                    st.session_state.inventory['hp_potion'] -= 1
                    if potion_target == "플레이어":
                        st.session_state.hp = min(max_hp, st.session_state.hp + hp_heal)
                        add_log("플레이어가 HP 포션을 사용했습니다.")
                    else:
                        comp_idx = potion_targets.index(potion_target) - 1
                        comp = st.session_state.companions[comp_idx]
                        _, _, c_max_hp, _ = get_companion_derived_stats(comp)
                        comp['hp'] = min(c_max_hp, comp['hp'] + hp_heal)
                        add_log(f"동료 {comp['name']}에게 HP 포션을 사용했습니다.")
                    save_game_state()
                    st.rerun()
                else:
                    st.warning("HP 포션 부족!")
        with col_p2:
            if st.button("MP 포션 사용"):
                if st.session_state.inventory['mp_potion'] > 0:
                    st.session_state.inventory['mp_potion'] -= 1
                    if potion_target == "플레이어":
                        st.session_state.mp = min(max_mp, st.session_state.mp + mp_heal)
                        add_log("플레이어가 MP 포션을 사용했습니다.")
                    else:
                        comp_idx = potion_targets.index(potion_target) - 1
                        comp = st.session_state.companions[comp_idx]
                        _, _, _, c_max_mp = get_companion_derived_stats(comp)
                        comp['mp'] = min(c_max_mp, comp['mp'] + mp_heal)
                        add_log(f"동료 {comp['name']}에게 MP 포션을 사용했습니다.")
                    save_game_state()
                    st.rerun()
                else:
                    st.warning("MP 포션 부족!")

    # 메인 화면
    st.title("🗺️ 텍스트 RPG 세계관")
    
    combat_delay = SETTINGS.get("combat_delay", 3)

    if st.session_state.in_combat:
        st.subheader(f"⚔️ 실시간 전투 진행 중 ({combat_delay}초 간격)")
        cm = st.session_state.combat_monster
        
        cols = st.columns(2 + len(st.session_state.companions))
        with cols[0]:
            p_pct = int(max(0.0, min(1.0, st.session_state.hp / float(max_hp))) * 100)
            st.markdown(f"""
            <div style="margin-bottom: 5px; font-size: 15px; font-weight: bold;">👤 {st.session_state.char_name}</div>
            <div style="background-color: #e0e0e0; border-radius: 12px; height: 26px; width: 100%; overflow: hidden;">
                <div style="background-color: #ff4b4b; width: {p_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 26px; font-size: 13px;">{st.session_state.hp} / {max_hp}</div>
            </div>
            """, unsafe_allow_html=True)
            
        for c_idx, comp in enumerate(st.session_state.companions):
            _, _, c_max_hp, _ = get_companion_derived_stats(comp)
            c_pct = int(max(0.0, min(1.0, comp['hp'] / float(c_max_hp))) * 100)
            with cols[1 + c_idx]:
                st.markdown(f"""
                <div style="margin-bottom: 5px; font-size: 15px; font-weight: bold;">🤝 {comp['name']}</div>
                <div style="background-color: #e0e0e0; border-radius: 12px; height: 26px; width: 100%; overflow: hidden;">
                    <div style="background-color: #ffa100; width: {c_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 26px; font-size: 13px;">{comp['hp']} / {c_max_hp}</div>
                </div>
                """, unsafe_allow_html=True)
                
        with cols[-1]:
            m_pct = int(max(0.0, min(1.0, cm['hp'] / float(cm['max_hp'])) * 100))
            st.markdown(f"""
            <div style="margin-bottom: 5px; font-size: 15px; font-weight: bold;">👹 {cm['name']}</div>
            <div style="background-color: #e0e0e0; border-radius: 12px; height: 26px; width: 100%; overflow: hidden;">
                <div style="background-color: #1c83e1; width: {m_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 26px; font-size: 13px;">{cm['hp']} / {cm['max_hp']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### ⚡ 최근 전투 결과")
        
        st.markdown(f"""
        <div style="padding: 25px; background-color: #f0f2f6; border-radius: 12px; border: 2px solid #d6d6d8; font-size: 2.5em; line-height: 1.2; text-align: center; font-weight: bold;">
            {st.session_state.last_combat_msg}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        min_dmg = SETTINGS.get("min_damage", 1)
        var_min = SETTINGS.get("random_variance_min", -2)
        var_max = SETTINGS.get("random_variance_max", 2)
        magic_mult = SETTINGS.get("magic_damage_multiplier", 0.5)
        mp_cost = SETTINGS.get("default_mp_cost", 5)

        turn = st.session_state.combat_turn
        
        if turn == "player":
            c_class = st.session_state.char_class
            base_attack_power = total_atk
            is_magic_attack = False
            
            best_spell_dmg = 0
            best_spell_name = None
            for sp_n, sp_d in game_data.get("spells", {}).items():
                if c_class == "마법사" or st.session_state.equipped_weapon == sp_n:
                    s_dmg = sp_d["base_damage"] + (st.session_state.stats["int"] // 2)
                    if s_dmg > best_spell_dmg:
                        best_spell_dmg = s_dmg
                        best_spell_name = sp_n
            
            if best_spell_name and st.session_state.mp >= mp_cost:
                base_attack_power = best_spell_dmg
                st.session_state.mp -= mp_cost
                is_magic_attack = True
            
            dmg_to_m = max(min_dmg, base_attack_power - cm['def'] + random.randint(var_min, var_max))
            
            if is_magic_attack or get_item_category(st.session_state.equipped_weapon) == "spells":
                dmg_to_m = max(min_dmg, int(dmg_to_m * magic_mult))
                
            double_msg = ""
            if st.session_state.player_double_damage:
                dmg_to_m *= 2
                st.session_state.player_double_damage = False
                double_msg = " (적 중심 상실: 데미지 2배!)"
                
            cm['hp'] -= dmg_to_m
            
            log_text = f"플레이어가 적을 공격 해서 {dmg_to_m} 의 피해를 입혔습니다{double_msg}"
            st.session_state.last_combat_msg = f"<span style='color: #e74c3c;'>{log_text}</span>"
            add_log(log_text)
            
            if cm['hp'] <= 0:
                exp_reward = cm['atk'] * 10
                gold_reward = cm['atk'] * 5
                win_msg = f"🎉 **{cm['name']}** 처치 성공! (+{gold_reward} 골드, +{exp_reward} EXP)"
                st.session_state.last_combat_msg = f"<span style='color: #27ae60;'>{win_msg}</span>"
                add_log(win_msg)
                st.session_state.gold += gold_reward
                add_exp(exp_reward)
                st.session_state.in_combat = False
                handle_item_drop(cm['atk'], cm['def'])
                save_game_state()
                time.sleep(1)
                st.rerun()
            else:
                if len(st.session_state.companions) > 0:
                    st.session_state.combat_turn = "companion_0"
                else:
                    st.session_state.combat_turn = "monster"
                save_game_state()
                time.sleep(combat_delay)
                st.rerun()
                
        elif turn.startswith("companion_"):
            c_idx = int(turn.split("_")[1])
            if c_idx >= len(st.session_state.companions) or st.session_state.companions[c_idx]['hp'] <= 0:
                if c_idx + 1 < len(st.session_state.companions):
                    st.session_state.combat_turn = f"companion_{c_idx + 1}"
                else:
                    st.session_state.combat_turn = "monster"
                save_game_state()
                st.rerun()
            else:
                comp = st.session_state.companions[c_idx]
                c_stats = comp['stats']
                
                if comp['type'] == "힐러":
                    all_members = [{"name": st.session_state.char_name, "hp": st.session_state.hp, "max_hp": max_hp, "type": "player", "obj": None}]
                    for oth_idx, oth_c in enumerate(st.session_state.companions):
                        _, _, o_max_hp, _ = get_companion_derived_stats(oth_c)
                        all_members.append({"name": oth_c['name'], "hp": oth_c['hp'], "max_hp": o_max_hp, "type": "companion", "obj": oth_c})
                    
                    needs_healing = [m for m in all_members if (m['hp'] / m['max_hp']) < 0.8]
                    
                    if needs_healing:
                        lowest_member = min(needs_healing, key=lambda x: x['hp'] / x['max_hp'])
                        
                        if comp['mp'] >= 5:
                            comp['mp'] -= 5
                            heal_amt = c_stats["int"] + comp['level']
                            if lowest_member['type'] == "player":
                                st.session_state.hp = min(max_hp, st.session_state.hp + heal_amt)
                            else:
                                _, _, lo_max_hp, _ = get_companion_derived_stats(lowest_member['obj'])
                                lowest_member['obj']['hp'] = min(lo_max_hp, lowest_member['obj']['hp'] + heal_amt)
                                
                            log_text = f"동료 [힐러]가 힐 스킬을 시전하여 {lowest_member['name']}의 체력을 {heal_amt} 회복시켰습니다!"
                        else:
                            log_text = "동료 [힐러]의 마나가 부족하여 힐을 시전하지 못했습니다."
                    else:
                        log_text = "동료 [힐러]가 아군 전원의 체력이 80% 이상이므로 힐을 사용하지 않았습니다."
                        
                    st.session_state.last_combat_msg = f"<span style='color: #27ae60;'>{log_text}</span>"
                    add_log(log_text)
                    
                    if c_idx + 1 < len(st.session_state.companions):
                        st.session_state.combat_turn = f"companion_{c_idx + 1}"
                    else:
                        st.session_state.combat_turn = "monster"
                    save_game_state()
                    time.sleep(combat_delay)
                    st.rerun()
                else:
                    c_weapon_atk = 0
                    is_c_magic = False
                    c_spell_name = None
                    
                    if comp.get('equipped_weapon'):
                        w_name = comp['equipped_weapon']
                        cat = get_item_category(w_name)
                        if cat in ["weapons", "daggers"]:
                            c_weapon_atk = game_data[cat][w_name]["attack"]
                        elif cat == "spells":
                            c_weapon_atk = game_data["spells"][w_name]["base_damage"] + c_stats["int"] // 2
                            is_c_magic = True
                            c_spell_name = w_name
                    
                    c_total_atk = c_stats["str"] + c_weapon_atk
                    if comp['type'] == "마법사" and comp['mp'] >= mp_cost:
                        comp['mp'] -= mp_cost
                        c_total_atk += int(c_stats["int"] * 1.5)
                        is_c_magic = True
                        if not c_spell_name:
                            for sp_n in game_data.get("spells", {}):
                                c_spell_name = sp_n
                                break
                            if not c_spell_name:
                                c_spell_name = "화염구"
                    
                    dmg_to_m = max(min_dmg, c_total_atk - cm['def'] + random.randint(var_min, var_max))
                    if is_c_magic or get_item_category(comp.get('equipped_weapon')) == "spells":
                        dmg_to_m = max(min_dmg, int(dmg_to_m * magic_mult))
                        
                    cm['hp'] -= dmg_to_m
                    
                    if is_c_magic or get_item_category(comp.get('equipped_weapon')) == "spells":
                        spell_title = c_spell_name if c_spell_name else "마법"
                        log_text = f"동료 [{comp['name']}]이(가) {spell_title} 마법을 시전하여 {dmg_to_m} 데미지를 입혔습니다."
                    else:
                        log_text = f"동료 [{comp['name']}]이(가) 적을 공격하여 {dmg_to_m} 의 피해를 입혔습니다."
                        
                    st.session_state.last_combat_msg = f"<span style='color: #d4ac0d;'>{log_text}</span>"
                    add_log(log_text)
                    
                    if cm['hp'] <= 0:
                        exp_reward = cm['atk'] * 10
                        gold_reward = cm['atk'] * 5
                        win_msg = f"🎉 **{cm['name']}** 처치 성공! (+{gold_reward} 골드, +{exp_reward} EXP)"
                        st.session_state.last_combat_msg = f"<span style='color: #27ae60;'>{win_msg}</span>"
                        add_log(win_msg)
                        st.session_state.gold += gold_reward
                        add_exp(exp_reward)
                        st.session_state.in_combat = False
                        handle_item_drop(cm['atk'], cm['def'])
                        save_game_state()
                        time.sleep(1)
                        st.rerun()
                    else:
                        if c_idx + 1 < len(st.session_state.companions):
                            st.session_state.combat_turn = f"companion_{c_idx + 1}"
                        else:
                            st.session_state.combat_turn = "monster"
                        save_game_state()
                        time.sleep(combat_delay)
                        st.rerun()
                
        elif turn == "monster":
            monster_atk = cm['atk']
            
            # --- [전사 우선 타겟팅 로직 추가부] ---
            valid_targets = []
            if st.session_state.hp > 0:
                valid_targets.append({
                    "type": "player", 
                    "name": st.session_state.char_name, 
                    "class": st.session_state.char_class
                })
            for comp in st.session_state.companions:
                if comp['hp'] > 0 and comp['type'] != "힐러":
                    valid_targets.append({
                        "type": "companion", 
                        "obj": comp, 
                        "name": comp['name'], 
                        "class": comp['type']
                    })
            
            # 전사 클래스가 존재하는지 필터링
            warrior_targets = [t for t in valid_targets if t.get("class") == "전사"]
            
            if warrior_targets:
                # 전사가 있다면 전사들 중 무작위로 우선 공격
                chosen_target = random.choice(warrior_targets)
            else:
                # 전사가 없거나 죽었으면 생존한 전체 대상 중 랜덤 공격
                chosen_target = random.choice(valid_targets)
            # ---------------------------------------------
            
            if chosen_target["type"] == "companion":
                comp = chosen_target["obj"]
                c_stats = comp['stats']
                c_armor_def = game_data["armors"][comp['equipped_armor']]["defense"] if comp.get('equipped_armor') and comp['equipped_armor'] in game_data.get("armors", {}) else 0
                c_total_def = (c_stats['dex'] // 2) + c_armor_def
                
                c_evade_chance = min(0.40, c_stats['dex'] * 0.02)
                c_block_chance = get_shield_block_chance(comp.get('equipped_shield'))
                
                c_evaded = random.random() < c_evade_chance
                c_blocked = False
                if not c_evaded:
                    c_blocked = random.random() < c_block_chance
                    
                if c_evaded:
                    dmg_to_c = 0
                elif c_blocked:
                    raw_dmg = max(min_dmg, monster_atk - c_total_def + random.randint(-1, 1))
                    dmg_to_c = max(0, raw_dmg // 2)
                else:
                    dmg_to_c = max(min_dmg, monster_atk - c_total_def + random.randint(-1, 1))
                    
                comp['hp'] -= dmg_to_c
                
                if c_evaded:
                    log_text = f"적이 동료 [{comp['name']}]을(를) 공격했으나 회피했습니다 (0 데미지)"
                elif c_blocked:
                    log_text = f"적이 동료 [{comp['name']}]을(를) 공격하여 블록 성공, {dmg_to_c} 의 데미지를 입혔습니다"
                else:
                    log_text = f"적이 동료 [{comp['name']}]을(를) 공격하여 {dmg_to_c} 의 데미지를 입혔습니다"
                    
                st.session_state.last_combat_msg = f"<span style='color: #2980b9;'>{log_text}</span>"
                add_log(log_text)
                
                if comp['hp'] <= 0:
                    death_msg = f"💀 동료 [{comp['name']}]이(가) 전투 중 사망하여 쓰러졌습니다..."
                    add_log(death_msg)
                    st.session_state.companions.remove(comp)
                
                st.session_state.combat_turn = "player"
                save_game_state()
                time.sleep(combat_delay)
                st.rerun()
                
            else:
                dex_val = st.session_state.stats['dex']
                p_evade_chance = min(0.40, dex_val * 0.02)
                p_block_chance = get_shield_block_chance(st.session_state.equipped_shield)
                
                p_evaded = random.random() < p_evade_chance
                p_blocked = False
                if not p_evaded:
                    p_blocked = random.random() < p_block_chance
                    
                if p_evaded:
                    dmg_to_p = 0
                elif p_blocked:
                    raw_dmg = max(min_dmg, monster_atk - total_def + random.randint(-1, 1))
                    dmg_to_p = max(0, raw_dmg // 2)
                else:
                    dmg_to_p = max(min_dmg, monster_atk - total_def + random.randint(-1, 1))
                    
                st.session_state.hp -= dmg_to_p
                
                if p_evaded:
                    st.session_state.player_double_damage = True
                    log_text = "적이 플레이어를 공격했으나 회피했습니다 (적 중심 상실! 다음 공격 데미지 2배)"
                elif p_blocked:
                    st.session_state.player_double_damage = True
                    log_text = f"적이 플레이어를 공격하여 블록 성공, {dmg_to_p} 의 데미지를 입었습니다 (적 중심 상실!)"
                else:
                    log_text = f"적이 플레이어를 공격하여 {dmg_to_p} 의 데미지를 입혔습니다"
                    
                st.session_state.last_combat_msg = f"<span style='color: #2980b9;'>{log_text}</span>"
                add_log(log_text)
                    
                if st.session_state.hp <= 0:
                    lose_msg = "💀 전투에서 패배하여 사망했습니다... 마을로 부활합니다. (장비 소실!)"
                    st.session_state.last_combat_msg = f"<span style='color: #e74c3c;'>{lose_msg}</span>"
                    add_log(lose_msg)
                    st.session_state.hp = max_hp
                    st.session_state.mp = max_mp
                    st.session_state.equipped_weapon = None
                    st.session_state.equipped_armor = None
                    st.session_state.equipped_shield = None
                    st.session_state.in_combat = False
                    save_game_state()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.combat_turn = "player"
                    save_game_state()
                    time.sleep(combat_delay)
                    st.rerun()

    else:
        tab1, tab2, tab3 = st.tabs(["🌲 사냥터", "🛒 상점", "🏨 여관"])
        
        with tab1:
            st.subheader("사냥터 선택")
            h_grounds = game_data.get("hunting_grounds", {})
            if not h_grounds:
                st.warning("game_data.json에 사냥터 데이터가 없습니다.")
            else:
                selected_hg = st.selectbox("사냥터를 선택하세요", list(h_grounds.keys()))
                
                if selected_hg:
                    hg_info = h_grounds[selected_hg]
                    st.info(f"**설명:** {hg_info['desc']} (몬스터 공격력: {hg_info['min_atk']} ~ {hg_info['max_atk']})")
                    
                    if st.button("⚔️ 사냥 시작!", type="primary"):
                        monsters = game_data.get("monsters", {})
                        valid_monsters = [
                            (m_name, m_data) for m_name, m_data in monsters.items() 
                            if hg_info['min_atk'] <= m_data['attack'] <= hg_info['max_atk']
                        ]
                        
                        if not valid_monsters:
                            st.error("해당 사냥터 범위에 일치하는 몬스터가 없습니다.")
                        else:
                            m_name, m_data = random.choice(valid_monsters)
                            st.session_state.combat_monster = {
                                "name": m_name,
                                "hp": m_data['hp'],
                                "max_hp": m_data['hp'],
                                "atk": m_data['attack'],
                                "def": m_data['defense']
                            }
                            st.session_state.combat_turn = "player"
                            st.session_state.in_combat = True
                            start_msg = f"야생의 **{m_name}** 출현!"
                            st.session_state.last_combat_msg = f"<span style='color: #31333F;'>{start_msg}</span>"
                            add_log(start_msg)
                            save_game_state()
                            st.rerun()

        with tab2:
            st.subheader("🛒 잡화 및 장비 상점")
            st.info("💡 체력 포션과 마나 포션은 상점에서 판매하지 않습니다.")
            
            st.markdown("---")
            st.subheader("💰 인벤토리 아이템 판매")
            st.write("인벤토리에 보유 중인 추가 장비를 상점에 판매하여 골드로 바꿀 수 있습니다.")
            
            if st.session_state.item_inventory:
                for idx, itm in enumerate(list(st.session_state.item_inventory)):
                    sell_p = get_item_sell_price(itm)
                    col_i1, col_i2 = st.columns([3, 1])
                    with col_i1:
                        st.text(f"• {get_item_stat_text(itm, '')} | 판매가: {sell_p} G")
                    with col_i2:
                        if st.button("판매하기", key=f"shop_sell_{idx}_{itm}"):
                            st.session_state.item_inventory.remove(itm)
                            st.session_state.gold += sell_p
                            add_log(f"💰 상점에 **{itm}**(을)를 판매하여 {sell_p} 골드를 획득했습니다.")
                            save_game_state()
                            st.rerun()
            else:
                st.info("판매할 수 있는 추가 장비가 인벤토리에 없습니다.")

        with tab3:
            st.subheader("🏨 여관 & 동료 고용소")
            inn_cost = SETTINGS.get("inn_cost", 50)
            hire_cost = SETTINGS.get("hire_cost", 100)

            st.write(f"여관 휴식 요금: **{inn_cost} G** (체력 및 마나 완전 회복)")
            if st.button("여관에서 휴식하기", type="primary"):
                if st.session_state.gold >= inn_cost:
                    st.session_state.gold -= inn_cost
                    st.session_state.hp = max_hp
                    st.session_state.mp = max_mp
                    for comp in st.session_state.companions:
                        _, _, c_max_hp, c_max_mp = get_companion_derived_stats(comp)
                        comp['hp'] = c_max_hp
                        comp['mp'] = c_max_mp
                    add_log("여관에서 휴식하여 플레이어와 모든 동료의 HP와 MP가 완전히 회복되었습니다.")
                    save_game_state()
                    st.rerun()
                else:
                    st.warning(f"여관비({inn_cost} G)가 부족합니다!")
            
            st.markdown("---")
            st.subheader(f"🤝 동료 고용소 (최대 2명 고용 가능 / 고용비: {hire_cost} G)")
            comp_type_selected = st.selectbox("고용할 동료 선택", [
                "힘전사 (힘10, 체5, 지5, 민5)", 
                "체력전사 (힘5, 체10, 지5, 민5)", 
                "도적 (힘5, 체5, 지5, 민10)", 
                "마법사 (힘5, 체5, 지10, 민5)",
                "힐러 (힘5, 지10, 민5, 지능10 - 공격 불가, 힐 스킬 전용)"
            ])
            
            if st.button("동료 고용하기"):
                if len(st.session_state.companions) >= 2:
                    st.warning("동료는 최대 2명까지만 고용할 수 있습니다!")
                elif st.session_state.gold < hire_cost:
                    st.warning(f"고용 비용({hire_cost} G)가 부족합니다!")
                else:
                    st.session_state.gold -= hire_cost
                    
                    if "힘전사" in comp_type_selected:
                        c_name = "힘전사"
                        c_type = "전사"
                        c_stats = {"str": 10, "dex": 5, "vit": 5, "int": 5}
                    elif "체력전사" in comp_type_selected:
                        c_name = "체력전사"
                        c_type = "전사"
                        c_stats = {"str": 5, "dex": 5, "vit": 10, "int": 5}
                    elif "도적" in comp_type_selected:
                        c_name = "도적"
                        c_type = "암살자"
                        c_stats = {"str": 5, "dex": 10, "vit": 5, "int": 5}
                    elif "마법사" in comp_type_selected:
                        c_name = "마법사"
                        c_type = "마법사"
                        c_stats = {"str": 5, "dex": 5, "vit": 5, "int": 10}
                    else:
                        c_name = "힐러"
                        c_type = "힐러"
                        c_stats = {"str": 5, "dex": 5, "vit": 5, "int": 10}
                        
                    c_max_hp = 50 + (c_stats["vit"] * 10)
                    c_max_mp = 30 + (c_stats["int"] * 8)
                    
                    new_comp = {
                        "name": c_name,
                        "type": c_type,
                        "stats": c_stats,
                        "level": 1,
                        "exp": 0,
                        "max_exp": 100,
                        "stat_points": 0,
                        "hp": c_max_hp,
                        "max_hp": c_max_hp,
                        "mp": c_max_mp,
                        "max_mp": c_max_mp,
                        "equipped_weapon": None,
                        "equipped_armor": None,
                        "equipped_shield": None
                    }
                    
                    st.session_state.companions.append(new_comp)
                    process_auto_equip()
                    add_log(f"🤝 든든한 동료 [{c_name}](을)를 고용했습니다!")
                    save_game_state()
                    st.rerun()

    st.markdown("---")
    st.subheader("📜 실시간 모험 기록")
    for log in st.session_state.logs:
        st.text(log)
