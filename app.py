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

# 세션 상태 초기화 및 누락된 키 보정
if "initialized" not in st.session_state:
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
    
    # 전투 상태
    st.session_state.in_combat = False
    st.session_state.combat_monster = None
    st.session_state.combat_turn = "player"
    st.session_state.last_combat_msg = "⚔️ 사냥터에서 사냥을 시작하면 실시간 전투 계산 결과가 여기에 표시됩니다."
    
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

def add_log(msg):
    st.session_state.logs.insert(0, msg)
    if len(st.session_state.logs) > 30:
        st.session_state.logs.pop()

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

# 아이템 드롭 및 자동 장착/보관 처리 함수
def handle_item_drop(m_atk, m_def):
    drop_type = random.choice(["weapon_or_spell", "armor_or_shield"])
    dropped_item = None
    item_category = ""
    item_val = 0
    
    if drop_type == "weapon_or_spell":
        candidates = []
        for w_n, w_d in game_data.get("weapons", {}).items():
            if w_d["attack"] == m_atk:
                candidates.append((w_n, "weapon", w_d["attack"]))
        for sp_n, sp_d in game_data.get("spells", {}).items():
            if sp_d["base_damage"] == m_atk:
                candidates.append((sp_n, "spell", sp_d["base_damage"]))
        if candidates:
            dropped_item, item_category, item_val = random.choice(candidates)
    else:
        candidates = []
        for a_n, a_d in game_data.get("armors", {}).items():
            if a_d["defense"] == m_def:
                candidates.append((a_n, "armor", a_d["defense"]))
        for sh_n, sh_d in game_data.get("shields", {}).items():
            if sh_d["defense"] == m_def:
                candidates.append((sh_n, "shield", sh_d["defense"]))
        if candidates:
            dropped_item, item_category, item_val = random.choice(candidates)
            
    if dropped_item:
        add_log(f"🎁 필드 드롭 아이템 발견: **{dropped_item}**!")
        c_class = st.session_state.char_class
        can_equip = False
        
        is_dagger = any(dropped_item.startswith(d) for d in [
            "낡은 단검", "나무 뾰족검", "스틸레토", "쿠커리", "커스 대거", "크리스", "카타르", 
            "어쌔신 나이프", "섀도우 단검", "독니 단검", "블러드 스틸레토", "은장 단검", 
            "룬 대거", "팬텀 나이프", "미스릴 대거", "티타늄 단검", "드래곤 이빨", "월광의 단검", "전설의 암살검", "신성한 스틸레토"
        ])
        
        if item_category in ["weapon", "spell"]:
            if c_class == "전사" and dropped_item in game_data.get("weapons", {}) and not is_dagger:
                can_equip = True
            elif c_class == "암살자" and is_dagger:
                can_equip = True
            elif c_class == "마법사" and dropped_item in game_data.get("spells", {}):
                can_equip = True
        elif item_category == "armor":
            can_equip = True
        elif item_category == "shield":
            if c_class == "전사":
                can_equip = True
                
        if can_equip:
            current_item = None
            current_val = 0
            if item_category in ["weapon", "spell"]:
                current_item = st.session_state.equipped_weapon
                if current_item in game_data.get("weapons", {}):
                    current_val = game_data["weapons"][current_item]["attack"]
                elif current_item in game_data.get("spells", {}):
                    current_val = game_data["spells"][current_item]["base_damage"]
            elif item_category == "armor":
                current_item = st.session_state.equipped_armor
                if current_item in game_data.get("armors", {}):
                    current_val = game_data["armors"][current_item]["defense"]
            elif item_category == "shield":
                current_item = st.session_state.equipped_shield
                if current_item in game_data.get("shields", {}):
                    current_val = game_data["shields"][current_item]["defense"]
                    
            if item_val > current_val:
                if item_category in ["weapon", "spell"]:
                    st.session_state.equipped_weapon = dropped_item
                elif item_category == "armor":
                    st.session_state.equipped_armor = dropped_item
                elif item_category == "shield":
                    st.session_state.equipped_shield = dropped_item
                add_log(f"✨ 더 뛰어난 성능! **{dropped_item}**(을)를 자동 장착했습니다.")
            else:
                st.session_state.item_inventory.append(dropped_item)
                add_log(f"📦 {dropped_item}을(를) 인벤토리에 보관했습니다.")
        else:
            st.session_state.item_inventory.append(dropped_item)
            add_log(f"📦 직업 제한으로 장착할 수 없어 {dropped_item}을(를) 인벤토리에 보관했습니다.")

# game_data 파일 유무 체크 경고
if not game_data:
    st.error("⚠️ 루트 디렉토리에 `game_data.json` 파일이 존재하지 않거나 내용이 비어 있습니다. 게임 데이터를 포함한 `game_data.json` 파일을 추가해주세요.")

