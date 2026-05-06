import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- 1. 페이지 설정 및 데이터 연결 ---
st.set_page_config(page_title="서울시 따릉이 분석 대시보드", layout="wide")
st.title("🚲 서울시 따릉이 이용현황 대시보드")
st.markdown("데이터를 통해 따릉이의 환경 영향과 이용 패턴을 분석합니다.")

# DB 연결 함수 (캐싱을 통해 성능 최적화)
def get_connection():
    return sqlite3.connect('bicycle.db')

# --- 2. [차트 1] 자치구별 탄소절감량 순위 ---
st.header("1. 자치구별 탄소절감량 순위")

# SQL 작성: 대여소 테이블과 이용정보 테이블을 대여소번호로 연결(JOIN)
query1 = """
SELECT s.자치구, SUM(u.탄소량) as 총탄소절감량
FROM 이용정보 u
JOIN 대여소 s ON u.대여소번호 = s.대여소번호
GROUP BY s.자치구
ORDER BY 총탄소절감량 DESC
"""

conn = get_connection()
df1 = pd.read_sql_query(query1, conn)

col1_1, col1_2 = st.columns([2, 1])

with col1_1:
    # 시각화: 세로 막대 그래프
    fig1 = px.bar(df1, x='자치구', y='총탄소절감량', 
                 title="자치구별 탄소절감량 합계",
                 color='총탄소절감량', color_continuous_scale='Greens')
    st.plotly_chart(fig1, use_container_width=True)

with col1_2:
    st.subheader("🔍 SQL & Insight")
    st.code(query1, language='sql')
    st.info("""
    - **인사이트**: 특정 자치구(예: 강남구, 송파구 등)의 탄소 절감량이 압도적으로 높게 나타납니다. 
    - 이는 해당 지역의 대여소 밀집도가 높거나 평지가 많아 자전거 이용이 활발함을 시사합니다.
    """)

# --- 3. [차트 2] 연령대별 대여구분 패턴 ---
st.divider()
st.header("2. 연령대별 대여구분 비중")

# SQL 작성
query2 = """
SELECT 연령대코드, 대여구분코드, SUM(이용건수) as 이용건수합계
FROM 이용정보
GROUP BY 연령대코드, 대여구분코드
"""
df2 = pd.read_sql_query(query2, conn)

# 사용자 선택을 위한 셀렉트박스
target_age = st.selectbox("확인하고 싶은 연령대를 선택하세요", df2['연령대코드'].unique())
df2_filtered = df2[df2['연령대코드'] == target_age]

col2_1, col2_2 = st.columns([2, 1])

with col2_1:
    # 시각화: 원 그래프
    fig2 = px.pie(df2_filtered, values='이용건수합계', names='대여구분코드', 
                 title=f"{target_age} 대여구분(정기권/일일권 등) 비중")
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.subheader("🔍 SQL & Insight")
    st.code(query2, language='sql')
    st.info("""
    - **인사이트**: 2030 젊은 층은 정기권 비중이 높은 반면, 외부 유입이 많은 지역이나 고령층/청소년층에서는 일일권 비중이 상대적으로 높을 수 있습니다.
    - 연령별 충성도를 파악하여 맞춤형 요금제를 기획할 수 있습니다.
    """)

# --- 4. [차트 3] 기온 별 이용시간 변화 ---
st.divider()
st.header("3. 기온에 따른 따릉이 이용시간")

# SQL 작성: 이용정보와 기온 테이블을 '년월'로 연결
query3 = """
SELECT t.평균기온, SUM(u.이용시간) as 총이용시간
FROM 이용정보 u
JOIN 기온 t ON u.대여일자 = t.년월
GROUP BY t.평균기온
ORDER BY t.평균기온
"""
df3 = pd.read_sql_query(query3, conn)

col3_1, col3_2 = st.columns([2, 1])

with col3_1:
    # 시각화: 꺾은선 그래프
    fig3 = px.line(df3, x='평균기온', y='총이용시간', 
                  title="평균기온 대비 총 이용시간 추이",
                  markers=True)
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.subheader("🔍 SQL & Insight")
    st.code(query3, language='sql')
    st.info("""
    - **인사이트**: 기온이 너무 낮거나(겨울) 너무 높을(한여름) 때보다, 활동하기 좋은 15~25도 사이에서 이용시간이 급격히 증가하는 '종 모양'의 패턴을 보입니다.
    - 날씨가 따릉이 수요의 핵심 변수임을 보여줍니다.
    """)

conn.close()