import streamlit as st
import json
import random
import os
import time

# 페이지 설정
st.set_page_config(page_title="AI 텍스트 RPG", page_icon="⚔️", layout="wide")

# 순수 외부 파일(game_data.json) 로드 함수
@st.cache_data
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

# 자동 저장 함수
def save_game_state():
    if st.session_state.get("game_started", False):
        save_data = {
            "game_started": st.session_state.game_started,
            "char_name": st.session_state.char_name,
            "char_class": st.session_state.char_class,
            "stats": st.session_state.stats,
            "hp": st.session_state.hp,
            "max_hp": st.session_state.max_hp,
            "mp": st.session_state.mp,
            "max_mp": st.session_state.max_mp,
            "gold": st.session_state.gold,
            "companion": st.session_state.companion,
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
            "logs": st.session_state.logs
        }
        try:
            with open("autosave.json", "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

# 세션 상태 초기화 및 자동 불러오기 (새로고침, 창 닫고 재접속 시 데이터 유지)
if "initialized" not in st.session_state:
    loaded_auto = False
    if os.path.exists("autosave.json"):
        try:
            with open("autosave.json", "r", encoding="utf-8") as f:
                auto_data = json.load(f)
                if auto_data and auto_data.get("game_started", False):
                    for k, v in auto_data.items():
                        st.session_state[k] = v
                    st.session_state["initialized"] = True
                    loaded_auto = True
        except Exception as e:
            pass

    if not loaded_auto:
        st.session_state.game_started = False
        st.session_state.char_name = ""
        st.session_state.char_class = ""
        st.session_state.stats = {"str": 5, "dex": 5, "vit": 5, "int": 5}
        st.session_state.bonus_points = 10
        st.session_state.hp = 100
        st.session_state.max_hp = 100
        st.session_state.mp = 50
        st.session_state.max_mp = 50
        st.session_state.gold = 100
        
        # 동료 시스템 상태 (전투 횟수 제한 제거, 사망 시 소멸)
        st.session_state.companion = None 
        
        # 전투 상태
        st.session_state.in_combat = False
        st.session_state.combat_monster = None
        st.session_state.combat_turn = "player"
        st.session_state.last_combat_msg = "⚔️ 사냥터에서 사냥을 시작하면 실시간 전투 계산 결과가 여기에 표시됩니다."
        st.session_state.player_double_damage = False
        
        # 장착 아이템
        st.session_state.equipped_weapon = None
        st.session_state.equipped_armor = None
        st.session_state.equipped_shield = None
        
        # 인벤토리 (소모품 및 보유 아이템)
        st.session_state.inventory = {"hp_potion": 2, "mp_potion": 2}
        st.session_state.item_inventory = []
        
        # 게임 로그
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
        st.session_state.last_combat_msg = "⚔️ 전투 대기 중..."
    if "companion" not in st.session_state:
        st.session_state.companion = None
    if "player_double_damage" not in st.session_state:
        st.session_state.player_double_damage = False

def add_log(msg):
    st.session_state.logs.insert(0, msg)
    if len(st.session_state.logs) > 30:
        st.session_state.logs.pop()
    save_game_state()

# 능력치 계산 함수
def get_derived_stats():
    s = st.session_state.stats
    weapon_atk = 0
    if st.session_state.equipped_weapon:
        w_name = st.session_state.equipped_weapon
        if w_name in game_data.get("weapons", {}):
            weapon_atk = game_data["weapons"][w_name]["attack"]
        elif w_name in game_data.get("spells", {}):
            weapon_atk = game_data["spells"][w_name]["base_damage"] + s["int"] // 2
            
    armor_def = 0
    if st.session_state.equipped_armor:
        a_name = st.session_state.equipped_armor
        if a_name in game_data.get("armors", {}):
            armor_def = game_data["armors"][a_name]["defense"]
            
    shield_def = 0
    if st.session_state.equipped_shield:
        sh_name = st.session_state.equipped_shield
        if sh_name in game_data.get("shields", {}):
            shield_def = game_data["shields"][sh_name]["defense"]
            
    total_atk = s["str"] + weapon_atk
    total_def = (s["dex"] // 2) + armor_def + shield_def
    max_hp = 50 + (s["vit"] * 10)
    max_mp = 30 + (s["int"] * 8)
    
    return total_atk, total_def, max_hp, max_mp

python_daggers = [
    "낡은 단검", "나무 뾰족검", "스틸레토", "쿠커리", "커스 대거", "크리스", "카타르", 
    "어쌔신 나이프", "섀도우 단검", "독니 단검", "블러드 스틸레토", "은장 단검", 
    "룬 대거", "팬텀 나이프", "미스릴 대거", "티타늄 단검", "드래곤 이빨", "월광의 단검", "전설의 암살검", "신성한 스틸레토"
]

def get_item_stat_text(item_name, item_type):
    if not item_name:
        return "없음"
    if item_type == "weapon":
        if item_name in game_data.get("weapons", {}):
            return f"{item_name} (공격력: {game_data['weapons'][item_name]['attack']})"
        elif item_name in game_data.get("spells", {}):
            return f"{item_name} (마법력: {game_data['spells'][item_name]['base_damage']})"
    elif item_type == "armor":
        if item_name in game_data.get("armors", {}):
            return f"{item_name} (방어력: {game_data['armors'][item_name]['defense']})"
    elif item_type == "shield":
        if item_name in game_data.get("shields", {}):
            return f"{item_name} (방어력: {game_data['shields'][item_name]['defense']})"
    return item_name

# 자동 장착 처리 함수 (플레이어 우선 장착 -> 중복 장비 제외 -> 동료 순서)
def process_auto_equip():
    inventory_items = list(st.session_state.item_inventory)
    
    # 1. 플레이어 자동 장착 검사
    c_class = st.session_state.char_class
    for itm in inventory_items:
        is_weapon = itm in game_data.get("weapons", {})
        is_spell = itm in game_data.get("spells", {})
        is_armor = itm in game_data.get("armors", {})
        is_shield = itm in game_data.get("shields", {})
        is_dagger = any(itm.startswith(d) for d in python_daggers)
        
        can_equip = False
        cat = ""
        if is_weapon or is_spell:
            if c_class == "전사" and is_weapon and not is_dagger: can_equip = True; cat = "weapon"
            elif c_class == "암살자" and is_dagger: can_equip = True; cat = "weapon"
            elif c_class == "마법사" and is_spell: can_equip = True; cat = "weapon"
        elif is_armor:
            can_equip = True; cat = "armor"
        elif is_shield and c_class == "전사":
            can_equip = True; cat = "shield"
            
        if can_equip:
            curr = None
            if cat == "weapon": curr = st.session_state.equipped_weapon
            elif cat == "armor": curr = st.session_state.equipped_armor
            elif cat == "shield": curr = st.session_state.equipped_shield
            
            if curr == itm:
                continue
                
            curr_val = 0
            if curr:
                if curr in game_data.get("weapons", {}): curr_val = game_data["weapons"][curr]["attack"]
                elif curr in game_data.get("spells", {}): curr_val = game_data["spells"][curr]["base_damage"]
                elif curr in game_data.get("armors", {}): curr_val = game_data["armors"][curr]["defense"]
                elif curr in game_data.get("shields", {}): curr_val = game_data["shields"][curr]["defense"]
                
            new_val = 0
            if itm in game_data.get("weapons", {}): new_val = game_data["weapons"][itm]["attack"]
            elif itm in game_data.get("spells", {}): new_val = game_data["spells"][itm]["base_damage"]
            elif itm in game_data.get("armors", {}): new_val = game_data["armors"][itm]["defense"]
            elif itm in game_data.get("shields", {}): new_val = game_data["shields"][itm]["defense"]
            
            if new_val > curr_val:
                if cat == "weapon": st.session_state.equipped_weapon = itm
                elif cat == "armor": st.session_state.equipped_armor = itm
                elif cat == "shield": st.session_state.equipped_shield = itm
                if itm in st.session_state.item_inventory:
                    st.session_state.item_inventory.remove(itm)
                add_log(f"✨ 플레이어가 인벤토리에서 **{itm}**(을)를 자동 장착했습니다.")

    # 2. 동료 자동 장착 검사 (다음 순서)
    comp = st.session_state.companion
    if comp:
        c_type = comp["type"]
        inventory_items_comp = list(st.session_state.item_inventory)
        for itm in inventory_items_comp:
            is_weapon = itm in game_data.get("weapons", {})
            is_spell = itm in game_data.get("spells", {})
            is_armor = itm in game_data.get("armors", {})
            is_shield = itm in game_data.get("shields", {})
            is_dagger = any(itm.startswith(d) for d in python_daggers)
            
            can_equip = False
            cat = ""
            if c_type == "전사" and is_weapon and not is_dagger: can_equip = True; cat = "weapon"
            elif c_type == "도적" and is_dagger: can_equip = True; cat = "weapon"
            elif c_type == "마법사" and is_spell: can_equip = True; cat = "weapon"
            elif is_armor: can_equip = True; cat = "armor"
            elif c_type == "전사" and is_shield: can_equip = True; cat = "shield"
            
            if can_equip:
                curr = None
                if cat == "weapon": curr = comp["equipped_weapon"]
                elif cat == "armor": curr = comp["equipped_armor"]
                elif cat == "shield": curr = comp["equipped_shield"]
                
                if curr == itm:
                    continue
                    
                curr_val = 0
                if curr:
                    if curr in game_data.get("weapons", {}): curr_val = game_data["weapons"][curr]["attack"]
                    elif curr in game_data.get("spells", {}): curr_val = game_data["spells"][curr]["base_damage"]
                    elif curr in game_data.get("armors", {}): curr_val = game_data["armors"][curr]["defense"]
                    elif curr in game_data.get("shields", {}): curr_val = game_data["shields"][curr]["defense"]
                    
                new_val = 0
                if itm in game_data.get("weapons", {}): new_val = game_data["weapons"][itm]["attack"]
                elif itm in game_data.get("spells", {}): new_val = game_data["spells"][itm]["base_damage"]
                elif itm in game_data.get("armors", {}): new_val = game_data["armors"][itm]["defense"]
                elif itm in game_data.get("shields", {}): new_val = game_data["shields"][itm]["defense"]
                
                if new_val > curr_val:
                    if cat == "weapon": comp["equipped_weapon"] = itm
                    elif cat == "armor": comp["equipped_armor"] = itm
                    elif cat == "shield": comp["equipped_shield"] = itm
                    if itm in st.session_state.item_inventory:
                        st.session_state.item_inventory.remove(itm)
                    add_log(f"✨ 동료 [{comp['name']}]이(가) 인벤토리에서 **{itm}**(을)를 자동 장착했습니다.")
    save_game_state()

# 아이템 드롭 함수 (드롭율 50%)
def handle_item_drop(m_atk, m_def):
    if random.random() >= 0.50:
        return 
        
    drop_type = random.choice(["weapon_or_spell", "armor_or_shield"])
    dropped_item = None
    
    if drop_type == "weapon_or_spell":
        candidates = []
        for w_n, w_d in game_data.get("weapons", {}).items():
            if w_d["attack"] == m_atk: candidates.append(w_n)
        for sp_n, sp_d in game_data.get("spells", {}).items():
            if sp_d["base_damage"] == m_atk: candidates.append(sp_n)
        if candidates: dropped_item = random.choice(candidates)
    else:
        candidates = []
        for a_n, a_d in game_data.get("armors", {}).items():
            if a_d["defense"] == m_def: candidates.append(a_n)
        for sh_n, sh_d in game_data.get("shields", {}).items():
            if sh_d["defense"] == m_def: candidates.append(sh_n)
        if candidates: dropped_item = random.choice(candidates)
            
    if dropped_item:
        add_log(f"🎁 필드 드롭 아이템 발견: **{dropped_item}**!")
        st.session_state.item_inventory.append(dropped_item)
        process_auto_equip()

if not game_data:
    st.error("⚠️ 루트 디렉토리에 `game_data.json` 파일이 존재하지 않거나 내용이 비어 있습니다.")

# ----------------- 사이드바: 저장 및 불러오기 메뉴 -----------------
with st.sidebar:
    st.title("💾 게임 데이터 관리")
    
    if st.session_state.game_started:
        save_data = {
            "game_started": st.session_state.game_started,
            "char_name": st.session_state.char_name,
            "char_class": st.session_state.char_class,
            "stats": st.session_state.stats,
            "hp": st.session_state.hp,
            "max_hp": st.session_state.max_hp,
            "mp": st.session_state.mp,
            "max_mp": st.session_state.max_mp,
            "gold": st.session_state.gold,
            "companion": st.session_state.companion,
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
            "logs": st.session_state.logs
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
            st.session_state["initialized"] = True
            save_game_state()
            st.success("🎉 게임 데이터를 성공적으로 불러왔습니다!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"저장 파일을 읽는 중 오류가 발생했습니다: {e}")

# ----------------- UI: 캐릭터 생성 화면 -----------------
if not st.session_state.game_started:
    st.title("⚔️ AI 텍스트 RPG: 모험의 시작")
    
    col1, col2 = st.columns(2)
    with col1:
        char_name = st.text_input("캐릭터 이름", value="모험가")
        char_class = st.selectbox("직업 선택", ["전사", "암살자", "마법사"])
        
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
        ### 🛡️ 직업별 특징 및 장착 제한
        * **전사 (Warrior)**: 한손/양손무기, 방패, 갑옷 장착 가능
        * **암살자 (Assassin)**: 단검, 갑옷 장착 가능
        * **마법사 (Mage)**: 마법(스펠), 갑옷 장착 가능
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
                
                _, _, max_hp, max_mp = get_derived_stats()
                st.session_state.max_hp = max_hp
                st.session_state.hp = max_hp
                st.session_state.max_mp = max_mp
                st.session_state.mp = max_mp
                
                if char_class == "전사":
                    st.session_state.equipped_weapon = list(game_data.get("weapons", {}).keys())[0] if game_data.get("weapons") else None
                    st.session_state.equipped_armor = list(game_data.get("armors", {}).keys())[0] if game_data.get("armors") else None
                    st.session_state.equipped_shield = list(game_data.get("shields", {}).keys())[0] if game_data.get("shields") else None
                elif char_class == "암살자":
                    st.session_state.equipped_weapon = list(game_data.get("weapons", {}).keys())[0] if game_data.get("weapons") else None
                    st.session_state.equipped_armor = list(game_data.get("armors", {}).keys())[0] if game_data.get("armors") else None
                    st.session_state.equipped_shield = None
                elif char_class == "마법사":
                    st.session_state.equipped_weapon = list(game_data.get("spells", {}).keys())[0] if game_data.get("spells") else None
                    st.session_state.equipped_armor = list(game_data.get("armors", {}).keys())[0] if game_data.get("armors") else None
                    st.session_state.equipped_shield = None
                    
                st.session_state.game_started = True
                add_log(f"[{char_name}] ({char_class}) 모험가가 탄생했습니다!")
                save_game_state()
                st.rerun()

else:
    # ----------------- 게임 메인 화면 -----------------
    total_atk, total_def, max_hp, max_mp = get_derived_stats()
    
    # 좌측 사이드바: 캐릭터 및 동료 상태, 장비 및 능력치, 인벤토리/포션
    with st.sidebar:
        st.markdown("---")
        st.title(f"👤 {st.session_state.char_name}")
        st.caption(f"직업: **{st.session_state.char_class}**")
        st.markdown("---")
        
        st.subheader("📊 스탯")
        st.text(f"힘 (STR): {st.session_state.stats['str']}")
        st.text(f"민첩 (DEX): {st.session_state.stats['dex']}")
        st.text(f"체력 (VIT): {st.session_state.stats['vit']}")
        st.text(f"지능 (INT): {st.session_state.stats['int']}")
        
        st.markdown("---")
        st.text(f"⚔️ 공격력: {total_atk}")
        st.text(f"🛡️ 방어력: {total_def}")
        st.text(f"❤️ HP: {st.session_state.hp} / {max_hp}")
        st.text(f"💙 MP: {st.session_state.mp} / {max_mp}")
        st.text(f"💰 소지금: {st.session_state.gold} G")
        
        # 동료 상태 표시
        if st.session_state.companion:
            comp = st.session_state.companion
            st.markdown("---")
            st.subheader(f"🤝 동료: {comp['name']}")
            st.text(f"❤️ HP: {comp['hp']} / {comp['max_hp']}")
            st.text(f"💙 MP: {comp['mp']} / {comp['max_mp']}")
        
        st.markdown("---")
        st.subheader("🎒 장착 장비 및 능력치")
        st.markdown("**[플레이어]**")
        w_type = 'weapon' if st.session_state.equipped_weapon in game_data.get('weapons', {}) else 'spell'
        st.text(f"무기/마법: {get_item_stat_text(st.session_state.equipped_weapon, w_type)}")
        st.text(f"갑옷: {get_item_stat_text(st.session_state.equipped_armor, 'armor')}")
        st.text(f"방패: {get_item_stat_text(st.session_state.equipped_shield, 'shield')}")

        if st.session_state.companion:
            comp = st.session_state.companion
            st.markdown(f"**[동료: {comp['name']}]**")
            cw_type = 'weapon' if comp['equipped_weapon'] in game_data.get('weapons', {}) else 'spell'
            st.text(f"무기/마법: {get_item_stat_text(comp['equipped_weapon'], cw_type)}")
            st.text(f"갑옷: {get_item_stat_text(comp['equipped_armor'], 'armor')}")
            st.text(f"방패: {get_item_stat_text(comp['equipped_shield'], 'shield')}")
        
        st.markdown("---")
        st.subheader("🧪 인벤토리 및 포션")
        st.text(f"HP 포션: {st.session_state.inventory['hp_potion']}개")
        st.text(f"MP 포션: {st.session_state.inventory['mp_potion']}개")
        
        if st.session_state.item_inventory:
            st.write("**보유 중인 추가 장비:**")
            for itm in st.session_state.item_inventory:
                st.text(f"- {itm}")
        else:
            st.text("보유 중인 추가 장비 없음")
            
        st.markdown("---")
        potion_target = st.radio("포션 사용 대상 선택", ["플레이어", "동료"], horizontal=True, disabled=(st.session_state.companion is None))
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("HP 포션 사용"):
                if st.session_state.inventory['hp_potion'] > 0:
                    st.session_state.inventory['hp_potion'] -= 1
                    if potion_target == "플레이어" or st.session_state.companion is None:
                        st.session_state.hp = min(max_hp, st.session_state.hp + 50)
                        add_log("플레이어가 HP 포션을 사용했습니다.")
                    else:
                        comp = st.session_state.companion
                        comp['hp'] = min(comp['max_hp'], comp['hp'] + 50)
                        add_log(f"동료 {comp['name']}에게 HP 포션을 사용했습니다.")
                    save_game_state()
                    st.rerun()
                else:
                    st.warning("HP 포션 부족!")
        with col_p2:
            if st.button("MP 포션 사용"):
                if st.session_state.inventory['mp_potion'] > 0:
                    st.session_state.inventory['mp_potion'] -= 1
                    if potion_target == "플레이어" or st.session_state.companion is None:
                        st.session_state.mp = min(max_mp, st.session_state.mp + 30)
                        add_log("플레이어가 MP 포션을 사용했습니다.")
                    else:
                        comp = st.session_state.companion
                        comp['mp'] = min(comp['max_mp'], comp['mp'] + 30)
                        add_log(f"동료 {comp['name']}에게 MP 포션을 사용했습니다.")
                    save_game_state()
                    st.rerun()
                else:
                    st.warning("MP 포션 부족!")

    # 메인 화면
    st.title("🗺️ 텍스트 RPG 세계관")
    
    # 전투 중일 때의 화면
    if st.session_state.in_combat:
        st.subheader("⚔️ 실시간 전투 진행 중 (2초 간격)")
        cm = st.session_state.combat_monster
        
        if st.session_state.companion:
            col_c1, col_c2, col_c3 = st.columns(3)
        else:
            col_c1, col_c2 = st.columns(2)
            
        with col_c1:
            p_pct = int(max(0.0, min(1.0, st.session_state.hp / float(max_hp))) * 100)
            st.markdown(f"""
            <div style="margin-bottom: 5px; font-size: 16px; font-weight: bold;">👤 {st.session_state.char_name}</div>
            <div style="background-color: #e0e0e0; border-radius: 12px; height: 26px; width: 100%; overflow: hidden;">
                <div style="background-color: #ff4b4b; width: {p_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 26px; font-size: 14px;">{st.session_state.hp} / {max_hp}</div>
            </div>
            """, unsafe_allow_html=True)
            
        if st.session_state.companion:
            with col_c2:
                comp = st.session_state.companion
                c_pct = int(max(0.0, min(1.0, comp['hp'] / float(comp['max_hp']))) * 100)
                st.markdown(f"""
                <div style="margin-bottom: 5px; font-size: 16px; font-weight: bold;">🤝 {comp['name']}</div>
                <div style="background-color: #e0e0e0; border-radius: 12px; height: 26px; width: 100%; overflow: hidden;">
                    <div style="background-color: #ffa100; width: {c_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 26px; font-size: 14px;">{comp['hp']} / {comp['max_hp']}</div>
                </div>
                """, unsafe_allow_html=True)
                
        target_col = col_c3 if st.session_state.companion else col_c2
        with target_col:
            m_pct = int(max(0.0, min(1.0, cm['hp'] / float(cm['max_hp']))) * 100)
            st.markdown(f"""
            <div style="margin-bottom: 5px; font-size: 16px; font-weight: bold;">👹 {cm['name']}</div>
            <div style="background-color: #e0e0e0; border-radius: 12px; height: 26px; width: 100%; overflow: hidden;">
                <div style="background-color: #1c83e1; width: {m_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 26px; font-size: 14px;">{cm['hp']} / {cm['max_hp']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### ⚡ 최근 전투 결과")
        st.markdown(f"""
        <div style="padding: 15px; background-color: #f0f2f6; color: #31333F; border-radius: 10px; border: 2px solid #d6d6d8;">
            {st.session_state.last_combat_msg}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        # ----------------- 턴 전투 흐름 처리 -----------------
        if st.session_state.combat_turn == "player":
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
            
            if best_spell_name and st.session_state.mp >= 5:
                base_attack_power = best_spell_dmg
                st.session_state.mp -= 5
                is_magic_attack = True
            
            dmg_to_m = max(1, base_attack_power - cm['def'] + random.randint(-2, 2))
            
            # 마법 데미지는 최종 데미지의 절반만 적용
            if is_magic_attack or st.session_state.equipped_weapon in game_data.get("spells", {}):
                dmg_to_m = max(1, int(dmg_to_m * 0.5))
                
            double_msg = ""
            if st.session_state.player_double_damage:
                dmg_to_m *= 2
                st.session_state.player_double_damage = False
                double_msg = " 🔥 [적 중심 상실 효과: 데미지 2배 적용!]"
                
            cm['hp'] -= dmg_to_m
            log_msg = f"⚔️ [플레이어 공격] 적 피해 데미지: {dmg_to_m}{double_msg}"
            st.session_state.last_combat_msg = log_msg
            add_log(log_msg)
            
            if cm['hp'] <= 0:
                win_msg = f"🎉 **{cm['name']}** 처치 성공! (+{cm['atk'] * 5} 골드)"
                st.session_state.last_combat_msg = win_msg
                add_log(win_msg)
                st.session_state.gold += cm['atk'] * 5
                st.session_state.in_combat = False
                handle_item_drop(cm['atk'], cm['def'])
                save_game_state()
                time.sleep(1)
                st.rerun()
            else:
                if st.session_state.companion and st.session_state.companion['hp'] > 0:
                    st.session_state.combat_turn = "companion"
                else:
                    st.session_state.combat_turn = "monster"
                save_game_state()
                time.sleep(2)
                st.rerun()
                
        elif st.session_state.combat_turn == "companion":
            comp = st.session_state.companion
            if not comp or comp['hp'] <= 0:
                st.session_state.combat_turn = "monster"
                save_game_state()
                st.rerun()
            else:
                c_stats = comp['stats']
                c_weapon_atk = 0
                is_c_magic = False
                if comp['equipped_weapon']:
                    w_name = comp['equipped_weapon']
                    if w_name in game_data.get("weapons", {}):
                        c_weapon_atk = game_data["weapons"][w_name]["attack"]
                    elif w_name in game_data.get("spells", {}):
                        c_weapon_atk = game_data["spells"][w_name]["base_damage"] + c_stats["int"] // 2
                        is_c_magic = True
                
                c_total_atk = c_stats["str"] + c_weapon_atk
                if comp['type'] == "마법사" and comp['mp'] >= 5:
                    comp['mp'] -= 5
                    c_total_atk += int(c_stats["int"] * 1.5)
                    is_c_magic = True
                
                dmg_to_m = max(1, c_total_atk - cm['def'] + random.randint(-2, 2))
                if is_c_magic or (comp['equipped_weapon'] in game_data.get("spells", {})):
                    dmg_to_m = max(1, int(dmg_to_m * 0.5))
                    
                cm['hp'] -= dmg_to_m
                log_msg = f"⚔️ [동료 공격] {comp['name']}의 공격 | 적 피해 데미지: {dmg_to_m}"
                st.session_state.last_combat_msg = log_msg
                add_log(log_msg)
                
                if cm['hp'] <= 0:
                    win_msg = f"🎉 **{cm['name']}** 처치 성공! (+{cm['atk'] * 5} 골드)"
                    st.session_state.last_combat_msg = win_msg
                    add_log(win_msg)
                    st.session_state.gold += cm['atk'] * 5
                    st.session_state.in_combat = False
                    handle_item_drop(cm['atk'], cm['def'])
                    save_game_state()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.combat_turn = "monster"
                    save_game_state()
                    time.sleep(2)
                    st.rerun()
                
        elif st.session_state.combat_turn == "monster":
            monster_atk = cm['atk']
            
            target_is_companion = False
            comp = st.session_state.companion
            if comp and comp['hp'] > 0:
                if comp['name'] in ["힘전사", "체력전사"]:
                    target_is_companion = True
            
            if target_is_companion:
                c_armor_def = 0
                if comp['equipped_armor'] and comp['equipped_armor'] in game_data.get("armors", {}):
                    c_armor_def = game_data["armors"][comp['equipped_armor']]["defense"]
                c_shield_def = 0
                if comp['equipped_shield'] and comp['equipped_shield'] in game_data.get("shields", {}):
                    c_shield_def = game_data["shields"][comp['equipped_shield']]["defense"]
                c_total_def = (comp['stats']['dex'] // 2) + c_armor_def + c_shield_def
                
                c_evade_chance = min(0.40, comp['stats']['dex'] * 0.02)
                c_block_chance = 0.30 if comp['equipped_shield'] else 0.05
                
                c_evaded = random.random() < c_evade_chance
                c_blocked = False
                if not c_evaded:
                    c_blocked = random.random() < c_block_chance
                    
                if c_evaded:
                    dmg_to_c = 0
                elif c_blocked:
                    raw_dmg = max(1, monster_atk - c_total_def + random.randint(-1, 1))
                    dmg_to_c = max(0, raw_dmg // 2)
                else:
                    dmg_to_c = max(1, monster_atk - c_total_def + random.randint(-1, 1))
                    
                comp['hp'] -= dmg_to_c
                
                if c_evaded:
                    log_msg = f"💨 {comp['name']} 회피 성공"
                elif c_blocked:
                    log_msg = f"🛡️ {comp['name']} 블록 성공"
                else:
                    log_msg = f"💥 [적 공격] {cm['name']}의 공격 ({comp['name']} 피격) 동료 피해 데미지: {dmg_to_c}"
                    
                st.session_state.last_combat_msg = log_msg
                add_log(log_msg)
                
                if comp['hp'] <= 0:
                    death_msg = f"💀 동료 [{comp['name']}]이(가) 전투 중 사망하여 쓰러졌습니다... 착용하고 있던 장비들과 함께 사라집니다."
                    add_log(death_msg)
                    st.session_state.companion = None
                
                st.session_state.combat_turn = "player"
                save_game_state()
                time.sleep(2)
                st.rerun()
                
            else:
                dex_val = st.session_state.stats['dex']
                p_evade_chance = min(0.40, dex_val * 0.02)
                p_block_chance = 0.30 if st.session_state.equipped_shield else 0.05
                
                p_evaded = random.random() < p_evade_chance
                p_blocked = False
                if not p_evaded:
                    p_blocked = random.random() < p_block_chance
                    
                if p_evaded:
                    dmg_to_p = 0
                elif p_blocked:
                    raw_dmg = max(1, monster_atk - total_def + random.randint(-1, 1))
                    dmg_to_p = max(0, raw_dmg // 2)
                else:
                    dmg_to_p = max(1, monster_atk - total_def + random.randint(-1, 1))
                    
                st.session_state.hp -= dmg_to_p
                
                if p_evaded:
                    st.session_state.player_double_damage = True
                    big_msg = "<h1 style='color: #00e1ff; text-align: center;'>💨 플레이어 회피성공!</h1><h3 style='text-align: center; color: #ffeb3b;'>적이 중심을 잃었습니다! (다음 플레이어 공격 데미지 2배 ⚡)</h3>"
                    st.session_state.last_combat_msg = big_msg
                    add_log("💨 플레이어 회피성공! 적이 중심을 잃었습니다.")
                elif p_blocked:
                    st.session_state.player_double_damage = True
                    big_msg = "<h1 style='color: #ff9800; text-align: center;'>🛡️ 플레이어 블록 성공!</h1><h3 style='text-align: center; color: #ffeb3b;'>적이 중심을 잃었습니다! (다음 플레이어 공격 데미지 2배 ⚡)</h3>"
                    st.session_state.last_combat_msg = big_msg
                    add_log("🛡️ 플레이어 블록 성공! 적이 중심을 잃었습니다.")
                else:
                    log_msg = f"💥 [적 공격] {cm['name']}의 공격 내 피해 데미지: {dmg_to_p}"
                    st.session_state.last_combat_msg = f"<div style='font-size: 18px; font-weight: bold;'>{log_msg}</div>"
                    add_log(log_msg)
                    
                if st.session_state.hp <= 0:
                    lose_msg = "💀 전투에서 패배하여 사망했습니다... 마을로 부활합니다. (착용 중인 모든 장비 소실!)"
                    st.session_state.last_combat_msg = lose_msg
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
                    time.sleep(2)
                    st.rerun()

    else:
        # 평상시 화면 (사냥터, 상점, 여관)
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
                            start_msg = f"야생의 **{m_name}** (공격력:{m_data['attack']}, 방어력:{m_data['defense']}, HP:{m_data['hp']}) 출현!"
                            st.session_state.last_combat_msg = start_msg
                            add_log(start_msg)
                            save_game_state()
                            st.rerun()

        with tab2:
            st.subheader("🛒 잡화 상점")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.write("### HP 포션 (30 G)")
                if st.button("HP 포션 구매"):
                    if st.session_state.gold >= 30:
                        st.session_state.gold -= 30
                        st.session_state.inventory["hp_potion"] += 1
                        add_log("HP 포션 구매 완료")
                        save_game_state()
                        st.rerun()
                    else:
                        st.warning("골드 부족!")
            with col_s2:
                st.write("### MP 포션 (25 G)")
                if st.button("MP 포션 구매"):
                    if st.session_state.gold >= 25:
                        st.session_state.gold -= 25
                        st.session_state.inventory["mp_potion"] += 1
                        add_log("MP 포션 구매 완료")
                        save_game_state()
                        st.rerun()
                    else:
                        st.warning("골드 부족!")

        with tab3:
            st.subheader("🏨 여관 & 동료 고용")
            st.write("여관 휴식 요금: **50 G** (체력 및 마나 완전 회복)")
            if st.button("여관에서 휴식하기", type="primary"):
                if st.session_state.gold >= 50:
                    st.session_state.gold -= 50
                    st.session_state.hp = max_hp
                    st.session_state.mp = max_mp
                    if st.session_state.companion:
                        st.session_state.companion['hp'] = st.session_state.companion['max_hp']
                        st.session_state.companion['mp'] = st.session_state.companion['max_mp']
                    add_log("여관에서 휴식하여 HP와 MP가 모두 회복되었습니다.")
                    save_game_state()
                    st.rerun()
                else:
                    st.warning("여관비(50 G)가 부족합니다!")
            
            st.markdown("---")
            st.subheader("🤝 동료 고용소 (고용비: 100 G)")
            comp_type_selected = st.selectbox("고용할 동료 선택", ["힘전사 (힘10, 체5, 지5, 민5)", "체력전사 (힘5, 체10, 지5, 민5)", "도적 (힘5, 체5, 지5, 민10)", "마법사 (힘5, 체5, 지10, 민5)"])
            
            if st.button("동료 고용하기"):
                if st.session_state.companion is not None:
                    st.warning("이미 동료가 있습니다! 한 번에 1명만 고용할 수 있습니다.")
                elif st.session_state.gold < 100:
                    st.warning("고용 비용(100 G)이 부족합니다!")
                else:
                    st.session_state.gold -= 100
                    
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
                        c_type = "도적"
                        c_stats = {"str": 5, "dex": 10, "vit": 5, "int": 5}
                    else:
                        c_name = "마법사"
                        c_type = "마법사"
                        c_stats = {"str": 5, "dex": 5, "vit": 5, "int": 10}
                        
                    c_max_hp = 50 + (c_stats["vit"] * 10)
                    c_max_mp = 30 + (c_stats["int"] * 8)
                    
                    st.session_state.companion = {
                        "name": c_name,
                        "type": c_type,
                        "stats": c_stats,
                        "hp": c_max_hp,
                        "max_hp": c_max_hp,
                        "mp": c_max_mp,
                        "max_mp": c_max_mp,
                        "equipped_weapon": None,
                        "equipped_armor": None,
                        "equipped_shield": None
                    }
                    
                    process_auto_equip()
                    add_log(f"🤝 든든한 동료 [{c_name}](을)를 기본 상태로 고용했습니다! (사망할 때까지 함께합니다)")
                    save_game_state()
                    st.rerun()

    st.markdown("---")
    st.subheader("📜 실시간 모험 기록")
    for log in st.session_state.logs:
        st.text(log)
