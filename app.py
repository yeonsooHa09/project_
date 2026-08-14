import streamlit as st
from datetime import date

from data.policies import get_matching_policies
from utils.ai_helper import get_empathy_response, convert_gap_activity, check_crisis_signal

# ---------- 페이지 설정 ----------
st.set_page_config(
    page_title="다시, 시작 - 청년 리스타트 플랫폼",
    page_icon="🌱",
    layout="wide",
)

# ---------- 고정 데이터 ----------
DAILY_QUESTS = [
    ("walk", "🚶 오늘 하루, 10분만 산책하기"),
    ("likes", "📝 내가 좋아하는 것 3가지 메모하기"),
    ("job_post", "💼 관심 있는 회사 채용공고 1개 읽어보기"),
    ("music", "🎵 좋아하는 음악 들으며 10분 쉬기"),
]

REGIONS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
]

# 미취업 기간 선택지를 대략적인 개월 수로 변환 (정책 필터링용)
PERIOD_TO_MONTHS = {
    "3개월 미만": 2,
    "3~6개월": 5,
    "6개월~1년": 9,
    "1년 이상": 13,
}

INTEREST_FIELDS = [
    "IT/개발", "디자인", "마케팅", "콘텐츠/미디어", "교육", "공공/행정", "서비스/영업", "기타",
]

# ---------- 세션 상태 초기화 ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "gap_year_result" not in st.session_state:
    st.session_state.gap_year_result = None


def calc_quest_points():
    """퀘스트 체크 개수 + 대화 횟수 + 공백기 변환 사용 여부로 포인트를 계산해요.
    (별도로 더하고 빼는 대신, 매번 세션 상태에서 다시 계산하는 방식이라 값이 꼬일 일이 없어요.)
    """
    checked = sum(1 for qid, _ in DAILY_QUESTS if st.session_state.get(f"quest_{qid}", False))
    chat_bonus = len(st.session_state.chat_history) * 5
    gap_bonus = 15 if st.session_state.gap_year_result else 0
    return checked * 10 + chat_bonus + gap_bonus


# ---------- 사이드바 ----------
with st.sidebar:
    st.header("👤 나의 정보")
    region = st.selectbox("거주 지역", REGIONS)
    unemployment_period = st.selectbox("미취업 기간", list(PERIOD_TO_MONTHS.keys()))
    interest_field = st.selectbox("관심 분야", INTEREST_FIELDS)

    st.divider()
    st.metric("나의 퀘스트 포인트", f"{calc_quest_points()} P")

    st.divider()
    st.caption("혼자 힘들어하지 마세요. 언제든 도움을 요청해도 괜찮아요.")
    st.caption("📞 정신건강 위기상담전화 1577-0199 (24시간)")
    st.caption("📞 자살예방상담전화 1393 (24시간)")

unemployment_months = PERIOD_TO_MONTHS[unemployment_period]

# ---------- 헤더 ----------
st.title("🌱 괜찮아, 잠시 쉬어가도 돼")
st.caption(f"오늘은 {date.today().strftime('%Y년 %m월 %d일')} · 작은 한 걸음이면 충분해요.")

