import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
import time

# --- 1. 기본 설정 및 앱 제목 ---
st.set_page_config(page_title="나의 재무 비서", layout="wide")
st.title("📊 나의 맞춤형 재무 비서 및 투자 전략 보드")
st.markdown("미래에셋증권 및 우리은행(DC/IRP) 계좌 캡처 이미지를 업로드하면 포트폴리오를 분석해 드립니다.")

# --- 2. 임시 데이터 생성 함수 (실제 환경에서는 OCR 및 증권 API로 대체됨) ---
def extract_mock_data_from_image(account_type):
    """
    이미지에서 추출된 데이터를 시뮬레이션하는 함수입니다.
    실제 개발 시 이 부분에 Tesseract OCR API 또는 Vision API가 들어갑니다.
    """
    if account_type == "mirae":
        return pd.DataFrame({
            "종목명": ["삼성전자", "SK하이닉스", "현대차", "NAVER", "예수금"],
            "매입가": [70000, 130000, 200000, 210000, 1],
            "현재가": [75000, 150000, 195000, 190000, 1],
            "수량": [100, 50, 30, 20, 5000000],
            "PER": [15.2, 12.5, 5.8, 30.1, 0],
            "PBR": [1.3, 1.5, 0.6, 1.2, 0]
        })
    elif account_type == "woori":
        return pd.DataFrame({
            "종목명": ["TIGER 미국S&P500", "KODEX 200", "예금형 자산"],
            "매입가": [12000, 35000, 1],
            "현재가": [14000, 36000, 1],
            "수량": [500, 200, 10000000],
            "PER": [20.1, 10.5, 0],
            "PBR": [3.5, 1.0, 0]
        })

def calculate_portfolio(df):
    """데이터프레임에 평가금액 및 수익률을 계산하여 추가합니다."""
    df['평가금액'] = df['현재가'] * df['수량']
    df['매입금액'] = df['매입가'] * df['수량']
    df['수익률(%)'] = np.where(df['종목명'].isin(['예수금', '예금형 자산']), 
                           0, 
                           ((df['현재가'] - df['매입가']) / df['매입가'] * 100).round(2))
    return df

# --- 3. 사이드바: 데이터 업로드 영역 ---
st.sidebar.header("📁 계좌 캡처 업로드")
mirae_img = st.sidebar.file_uploader("미래에셋증권 캡처 이미지", type=['png', 'jpg', 'jpeg'])
woori_img = st.sidebar.file_uploader("우리은행 DC/IRP 캡처 이미지", type=['png', 'jpg', 'jpeg'])

# --- 4. 메인 화면 구성 ---
if mirae_img or woori_img:
    with st.spinner('이미지를 분석하고 데이터를 추출하는 중입니다...'):
        time.sleep(1) # 분석 지연 시간 시뮬레이션
        
    st.success("데이터 업데이트 완료!")
    
    # 데이터 처리
    df_mirae = calculate_portfolio(extract_mock_data_from_image("mirae")) if mirae_img else pd.DataFrame()
    df_woori = calculate_portfolio(extract_mock_data_from_image("woori")) if woori_img else pd.DataFrame()
    
    df_total = pd.concat([df_mirae, df_woori]).reset_index(drop=True)
    total_asset = df_total['평가금액'].sum()
    
    # --- 상단 요약 지표 ---
    st.subheader("💰 총 자산 요약")
    col1, col2, col3 = st.columns(3)
    col1.metric("총 자산 평가액", f"{total_asset:,.0f} 원")
    
    total_buy = df_total['매입금액'].sum()
    total_profit = total_asset - total_buy
    profit_rate = (total_profit / total_buy) * 100 if total_buy > 0 else 0
    col2.metric("총 평가 손익", f"{total_profit:,.0f} 원", f"{profit_rate:.2f}%")
    
    cash = df_total[df_total['종목명'].isin(['예수금', '예금형 자산'])]['평가금액'].sum()
    col3.metric("현금 비중 (예수금/예금)", f"{cash:,.0f} 원", f"{(cash/total_asset)*100:.1f}%", delta_color="off")

    st.divider()

    # --- 시각화 및 상세 데이터 ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🥧 자산 분산 포트폴리오")
        # Plotly를 이용한 파이 차트
        fig = px.pie(df_total, values='평가금액', names='종목명', hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📈 기술적/기본적 분석 시그널")
        # 가상의 이동평균선 시그널 및 PER/PBR 데이터 매핑
        analysis_data = []
        for index, row in df_total[~df_total['종목명'].isin(['예수금', '예금형 자산'])].iterrows():
            signal = "매수" if row['PER'] < 15 and row['PBR'] < 1.5 else "관망"
            if row['수익률(%)'] < -5: signal = "추가매수(물타기) 고려"
            
            analysis_data.append({
                "종목명": row['종목명'],
                "현재 PER": row['PER'],
                "현재 PBR": row['PBR'],
                "20일선 추세": np.random.choice(["상승", "하락", "횡보"]), # 가상 데이터
                "AI 투자의견": signal
            })
        st.dataframe(pd.DataFrame(analysis_data), use_container_width=True)

    # --- 상세 계좌 정보 ---
    st.subheader("📋 상세 보유 종목 현황")
    st.dataframe(df_total[['종목명', '매입가', '현재가', '수량', '매입금액', '평가금액', '수익률(%)']].style.format({
        "매입가": "{:,.0f}", "현재가": "{:,.0f}", "수량": "{:,.0f}", 
        "매입금액": "{:,.0f}", "평가금액": "{:,.0f}", "수익률(%)": "{:.2f}%"
    }), use_container_width=True)

    # --- AI 투자 전략 리포트 ---
    st.divider()
    st.subheader("💡 재무 비서 종합 투자 전략 (업데이트 완료)")
    
    st.info(f"""
    **[포트폴리오 분석 결과]**
    - 현재 주식과 현금 비중이 {(1-cash/total_asset)*100:.1f} : {(cash/total_asset)*100:.1f} 입니다. 
    - 시장 변동성에 대비하여 현금 비중을 20~30% 수준으로 유지하는 것을 권장합니다.
    - 'TIGER 미국S&P500'은 꾸준한 우상향 추세(20일선 상승)를 보이고 있으므로 장기 보유 전략이 유효합니다.
    - 일부 종목(예: 네이버, 현대차)은 가치 지표(PER/PBR) 대비 저평가 또는 고평가 국면에 있으므로, 목표 수익률 도달 시 분할 매도를 통한 리스크 관리가 필요합니다.
    
    **[행동 지침]**
    1. 계좌 내 흩어져 있는 예수금을 파악하여 CMA 등 단기 이자가 붙는 곳으로 일원화.
    2. 연금저축(DC/IRP) 포트폴리오는 ETF 비중을 늘려 글로벌 자산배분(미국 증시 등)을 강화할 것.
    """)

else:
    st.info("👈 왼쪽 사이드바에서 미래에셋증권 또는 우리은행 계좌 캡처 이미지를 업로드해 주세요.")