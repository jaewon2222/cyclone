import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 페이지 설정
st.set_page_config(page_title="온대 저기압 시뮬레이터", layout="wide")

st.title("🌪️ 온대 저기압 시뮬레이터 (Mid-latitude Cyclone)")
st.markdown("""
이 시뮬레이터는 온대 저기압의 구조(기압 배치, 바람, 전선)를 수학적으로 단순화하여 시각화합니다.
사이드바에서 파라미터를 조절하여 저기압의 발달 과정을 관찰해보세요.
""")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 파라미터 조절")

# 1. 저기압 강도 (중심 기압)
intensity = st.sidebar.slider("저기압 강도 (hPa 감쇄)", 10, 60, 30, help="중심 기압이 얼마나 낮아질지 결정합니다.")
central_pressure = 1013 - intensity

# 2. 저기압 크기 (반경)
radius_scale = st.sidebar.slider("저기압 반경 (Scale)", 1.0, 5.0, 2.5)

# 3. 시간 경과 (전선 이동 및 폐색)
time_step = st.sidebar.slider("시간 경과 (발달 단계)", 0, 100, 20, help="시간이 지날수록 한랭전선이 온난전선을 따라잡아 폐색전선이 형성됩니다.")

# --- 데이터 생성 (수학적 모델링) ---

# 그리드 생성
N = 100
x = np.linspace(-10, 10, N)
y = np.linspace(-10, 10, N)
X, Y = np.meshgrid(x, y)

# 중심 위치 (시간에 따라 약간 이동 가능하게 할 수 있음, 여기선 고정)
cx, cy = 0, 0

# 거리 계산
R = np.sqrt((X - cx)**2 + (Y - cy)**2)

# 기압장 계산 (가우시안 분포 역수)
# P_env = 1013 hPa
P = 1013 - intensity * np.exp(- (R**2) / (2 * radius_scale**2))

# 바람장 계산 (기압경도력에 의한 반시계 회전 + 수렴)
# 단순화: 중심을 향해 반시계 방향으로 회전하는 벡터장
u = -1 * (Y - cy) - 0.2 * (X - cx)  # u 성분 (x축 바람)
v = (X - cx) - 0.2 * (Y - cy)       # v 성분 (y축 바람)

# 거리에 따른 바람 세기 조절 (중심 근처 강함, 먼 곳 약함)
speed_factor = np.exp(- (R**2) / (2 * (radius_scale*1.5)**2))
u = u * speed_factor
v = v * speed_factor

# --- 시각화 (Matplotlib) ---
fig, ax = plt.subplots(figsize=(10, 8))

# 1. 등압선 (Isobars) 그리기
contours = ax.contour(X, Y, P, levels=np.arange(960, 1016, 4), colors='black', linewidths=1)
ax.clabel(contours, inline=True, fontsize=8, fmt='%1.0f')

# 2. 바람 벡터 (Wind Quivers) - 가독성을 위해 간격 띄워서 표시
skip = 8
ax.quiver(X[::skip, ::skip], Y[::skip, ::skip], u[::skip, ::skip], v[::skip, ::skip], 
          color='gray', alpha=0.5, scale=50, width=0.003)

# 3. 전선 그리기 (Fronts)
# 전선은 수학적 모델보다는 기하학적 위치로 표현합니다.
# 시간(time_step)에 따라 각도가 변하여 폐색 과정을 묘사

# 온난 전선 (Warm Front) - 오른쪽 위로 뻗음
# 한랭 전선 (Cold Front) - 왼쪽 아래로 뻗음 (더 빨리 이동)

# 각도 설정 (단위: 라디안)
angle_warm = np.radians(15)  # 온난전선은 천천히 이동
angle_cold = np.radians(240 - (time_step * 1.5)) # 한랭전선은 빨리 회전하며 따라잡음

# 폐색 여부 확인
occluded = False
if angle_cold <= angle_warm + np.radians(10): # 거의 따라잡음
    occluded = True
    angle_cold = angle_warm # 겹쳐짐 (폐색)

# 전선 길이
front_len = 7

# 온난 전선 좌표
wx = [cx, cx + front_len * np.cos(angle_warm)]
wy = [cy, cy + front_len * np.sin(angle_warm)]

# 한랭 전선 좌표
cx_line = [cx, cx + front_len * np.cos(angle_cold)]
cy_line = [cy, cy + front_len * np.sin(angle_cold)]

# 전선 그리기
if not occluded:
    # 온난전선 (빨강, 반원 마커는 복잡하므로 실선으로 대체하되 스타일 지정)
    ax.plot(wx, wy, color='red', linewidth=3, label='온난전선 (Warm Front)')
    # 한랭전선 (파랑)
    ax.plot(cx_line, cy_line, color='blue', linewidth=3, label='한랭전선 (Cold Front)')
else:
    # 폐색전선 (보라)
    ox = [cx, cx + front_len * np.cos(angle_warm)]
    oy = [cy, cy + front_len * np.sin(angle_warm)]
    ax.plot(ox, oy, color='purple', linewidth=3, linestyle='--', label='폐색전선 (Occluded Front)')

# 구역 표시 (Warm Sector)
if not occluded:
    # 한랭전선과 온난전선 사이의 따뜻한 구역 색칠
    # 폴리곤 생성 로직은 복잡하므로 텍스트로 대체하거나 간단한 fill
    pass

# 그래프 꾸미기
ax.set_title(f"중심 기압: {int(central_pressure)} hPa | 단계: {'폐색됨' if occluded else '발달 중'}")
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_xlabel("동서 거리 (Relative)")
ax.set_ylabel("남북 거리 (Relative)")
ax.legend(loc='upper right')
ax.grid(True, linestyle=':', alpha=0.6)

# Streamlit에 플롯 표시
st.pyplot(fig)

# --- 설명 섹션 ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("💡 관전 포인트")
    st.markdown("""
    * **바람의 방향:** 등압선에 평행하지 않고, 마찰력 때문에 저기압 중심을 향해 15~30도 안쪽으로 불어 들어옵니다.
    * **등압선 간격:** 중심 기압이 낮아질수록(강도가 셀수록) 등압선이 조밀해지고 바람이 강해집니다.
    * **전선의 이동:** '시간 경과' 슬라이더를 올리면 한랭전선(파랑)이 온난전선(빨강)을 따라잡아 폐색전선(보라)을 만드는 과정을 볼 수 있습니다.
    """)

with col2:
    st.subheader("📊 현재 상태")
    st.metric(label="중심 기압", value=f"{central_pressure:.1f} hPa", delta=f"표준기압 대비 {central_pressure - 1013:.1f}")
    st.metric(label="전선 상태", value="폐색 전선 형성" if occluded else "개방 파동 (Open Wave)")
