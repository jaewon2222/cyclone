import streamlit as st
import math

# 페이지 설정
st.set_page_config(page_title="온대 저기압 (Simpler)", layout="wide")

st.title("🌪️ 온대 저기압 데이터 대시보드")
st.caption("Matplotlib 없이 Streamlit 기본 차트만 사용한 버전입니다.")

# 1. 파라미터 조절
intensity = st.slider("저기압 강도 (hPa 감쇄)", 10, 60, 30)
radius_scale = st.slider("영향 반경", 1.0, 5.0, 2.5)

# 2. 데이터 계산 (Numpy 없이 순수 파이썬 리스트 사용)
# 중심에서 멀어질수록 기압이 어떻게 변하는지 계산
distances = range(0, 20)  # 거리 0부터 20까지
pressures = []

for r in distances:
    # 기압 계산 공식 (가우시안 분포)
    p = 1013 - intensity * math.exp(- (r**2) / (2 * (radius_scale * 2)**2))
    pressures.append(p)

# 3. 데이터 시각화 (Streamlit 내장 차트 사용)
st.subheader("📉 중심으로부터의 거리에 따른 기압 변화")
st.markdown("왼쪽(0)이 저기압 중심이고, 오른쪽으로 갈수록 기압이 높아집니다.")

# 딕셔너리 형태로 데이터 생성
chart_data = {
    "거리": distances,
    "기압(hPa)": pressures
}

# 꺾은선 그래프 그리기 (내장 함수)
st.line_chart(chart_data, x="거리", y="기압(hPa)")

# 4. 상태 표시
st.metric(label="현재 중심 기압", value=f"{min(pressures):.1f} hPa")
st.info("이 버전은 지도를 그리지 않기 때문에 Matplotlib 설치가 필요 없습니다.")
