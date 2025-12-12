import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 페이지 설정
st.set_page_config(page_title="온대 저기압 시뮬레이터", layout="wide")

st.title("🌪️ 온대 저기압 시뮬레이터 (수정판)")
st.caption("이제 한랭전선이 온난전선을 확실하게 따라잡아 폐색전선을 만듭니다.")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 초기 설정")
intensity = st.sidebar.slider("저기압 강도", 10, 60, 30)
radius_scale = st.sidebar.slider("저기압 크기", 1.0, 5.0, 2.5)
speed = st.sidebar.slider("애니메이션 속도", 0.01, 0.5, 0.05)

start_btn = st.button("▶️ 시뮬레이션 시작 (Replay)")

# 빈 공간 확보
plot_placeholder = st.empty()
info_placeholder = st.empty()

# --- 시뮬레이션 함수 ---
def draw_cyclone(time_step):
    # 1. 그리드 생성
    N = 100
    lim = 10
    x = np.linspace(-lim, lim, N)
    y = np.linspace(-lim, lim, N)
    X, Y = np.meshgrid(x, y)
    cx, cy = 0, 0
    R = np.sqrt((X - cx)**2 + (Y - cy)**2)

    # 2. 기압장 & 바람장
    P = 1013 - intensity * np.exp(- (R**2) / (2 * radius_scale**2))
    u = -1 * (Y - cy) - 0.2 * (X - cx)
    v = (X - cx) - 0.2 * (Y - cy)
    speed_factor = np.exp(- (R**2) / (2 * (radius_scale*1.5)**2))
    u = u * speed_factor
    v = v * speed_factor

    # --- [수정된 부분: 전선 각도 로직] ---
    # 목표: t=0일 때 벌어져 있다가, t=60쯤에 만남
    
    # 온난전선 (Warm Front): 천천히 반시계 방향 회전
    # 시작: -10도 (약간 남동쪽) -> 속도: 0.5
    deg_warm = -10 + (time_step * 0.5)
    
    # 한랭전선 (Cold Front): 빠르게 반시계 방향 회전하여 따라잡음
    # 시작: -100도 (남서쪽 뒤편) -> 속도: 2.0 (4배 빠름)
    deg_cold = -100 + (time_step * 2.0)

    # 각도를 라디안으로 변환
    angle_warm = np.radians(deg_warm)
    angle_cold = np.radians(deg_cold)
    
    # 폐색(Catch up) 판정
    # 한랭전선 각도가 온난전선보다 커지거나 같아지면 잡은 것
    occluded = False
    if deg_cold >= deg_warm:
        occluded = True
        angle_cold = angle_warm  # 겹쳐서 하나로 표시

    # 전선 좌표 계산
    front_len = 7
    # 온난전선 좌표
    wx = [cx, cx + front_len * np.cos(angle_warm)]
    wy = [cy, cy + front_len * np.sin(angle_warm)]
    # 한랭전선 좌표
    cx_line = [cx, cx + front_len * np.cos(angle_cold)]
    cy_line = [cy, cy + front_len * np.sin(angle_cold)]

    # 3. 그리기
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 등압선
    contours = ax.contour(X, Y, P, levels=np.arange(960, 1016, 4), colors='black', linewidths=1)
    ax.clabel(contours, inline=True, fontsize=8, fmt='%1.0f')
    
    # 바람 (너무 빽빽하지 않게 skip)
    s = 8
    ax.quiver(X[::s, ::s], Y[::s, ::s], u[::s, ::s], v[::s, ::s], 
              color='silver', alpha=0.5, scale=50, width=0.003)

    # 전선 그리기
    if not occluded:
        # 잡히기 전: 따로 그림
        ax.plot(wx, wy, color='red', linewidth=4, alpha=0.8, label='온난전선')
        ax.plot(cx_line, cy_line, color='blue', linewidth=4, alpha=0.8, label='한랭전선')
        
        # 난기역(Warm Sector) 표시 (두 전선 사이)
        # 시각적 효과를 위해 텍스트 추가
        mid_angle = (angle_warm + angle_cold) / 2
        tx = cx + 4 * np.cos(mid_angle)
        ty = cy + 4 * np.sin(mid_angle)
        ax.text(tx, ty, "Warm\nAir", color='orange', ha='center', fontweight='bold')
        
    else:
        # 잡힌 후: 폐색전선 (보라색 점선)
        ox = [cx, cx + front_len * np.cos(angle_warm)]
        oy = [cy, cy + front_len * np.sin(angle_warm)]
        ax.plot(ox, oy, color='purple', linewidth=4, linestyle='--', label='폐색전선')
        ax.text(cx + 4 * np.cos(angle_warm), cy + 4 * np.sin(angle_warm) + 1, "Occluded", color='purple', ha='center')

    # 그래프 설정
    status_text = "⚠️ 폐색됨 (에너지 소멸 중)" if occluded else "⚡ 발달 중 (전선 접근)"
    ax.set_title(f"Time: {time_step}% | {status_text}")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(loc='upper left')
    
    return fig, occluded

# --- 실행 로직 ---
if start_btn:
    progress_bar = st.progress(0)
    
    # 0 ~ 100까지 루프
    for t in range(0, 101, 2):
        fig, is_occluded = draw_cyclone(t)
        
        # 화면 업데이트
        plot_placeholder.pyplot(fig)
        
        # 상태 메시지
        if is_occluded:
            info_placeholder.error(f"🔴 [{t}%] 한랭전선이 따라잡았습니다! 폐색전선 형성.")
        else:
            info_placeholder.info(f"🔵 [{t}%] 한랭전선이 맹렬히 추격 중입니다...")
            
        progress_bar.progress(t)
        plt.close(fig)
        time.sleep(speed)
else:
    # 초기 화면
    fig, _ = draw_cyclone(0)
    plot_placeholder.pyplot(fig)
    info_placeholder.markdown("버튼을 눌러 시뮬레이션을 시작하세요.")