with st.expander("💭 오늘의 리스타트 지수 체크하기", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        energy = st.slider("오늘 에너지 레벨", 0, 10, 5)
    with col2:
        motivation = st.slider("무언가 시작해보고 싶은 마음", 0, 10, 5)
    with col3:
        anxiety = st.slider("불안한 정도", 0, 10, 5)

    restart_index = round((energy + motivation + (10 - anxiety)) / 3, 1)

    if restart_index >= 7:
        st.success(f"오늘의 리스타트 지수 **{restart_index}/10** — 컨디션이 좋네요! 작은 도전을 시작해보기 좋은 날이에요 ✨")
    elif restart_index >= 4:
        st.info(f"오늘의 리스타트 지수 **{restart_index}/10** — 무리하지 않아도 괜찮아요. 딱 5분만 움직여볼까요?")
    else:
        st.warning(f"오늘의 리스타트 지수 **{restart_index}/10** — 오늘은 푹 쉬는 것도 훌륭한 선택이에요. 당신은 이미 잘하고 있어요 💙")

st.divider()

# ---------- 메인 탭 ----------
tab1, tab2, tab3 = st.tabs(["💙 AI 마음 케어", "💰 공공 지원금 한눈에", "✨ AI 공백기 변환기"])

# ===== Tab 1: AI 마음 케어 =====
with tab1:
    st.subheader("오늘의 소소한 퀘스트")
    st.caption("완료할 때마다 +10P! 부담 갖지 말고 할 수 있는 만큼만 해보세요.")

    quest_cols = st.columns(len(DAILY_QUESTS))
    for i, (qid, qlabel) in enumerate(DAILY_QUESTS):
        with quest_cols[i]:
            st.checkbox(qlabel, key=f"quest_{qid}")

    st.divider()
    st.subheader("오늘 내 마음은 어땠나요?")
    user_feeling = st.text_area(
        "편하게 적어보세요. 여기엔 정답이 없어요.",
        placeholder="예: 오늘도 이력서를 못 썼어... 괜히 불안하고 자신감이 없어졌어",
        key="feeling_input",
    )

    if st.button("마음 나누기 💬", key="mind_care_btn"):
        if not user_feeling.strip():
            st.warning("마음을 편하게 적어주세요 :)")
        elif check_crisis_signal(user_feeling):
            # AI를 부르기 전에, 위기 신호는 코드 단에서 먼저 걸러서 전문 상담 정보를 안내해요.
            st.error(
                "💙 많이 힘든 마음이 느껴져요. 혼자 견디지 않아도 돼요.\n\n"
                "**24시간, 바로 이야기할 수 있는 곳이에요**\n"
                "- 자살예방상담전화 ☎ 1393\n"
                "- 정신건강 위기상담전화 ☎ 1577-0199\n"
                "- 청소년 상담 ☎ 1388\n\n"
                "지금 이 순간, 당신의 이야기를 들어줄 준비가 된 사람들이 있어요."
            )
        else:
            with st.spinner("AI가 당신의 이야기를 듣고 있어요..."):
                response = get_empathy_response(user_feeling)
            st.session_state.chat_history.append({"user": user_feeling, "ai": response})

    for chat in reversed(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(chat["user"])
        with st.chat_message("assistant"):
            st.write(chat["ai"])

# ===== Tab 2: 공공 지원금 한눈에 =====
with tab2:
    st.subheader(f"{region} · {unemployment_period} 청년님께 맞는 지원 정책")
    st.caption("아래 정책은 데모용 샘플 데이터예요. 실제 신청 전엔 꼭 공식 사이트에서 최신 정보를 확인하세요.")

    matched = get_matching_policies(unemployment_months)

    for policy, eligible in matched:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"#### {policy['name']}")
                st.caption(f"{policy['org']} · {policy['age_range']}")
            with col2:
                if eligible:
                    st.success("✅ 조건 충족")
                else:
                    st.info("ℹ️ 조건 확인")

            st.write(policy["summary"])
            st.markdown(f"**지원 내용**: {policy['benefit']}")
            st.markdown(f"**추가 조건**: {policy['extra_condition']}")
            st.markdown(f"**신청 방법**: {policy['how_to_apply']} · [바로가기]({policy['url']})")

# ===== Tab 3: AI 공백기 변환기 =====
with tab3:
    st.subheader("쉬는 동안 했던 활동, 강점으로 바꿔드려요")
    st.caption("아무리 소소해도 괜찮아요. 있는 그대로 솔직하게 적어주세요.")

    gap_activity = st.text_area(
        "쉬는 동안 했던 일을 적어주세요",
        placeholder="예: OTT 정주행하고, 가끔 블로그에 감상 글 쓰고, 유튜브로 요리 영상 챙겨봤어요",
        key="gap_activity_input",
    )

    if st.button("직무 역량으로 변환하기 ✨", key="gap_convert_btn"):
        if not gap_activity.strip():
            st.warning("활동 내용을 적어주세요 :)")
        else:
            with st.spinner("AI가 활동 속 강점을 찾고 있어요..."):
                result = convert_gap_activity(gap_activity, interest_field)
            st.session_state.gap_year_result = result

    if st.session_state.gap_year_result:
        st.divider()
        st.markdown(st.session_state.gap_year_result)
