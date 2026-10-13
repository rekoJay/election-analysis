import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr

# 1. 페이지 설정
st.set_page_config(page_title="선거관리위원회 인력 공급 구조 분석", layout="wide")

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    file_path = "선거별_원자료_최종통합완료_오류수정.xlsx"
    df = pd.read_excel(file_path, sheet_name=0)
    
    # 데이터 정제
    df = df[df['선거명'] != '제9회 지방선거']
    df = df.dropna(subset=['지자체_공무원_현원'])
    
    # 지표 생성
    df['X_압력지수'] = df['동원압력지수(%)']
    df['Y_지방직_의존도'] = (df['3대사무원_지방직_총원'] / df['3대사무원_총원']) * 100
    
    return df

df = load_data()

# 3. 대시보드 제목
st.title("📊 선거관리위원회 인력 공급 구조 분석 대시보드")

# 4. 분석 선거 선택
elections = df['선거명'].unique()
selected_election = st.selectbox("📌 분석을 원하는 선거를 선택하세요:", elections)

sub_df = df[df['선거명'] == selected_election].copy()

# 5. 통계량 계산
x_median = sub_df['X_압력지수'].median()
y_median = sub_df['Y_지방직_의존도'].median()
corr, p_value = pearsonr(sub_df['X_압력지수'], sub_df['Y_지방직_의존도'])
m, b = np.polyfit(sub_df['X_압력지수'], sub_df['Y_지방직_의존도'], 1)

# 통계 요약 지표
st.subheader("통계 분석 결과")
col1, col2, col3 = st.columns(3)
col1.metric("상관계수 (r)", f"{corr:.4f}")
col2.metric("유의확률 (p-value)", f"{p_value:.4e}")
col3.metric("회귀식", f"y = {m:.4f}x + {b:.2f}")

# 6. 시각화
fig = px.scatter(
    sub_df, 
    x='X_압력지수', 
    y='Y_지방직_의존도',
    hover_name='통합_시군구',
    hover_data={'X_압력지수': ':.1f', 'Y_지방직_의존도': ':.1f'},
    title=f"{selected_election} 4분면 분석 (중앙값 기준)",
    labels={'X_압력지수': '동원압력지수 (필요인력/공무원현원)', 'Y_지방직_의존도': '지방직 공무원 의존도 (%)'},
    opacity=0.7
)

# 중앙값 기준선
fig.add_vline(x=x_median, line_dash="dash", line_color="green", annotation_text=f"X 중앙값: {x_median:.1f}")
fig.add_hline(y=y_median, line_dash="dash", line_color="green", annotation_text=f"Y 중앙값: {y_median:.1f}")

# 선형 회귀선
x_range = np.linspace(sub_df['X_압력지수'].min(), sub_df['X_압력지수'].max(), 100)
y_range = m * x_range + b
fig.add_traces(go.Scatter(x=x_range, y=y_range, mode='lines', name='선형 회귀선', line=dict(color='red', width=2)))

fig.update_layout(height=600, title_font_size=20)
st.plotly_chart(fig, use_container_width=True)

# 7. 사분면별 지자체 리스트
st.subheader("📋 사분면별 소속 위원회 목록")

q1 = sub_df[(sub_df['X_압력지수'] >= x_median) & (sub_df['Y_지방직_의존도'] >= y_median)]
q2 = sub_df[(sub_df['X_압력지수'] < x_median) & (sub_df['Y_지방직_의존도'] >= y_median)]
q3 = sub_df[(sub_df['X_압력지수'] < x_median) & (sub_df['Y_지방직_의존도'] < y_median)]
q4 = sub_df[(sub_df['X_압력지수'] >= x_median) & (sub_df['Y_지방직_의존도'] < y_median)]

display_cols = ['통합_시군구', 'X_압력지수', 'Y_지방직_의존도', '지자체_공무원_현원']

tab1, tab2, tab3, tab4 = st.tabs(["1사분면", "2사분면", "3사분면", "4사분면"])

with tab1:
    st.dataframe(q1[display_cols].sort_values(by='X_압력지수', ascending=False).reset_index(drop=True))
with tab2:
    st.dataframe(q2[display_cols].sort_values(by='Y_지방직_의존도', ascending=False).reset_index(drop=True))
with tab3:
    st.dataframe(q3[display_cols].sort_values(by='X_압력지수', ascending=True).reset_index(drop=True))
with tab4:
    st.dataframe(q4[display_cols].sort_values(by='Y_지방직_의존도', ascending=True).reset_index(drop=True))