import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time  # 시간 지연을 위해 추가

# 페이지 설정
st.set_page_config(page_title="온대 저기압 시뮬레이터", layout="wide")

st.title("🌪️ 온대 저기압 시뮬레이터 (자동 재생 버전)")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 초기 설정")
intensity = st.sidebar.slider("저기압 강도 (hPa 감쇄)", 10, 60, 30)
radius_scale = st.sidebar.slider("저기압 반경 (Scale)", 1.0, 5.0, 2.5)

# 속도 조절
speed = st.sidebar.slider("애니메이션 속도 (초)", 0.01, 0.5, 0.1, help="낮을수록 빠릅니다.")

# 시작 버튼
start_btn = st.button("▶️ 시뮬레이션 시작 (Auto Play)")

# --- 그래프를 그릴 빈 공간(Container) 확보 ---
# 이 부분이 핵심입니다. 여기에 그림을 계속 덮어씁니다.
plot_placeholder = st.empty()
info_placeholder = st.empty()

# --- 시뮬레이션 로직 ---

def draw_cyclone(time_step):
    # 1. 그리드 및 기본 데이터 생성
    N = 100
    x = np.linspace(-10, 10, N)
    y = np.linspace(-10, 10, N)
    X, Y = np.meshgrid(x, y)
    cx, cy = 0, 0
    R = np.sqrt((X - cx)**2 + (Y - cy)**2)

    # 2. 기압장 및 바람장 계산
    P = 1013 - intensity * np.exp(- (R**2) / (2 * radius_scale**2))
    u = -1 * (Y - cy) - 0.2 * (X - cx)
    v = (X - cx) - 0.2 * (Y - cy)
    speed_factor = np.exp(- (R**2) / (2 * (radius_scale*1.5)**2))
    u = u * speed_factor
    v = v * speed_factor

    # 3. 전선 위치 계산 (시간에 따라 변함)
    angle_warm = np.radians(15)
    angle_cold = np.radians(240 - (time_step * 1.5))
    
    # 폐색 여부 판단
    occluded = False
    if angle_cold <= angle_warm + np.radians(10):
        occluded = True
        angle_cold = angle_warm 

    front_len = 7
    wx = [cx, cx + front_len * np.cos(angle_warm)]
    wy = [cy, cy + front_len * np.sin(angle_warm)]
    cx_line = [cx, cx + front_len * np.cos(angle_cold)]
    cy_line = [cy, cy + front_len * np.sin(angle_cold)]

    # 4. 그림 그리기
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 등압선
    contours = ax.contour(X, Y, P, levels=np.arange(960, 1016, 4), colors='black', linewidths=1)
    ax.clabel(contours, inline=True, fontsize=8, fmt='%1.0f')
    
    # 바람 화살표
    skip = 8
    ax.quiver(X[::skip, ::skip], Y[::skip, ::skip], u[::skip, ::skip], v[::skip, ::skip], 
              color='gray', alpha=0.5, scale=50, width=0.003)

    # 전선 그리기
    if not occluded:
        ax.plot(wx, wy, color='red', linewidth=3, label='온난전선')
        ax.plot(cx_line, cy_line, color='blue', linewidth=3, label='한랭전선')
    else:
        ox = [cx, cx + front_len * np.cos(angle_warm)]
        oy = [cy, cy + front_len * np.sin(angle_warm)]
        ax.plot(ox, oy, color='purple', linewidth=3, linestyle='--', label='폐색전선')

    # 그래프 꾸미기
    current_pressure = 1013 - intensity
    status = "폐색됨 (소멸 단계)" if occluded else "발달 중 (성숙 단계)"
    ax.set_title(f"Time Step: {time_step} | 상태: {status}")
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    return fig, status, current_pressure

# 버튼을 누르면 루프 실행
if start_btn:
    # 0부터 100까지 시간(t)을 흐르게 함
    for t in range(0, 101, 2):
        # 그림 그리는 함수 호출
        fig, status, pres = draw_cyclone(t)
        
        # 'plot_placeholder' 자리에 그림 덮어쓰기
        plot_placeholder.pyplot(fig)
        
        # 정보창 업데이트
        info_placeholder.info(f"⏳ 현재 진행도: {t}% | 중심기압: {pres} hPa | {status}")
        
        # 메모리 관리를 위해 그림 닫기
        plt.close(fig)
        
        # 속도 조절 (잠깐 멈춤)
        time.sleep(speed)
else:
    # 버튼 누르기 전 대기 화면 (time_step = 0)
    fig, status, pres = draw_cyclone(0)
    plot_placeholder.pyplot(fig)
    info_placeholder.markdown("☝️ 위의 **'시뮬레이션 시작'** 버튼을 누르면 저기압이 이동합니다.")