# ----------------- 사이드바: 저장 및 불러오기 메뉴 -----------------
with st.sidebar:
    st.title("💾 게임 데이터 관리")
    st.markdown("현재 진행 상황을 내 기기에 저장하거나 저장된 파일을 불러올 수 있습니다.")
    
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
            "in_combat": st.session_state.in_combat,
            "combat_monster": st.session_state.combat_monster,
            "combat_turn": st.session_state.combat_turn,
            "last_combat_msg": st.session_state.last_combat_msg,
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
    else:
        st.info("캐릭터 생성 후 저장 기능을 사용할 수 있습니다.")

    st.markdown("---")
    
    uploaded_save_file = st.file_uploader("📂 저장 파일 불러오기", type=["json"])
    if uploaded_save_file is not None:
        try:
            loaded_data = json.load(uploaded_save_file)
            for k, v in loaded_data.items():
                st.session_state[k] = v
            st.session_state["initialized"] = True
            st.success("🎉 게임 데이터를 성공적으로 불러왔습니다!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"저장 파일을 읽는 중 오류가 발생했습니다: {e}")

    st.markdown("---")

# ----------------- UI: 캐릭터 생성 화면 -----------------
if not st.session_state.game_started:
    st.title("⚔️ AI 텍스트 RPG: 모험의 시작")
    st.markdown("캐릭터를 생성하거나, 사이드바에서 기존 저장 파일을 불러와 모험을 계속하세요!")
    
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
        * **전사 (Warrior)**
          * 장착 가능: 한손무기, 양손무기, 방패, 갑옷
          * 특징: 높은 체력과 방어력, 강력한 물리 공격
        * **암살자 (Assassin)**
          * 장착 가능: 단검, 갑옷
          * 특징: 높은 민첩과 회피, 치명적인 단검 공격
        * **마법사 (Mage)**
          * 장착 가능: 마법(스펠), 갑옷
          * 특징: 강력한 원거리 마법 공격과 넓은 마나 폭넓음
        """)
        
        if st.button("🚀 모험 시작하기", type="primary", use_container_width=True):
            if current_sum != 10:
                st.warning("보너스 포인트 10점을 모두 분배해주세요!")
            elif not game_data:
                st.error("game_data.json 데이터가 로드되지 않아 게임을 시작할 수 없습니다.")
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
                add_log(f"[{char_name}] ({char_class}) 모험가가 탄생했습니다! 마을에서 여정을 시작합니다.")
                st.rerun()

else:
    # ----------------- 게임 메인 화면 -----------------
    total_atk, total_def, max_hp, max_mp = get_derived_stats()
    
    # 좌측 사이드바: 캐릭터 상태 및 인벤토리
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
        
        st.markdown("---")
        st.subheader("🎒 장착 장비")
        st.text(f"무기/마법: {st.session_state.equipped_weapon or '없음'}")
        st.text(f"갑옷: {st.session_state.equipped_armor or '없음'}")
        st.text(f"방패: {st.session_state.equipped_shield or '없음'}")
        
        st.markdown("---")
        st.subheader("🧪 인벤토리")
        st.text(f"HP 포션: {st.session_state.inventory['hp_potion']}개")
        st.text(f"MP 포션: {st.session_state.inventory['mp_potion']}개")
        
        if st.session_state.item_inventory:
            st.write("**보유 중인 추가 장비:**")
            for itm in st.session_state.item_inventory:
                st.text(f"- {itm}")
        else:
            st.text("보유 중인 추가 장비 없음")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("HP 포션 사용"):
                if st.session_state.inventory['hp_potion'] > 0:
                    st.session_state.inventory['hp_potion'] -= 1
                    st.session_state.hp = min(max_hp, st.session_state.hp + 50)
                    add_log("HP 포션을 사용하여 체력을 회복했습니다.")
                    st.rerun()
                else:
                    st.warning("HP 포션 부족!")
        with col_p2:
            if st.button("MP 포션 사용"):
                if st.session_state.inventory['mp_potion'] > 0:
                    st.session_state.inventory['mp_potion'] -= 1
                    st.session_state.mp = min(max_mp, st.session_state.mp + 30)
                    add_log("MP 포션을 사용하여 마나를 회복했습니다.")
                    st.rerun()
                else:
                    st.warning("MP 포션 부족!")

    # 메인 화면
    st.title("🗺️ 텍스트 RPG 세계관")
    
    # 전투 중일 때의 화면
    if st.session_state.in_combat:
        st.subheader("⚔️ 실시간 전투 진행 중 (2초 간격)")
        cm = st.session_state.combat_monster
        
        # ----------------- 큼지막하고 색상이 적용된 HP 바 -----------------
        col_c1, col_c2 = st.columns(2)
        
        # 1. 플레이어 HP 바 (붉은색 #ff4b4b, 큼지막한 높이 30px)
        with col_c1:
            p_pct = int(max(0.0, min(1.0, st.session_state.hp / float(max_hp))) * 100)
            st.markdown(f"""
            <div style="margin-bottom: 5px; font-size: 18px; font-weight: bold;">👤 {st.session_state.char_name} (플레이어)</div>
            <div style="background-color: #e0e0e0; border-radius: 12px; height: 30px; width: 100%; overflow: hidden;">
                <div style="background-color: #ff4b4b; width: {p_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 30px; font-size: 16px;">{st.session_state.hp} / {max_hp} ({p_pct}%)</div>
            </div>
            """, unsafe_allow_html=True)
            st.text(f"MP: {st.session_state.mp} / {max_mp}")
            
        # 2. 적 HP 바 (푸른색 #1c83e1, 큼지막한 높이 30px)
        with col_c2:
            m_pct = int(max(0.0, min(1.0, cm['hp'] / float(cm['max_hp']))) * 100)
            st.markdown(f"""
            <div style="margin-bottom: 5px; font-size: 18px; font-weight: bold;">👹 {cm['name']} (적)</div>
            <div style="background-color: #e0e0e0; border-radius: 12px; height: 30px; width: 100%; overflow: hidden;">
                <div style="background-color: #1c83e1; width: {m_pct}%; height: 100%; text-align: center; color: white; font-weight: bold; line-height: 30px; font-size: 16px;">{cm['hp']} / {cm['max_hp']} ({m_pct}%)</div>
            </div>
            """, unsafe_allow_html=True)
            st.text("")
            
        st.markdown("---")
        
        # ----------------- 큼지막하게 표시되는 최근 전투 계산 결과 박스 -----------------
        st.markdown("### ⚡ 최근 전투 결과")
        st.markdown(f"""
        <div style="font-size: 22px; font-weight: bold; padding: 20px; background-color: #f0f2f6; color: #31333F; border-radius: 10px; text-align: center; border: 2px solid #d6d6d8;">
            {st.session_state.last_combat_msg}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        # 전투 턴 처리 (2초마다 교대 공격)
        if st.session_state.combat_turn == "player":
            c_class = st.session_state.char_class
            base_attack_power = total_atk
            
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
            
            m_evaded = random.random() < 0.10
            m_blocked = False
            if not m_evaded:
                m_blocked = random.random() < 0.10
                
            if m_evaded:
                dmg_to_m = 0
            elif m_blocked:
                raw_dmg = max(1, base_attack_power - cm['def'] + random.randint(-2, 2))
                dmg_to_m = max(1, raw_dmg // 2)
            else:
                dmg_to_m = max(1, base_attack_power - cm['def'] + random.randint(-2, 2))
                
            cm['hp'] -= dmg_to_m
            
            # 플레이어 공격 메시지 형식 적용 (적 피해 데미지만 표시)
            log_msg = f"⚔️ [플레이어 공격] 적 피해 데미지: {dmg_to_m}"
            st.session_state.last_combat_msg = log_msg
            add_log(log_msg)
            
            if cm['hp'] <= 0:
                win_msg = f"🎉 **{cm['name']}** 처치 성공! (+{cm['atk'] * 5} 골드)"
                st.session_state.last_combat_msg = win_msg
                add_log(win_msg)
                st.session_state.gold += cm['atk'] * 5
                st.session_state.in_combat = False
                
                if random.random() < 0.10:
                    handle_item_drop(cm['atk'], cm['def'])
                    
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.combat_turn = "monster"
                time.sleep(2)
                st.rerun()
                
        elif st.session_state.combat_turn == "monster":
            monster_atk = cm['atk']
            
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
            
            # 적 공격 메시지 조건부 형식 적용 (피해 데미지 / 회피 성공 / 블록 성공)
            if p_evaded:
                log_msg = "💨 회피 성공"
            elif p_blocked:
                log_msg = "🛡️ 블록 성공"
            else:
                log_msg = f"💥 [적 공격] {cm['name']}의 공격 내 피해 데미지: {dmg_to_p}"
                
            st.session_state.last_combat_msg = log_msg
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
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.combat_turn = "player"
                time.sleep(2)
                st.rerun()

    else:
        # 평상시 탭 화면 (사냥터, 상점, 여관)
        tab1, tab2, tab3 = st.tabs(["🌲 사냥터", "🛒 상점", "🏨 여관"])
        
        with tab1:
            st.subheader("사냥터 선택")
            h_grounds = game_data.get("hunting_grounds", {})
            if not h_grounds:
                st.warning("game_data.json에 사냥터(hunting_grounds) 데이터가 없습니다.")
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
                            st.error("해당 사냥터 범위에 일치하는 몬스터 데이터가 game_data.json에 없습니다.")
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
                        st.rerun()
                    else:
                        st.warning("골드 부족!")

        with tab3:
            st.subheader("🏨 여관")
            st.write("이용 요금: **50 G** (체력 및 마나 완전 회복)")
            if st.button("여관에서 휴식하기", type="primary"):
                if st.session_state.gold >= 50:
                    st.session_state.gold -= 50
                    st.session_state.hp = max_hp
                    st.session_state.mp = max_mp
                    add_log("여관에서 휴식하여 HP와 MP가 모두 회복되었습니다.")
                    st.rerun()
                else:
                    st.warning("여관비(50 G)가 부족합니다!")

    st.markdown("---")
    st.subheader("📜 실시간 모험 기록")
    for log in st.session_state.logs:
        st.text(log)
