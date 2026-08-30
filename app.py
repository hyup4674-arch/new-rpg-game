import streamlit as st
import json
import random
import os

# 페이지 설정
st.set_page_config(page_title="AI 텍스트 RPG", page_icon="⚔️", layout="wide")

# 데이터 로드 함수
@st.cache_data
def load_game_data():
    if os.path.exists("game_data.json"):
        with open("game_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

game_data = load_game_data()

# 세션 상태 초기화
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
    
    # 장착 아이템
    st.session_state.equipped_weapon = None
    st.session_state.equipped_armor = None
    st.session_state.equipped_shield = None
    
    # 인벤토리 (소모품 등)
    st.session_state.inventory = {"hp_potion": 2, "mp_potion": 2}
    
    # 게임 로그
    st.session_state.logs = ["모험의 세계에 오신 것을 환영합니다! 캐릭터를 생성해주세요."]
    st.session_state.initialized = True

def add_log(msg):
    st.session_state.logs.insert(0, msg)
    if len(st.session_state.logs) > 30:
        st.session_state.logs.pop()

# 능력치 계산 함수
def get_derived_stats():
    s = st.session_state.stats
    # 기본 공격력 = 힘 + 무기 공격력 (또는 마법 기본 데미지)
    weapon_atk = 0
    if st.session_state.equipped_weapon:
        w_name = st.session_state.equipped_weapon
        # 무기인지 마법인지 확인
        if w_name in game_data.get("weapons", {}):
            weapon_atk = game_data["weapons"][w_name]["attack"]
        elif w_name in game_data.get("spells", {}):
            weapon_atk = game_data["spells"][w_name]["base_damage"] + s["int"] // 2
            
    # 방어력 = 민첩/2 + 갑옷 방어력 + 방패 방어력
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

# ----------------- UI: 캐릭터 생성 화면 -----------------
if not st.session_state.game_started:
    st.title("⚔️ AI 텍스트 RPG: 모험의 시작")
    st.markdown("캐릭터를 생성하고 모험을 떠나세요!")
    
    col1, col2 = st.columns(2)
    with col1:
        char_name = st.text_input("캐릭터 이름", value="모험가")
        char_class = st.selectbox("직업 선택", ["전사", "암살자", "마법사"])
        
        st.markdown("---")
        st.subheader("스탯 분배 (기본 각 5, 남은 포인트: {})".format(st.session_state.bonus_points))
        
        # 스탯 분배 슬라이더/인풋 관리
        # 임시 상태 저장
        if "alloc" not in st.session_state:
            st.session_state.alloc = {"str": 0, "dex": 0, "vit": 0, "int": 0}
            
        total_allocated = sum(st.session_state.alloc.values())
        remaining = 10 - total_allocated
        
        st.write(f"남은 보너스 포인트: **{remaining}**")
        
        s_str = st.slider("힘 (STR)", 0, 10, st.session_state.alloc["str"], key="s_str_slider")
        s_dex = st.slider("민첩 (DEX)", 0, 10, st.session_state.alloc["dex"], key="s_dex_slider")
        s_vit = st.slider("체력 (VIT)", 0, 10, st.session_state.alloc["vit"], key="s_vit_slider")
        s_int = st.slider("지능 (INT)", 0, 10, st.session_state.alloc["int"], key="s_int_slider")
        
        # 슬라이더 값 합계 검증
        current_sum = s_str + s_dex + s_vit + s_int
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
            else:
                st.session_state.char_name = char_name
                st.session_state.char_class = char_class
                st.session_state.stats = {
                    "str": 5 + st.session_state.alloc["str"],
                    "dex": 5 + st.session_state.alloc["dex"],
                    "vit": 5 + st.session_state.alloc["vit"],
                    "int": 5 + st.session_state.alloc["int"]
                }
                
                # 최초 장비 지급
                _, _, max_hp, max_mp = get_derived_stats()
                st.session_state.max_hp = max_hp
                st.session_state.hp = max_hp
                st.session_state.max_mp = max_mp
                st.session_state.mp = max_mp
                
                if char_class == "전사":
                    st.session_state.equipped_weapon = "루키 숏소드"
                    st.session_state.equipped_armor = "누더기 갑옷세트"
                    st.session_state.equipped_shield = "나무 방패"
                elif char_class == "암살자":
                    st.session_state.equipped_weapon = "낡은 단검"
                    st.session_state.equipped_armor = "누더기 갑옷세트"
                    st.session_state.equipped_shield = None
                elif char_class == "마법사":
                    st.session_state.equipped_weapon = "작은 불꽃"
                    st.session_state.equipped_armor = "누더기 갑옷세트"
                    st.session_state.equipped_shield = None
                    
                st.session_state.game_started = True
                add_log(f"[{char_name}] ({char_class}) 모험가가 탄생했습니다! 마을에서 여정을 시작합니다.")
                st.rerun()

else:
    # ----------------- 게임 메인 화면 -----------------
    total_atk, total_def, max_hp, max_mp = get_derived_stats()
    
    # 좌측 사이드바: 캐릭터 상태 및 인벤토리
    with st.sidebar:
        st.title(f"👤 {st.session_state.char_name}")
        st.caption(f"직업: **{st.session_state.char_class}**")
        st.markdown("---")
        
        st.subheader("📊 능력치")
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
        st.subheader("🧪 보유 포션")
        st.text(f"HP 포션: {st.session_state.inventory['hp_potion']}개")
        st.text(f"MP 포션: {st.session_state.inventory['mp_potion']}개")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("HP 포션 사용"):
                if st.session_state.inventory['hp_potion'] > 0:
                    st.session_state.inventory['hp_potion'] -= 1
                    st.session_state.hp = min(max_hp, st.session_state.hp + 50)
                    add_log("HP 포션을 사용하여 체력을 50 회복했습니다.")
                    st.rerun()
                else:
                    st.warning("HP 포션이 부족합니다!")
        with col_p2:
            if st.button("MP 포션 사용"):
                if st.session_state.inventory['mp_potion'] > 0:
                    st.session_state.inventory['mp_potion'] -= 1
                    st.session_state.mp = min(max_mp, st.session_state.mp + 30)
                    add_log("MP 포션을 사용하여 마나를 30 회복했습니다.")
                    st.rerun()
                else:
                    st.warning("MP 포션이 부족합니다!")

    # 메인 화면 구성
    st.title("🗺️ 텍스트 RPG 세계관")
    
    # 상단 탭 (사냥터, 상점, 여관)
    tab1, tab2, tab3 = st.tabs(["🌲 사냥터", "🛒 상점", "🏨 여관"])
    
    with tab1:
        st.subheader("사냥터 선택")
        h_grounds = game_data.get("hunting_grounds", {})
        selected_hg = st.selectbox("사냥터를 선택하세요", list(h_grounds.keys()))
        
        if selected_hg:
            hg_info = h_grounds[selected_hg]
            st.info(f"**설명:** {hg_info['desc']} (몬스터 공격력 범위: {hg_info['min_atk']} ~ {hg_info['max_atk']})")
            
            if st.button("⚔️ 사냥 시작!", type="primary"):
                # 해당 공격력 범위 내의 몬스터 필터링
                monsters = game_data.get("monsters", {})
                valid_monsters = []
                for m_name, m_data in monsters.items():
                    if hg_info['min_atk'] <= m_data['attack'] <= hg_info['max_atk']:
                        valid_monsters.append((m_name, m_data))
                
                if valid_monsters:
                    m_name, m_data = random.choice(valid_monsters)
                    m_atk = m_data['attack']
                    m_def = m_data['defense']
                    m_hp = m_data['hp']
                    m_max_hp = m_hp
                    
                    add_log(f" 야생의 **{m_name}** (공격력:{m_atk}, 방어력:{m_def}, HP:{m_hp})과(와) 전투를 시작합니다!")
                    
                    # 전투 시뮬레이션
                    battle_log = []
                    turn = 1
                    while m_hp > 0 and st.session_state.hp > 0:
                        # 플레이어 공격
                        dmg_to_m = max(1, total_atk - m_def + random.randint(-2, 2))
                        m_hp -= dmg_to_m
                        
                        if m_hp <= 0:
                            battle_log.append(f"턴 {turn}: 플레이어의 공격! {m_name}에게 {dmg_to_m}의 피해를 입혔습니다. ({m_name} 처치!)")
                            break
                        
                        # 몬스터 반격
                        dmg_to_p = max(1, m_atk - total_def + random.randint(-1, 1))
                        st.session_state.hp -= dmg_to_p
                        
                        battle_log.append(f"턴 {turn}: 플레이어 공격({dmg_to_m} 피해) ➔ {m_name} 반격({dmg_to_p} 피해). 잔여 HP: {max(0, st.session_state.hp)}/{max_hp}")
                        
                        if st.session_state.hp <= 0:
                            break
                        turn += 1
                        if turn > 50: # 무한루프 방지
                            break
                            
                    for l in battle_log:
                        add_log(l)
                        
                    # 전투 결과 처리
                    if st.session_state.hp <= 0:
                        add_log(f"💀 사망하셨습니다... 마을로 부활합니다. (모든 장착 장비 소실!)")
                        st.session_state.hp = max_hp
                        st.session_state.mp = max_mp
                        st.session_state.equipped_weapon = None
                        st.session_state.equipped_armor = None
                        st.session_state.equipped_shield = None
                        st.rerun()
                    else:
                        add_log(f"🎉 **{m_name}** 처치 성공! 승리하였습니다!")
                        st.session_state.gold += m_atk * 5
                        
                        # 아이템 드롭 체크 (5% 확률)
                        if random.random() < 0.05:
                            # 1개만 드롭: 무기/마법 (공격력 == m_atk) 또는 방패/갑옷 (방어력 == m_def)
                            drop_type = random.choice(["weapon_or_spell", "armor_or_shield"])
                            dropped_item = None
                            item_category = ""
                            
                            if drop_type == "weapon_or_spell":
                                # 한손무기, 양손무기, 단검, 마법 중 m_atk와 일치하는 것 탐색
                                candidates = []
                                for w_n, w_d in game_data.get("weapons", {}).items():
                                    if w_d["attack"] == m_atk:
                                        candidates.append((w_n, "weapon"))
                                for sp_n, sp_d in game_data.get("spells", {}).items():
                                    if sp_d["base_damage"] == m_atk:
                                        candidates.append((sp_n, "spell"))
                                if candidates:
                                    dropped_item, item_category = random.choice(candidates)
                            else:
                                # 방패, 갑옷 중 m_def와 일치하는 것 탐색
                                candidates = []
                                for a_n, a_d in game_data.get("armors", {}).items():
                                    if a_d["defense"] == m_def:
                                        candidates.append((a_n, "armor"))
                                for sh_n, sh_d in game_data.get("shields", {}).items():
                                    if sh_d["defense"] == m_def:
                                        candidates.append((sh_n, "shield"))
                                if candidates:
                                    dropped_item, item_category = random.choice(candidates)
                                    
                            if dropped_item:
                                add_log(f"🎁 희귀 아이템 드롭 발견: **{dropped_item}**!")
                                
                                # 직업별 착용 제한 검증 및 자동 획득(착용)
                                c_class = st.session_state.char_class
                                can_equip = False
                                
                                if item_category in ["weapon", "spell"]:
                                    if c_class == "전사":
                                        # 전사: 한손무기, 양손무기 착용 가능 (단검, 마법 불가)
                                        if dropped_item in game_data.get("weapons", {}):
                                            # 한손/양손 구분 (양손무기 리스트에 있거나 단검이 아니면)
                                            is_dagger = any(dropped_item.startswith(d_prefix) for d_prefix in ["낡은 단검", "나무 뾰족검", "스틸레토", "쿠커리", "커스 대거", "크리스", "카타르", "어쌔신 나이프", "섀도우 단검", "독니 단검", "블러드 스틸레토", "은장 단검", "룬 대거", "팬텀 나이프", "미스릴 대거", "티타늄 단검", "드래곤 이빨", "월광의 단검", "전설의 암살검", "신성한 스틸레토"])
                                            if not is_dagger:
                                                can_equip = True
                                    elif c_class == "암살자":
                                        # 암살자: 단검만 착용 가능
                                        if dropped_item in game_data.get("weapons", {}):
                                            is_dagger = any(dropped_item.startswith(d_prefix) for d_prefix in ["낡은 단검", "나무 뾰족검", "스틸레토", "쿠커리", "커스 대거", "크리스", "카타르", "어쌔신 나이프", "섀도우 단검", "독니 단검", "블러드 스틸레토", "은장 단검", "룬 대거", "팬텀 나이프", "미스릴 대거", "티타늄 단검", "드래곤 이빨", "월광의 단검", "전설의 암살검", "신성한 스틸레토"])
                                            if is_dagger:
                                                can_equip = True
                                    elif c_class == "마법사":
                                        # 마법사: 마법만 사용 가능
                                        if dropped_item in game_data.get("spells", {}):
                                            can_equip = True
                                            
                                elif item_category == "armor":
                                    # 갑옷은 모든 직업 착용 가능
                                    can_equip = True
                                    
                                elif item_category == "shield":
                                    # 방패는 전사만 착용 가능 (암살자, 마법사 불가)
                                    if c_class == "전사":
                                        can_equip = True
                                        
                                if can_equip:
                                    if item_category in ["weapon", "spell"]:
                                        st.session_state.equipped_weapon = dropped_item
                                        add_log(f"✨ 직업에 적합하여 무기/마법 **{dropped_item}**(을)를 자동 장착했습니다!")
                                    elif item_category == "armor":
                                        st.session_state.equipped_armor = dropped_item
                                        add_log(f"✨ 갑옷 **{dropped_item}**(을)를 자동 장착했습니다!")
                                    elif item_category == "shield":
                                        st.session_state.equipped_shield = dropped_item
                                        add_log(f"✨ 방패 **{dropped_item}**(을)를 자동 장착했습니다!")
                                else:
                                    add_log(f"⚠️ 직업({c_class}) 제한에 맞지 않아 획득한 아이템({dropped_item})을 장착할 수 없습니다.")
                        st.rerun()

    with tab2:
        st.subheader("🛒 잡화 상점")
        st.markdown("모험에 필요한 포션을 구입할 수 있습니다.")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.write("### HP 포션 (회복 50)")
            st.write("가격: **30 G**")
            if st.button("HP 포션 구매"):
                if st.session_state.gold >= 30:
                    st.session_state.gold -= 30
                    st.session_state.inventory["hp_potion"] += 1
                    add_log("HP 포션을 1개 구입했습니다.")
                    st.rerun()
                else:
                    st.warning("골드가 부족합니다!")
                    
        with col_s2:
            st.write("### MP 포션 (회복 30)")
            st.write("가격: **25 G**")
            if st.button("MP 포션 구매"):
                if st.session_state.gold >= 25:
                    st.session_state.gold -= 25
                    st.session_state.inventory["mp_potion"] += 1
                    add_log("MP 포션을 1개 구입했습니다.")
                    st.rerun()
                else:
                    st.warning("골드가 부족합니다!")

    with tab3:
        st.subheader("🏨 모험가의 여관")
        st.markdown("여관에서 피로를 풀고 체력과 마나를 완벽하게 회복하세요.")
        st.write("이용 요금: **50 G**")
        
        if st.button("여관에서 휴식하기", type="primary"):
            if st.session_state.gold >= 50:
                st.session_state.gold -= 50
                st.session_state.hp = max_hp
                st.session_state.mp = max_mp
                add_log("여관에서 편안하게 휴식을 취해 HP와 MP가 모두 회복되었습니다!")
                st.rerun()
            else:
                st.warning("여관비를 지불할 골드가 부족합니다! (필요: 50 G)")

    # 하단 실시간 게임 로그 표시
    st.markdown("---")
    st.subheader("📜 실시간 모험 기록")
    for log in st.session_state.logs:
        st.text(log)

