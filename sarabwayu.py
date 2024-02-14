import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from wordcloud import WordCloud
import json

from matplotlib import font_manager, rc
from streamlit_option_menu import option_menu

font_path = "./font/NotosansKR-Regular.ttf"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

def load_data():
    df = pd.read_excel('키워드사운드_한달살이_검색량.xlsx')
    df['날짜'] = pd.to_datetime(df['날짜'])
    df.set_index('날짜', inplace=True)

    # start_date = '2022-01-20'
    # end_date = '2022-06-01'
    # df = df[df.index >= start_date]
    # df = df[df.index <= end_date]

    total_search = df['총 검색량']
    df_daily = total_search.resample('D').sum()

    return df_daily

def load_population_data():
    df = pd.read_csv('대전시_10~30대_인구수.csv')
    return df

def load_apartment_info():
    with open('apartment_info.jsonl', 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    return data

def render_sidebar():
    with st.sidebar:
        choose = option_menu("데이터셋", ["한달살이 검색량", "대전청년인구 감소추이", "연도별 빈집 개수 추이", "한달살이 할 때 중요하게 생각하는 요소", "한달살이 후에 해당 지역에 거주할 의향", "대전 집 현황"],
                             icons=['house', 'people', 'kanban', ''],
                             menu_icon="메뉴 타이틀 아이콘", default_index=0,
                             styles={
                                 "container": {"padding": "5!important", "background-color": "#fafafa"},
                                 "icon": {"color": "purple", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                              "--hover-color": "#eee"},
                                 "nav-link-selected": {"background-color": "#02ab21"},
                             })
    return choose

def render_chart(df, default_year=2020):
    st.header('한달살이 검색량 그래프')
    st.markdown("*[출처] 키워드사운드 : https://keywordsound.com/*")
    st.write("---")
    year = st.selectbox('연도를 선택하세요:', options=[2020, 2021, 2022, 2023])
    df_year = df[df.index.year == year]
    st.line_chart(df_year)
    st.markdown(f'**기간 : {year}.01 ~ {year}.12**')


def render_bar_chart(df):
    st.header('대전시 10~30대 인구수')
    st.markdown("*[출처] 공공데이터포털: 통계청_SGIS오픈플랫폼_인구통계*")
    st.write("---")
    df['날짜'] = pd.to_datetime(df['날짜'], format='%Y년%m월') 
    df.set_index('날짜', inplace=True)

    scaler = MinMaxScaler()
    df_normalized = scaler.fit_transform(df)
    df_normalized = pd.DataFrame(df_normalized, index=df.index, columns=[col+'_normalized' for col in df.columns])
    
    df_with_normalized = pd.concat([df, df_normalized], axis=1)
    
    st.bar_chart(df_normalized)

    col1, col2 = st.columns(2)
    col1.write(df_with_normalized)
    col2.markdown("원데이터 분포를 유지하면서 정규화를 하기 위해 MinMaxScaler를 이용하여 각 데이터 값들은 0과 1 사이의 값을 가집니다.")
    col2.write("그래프를 살펴보면, 대전시의 10~30대 인구수가 시간이 지남에 따라 감소하는 경향을 보입니다.")

def render_wordcloud(data):
    st.header("대전 집 현황")
    st.markdown("*[출처] 네이버페이 부동산: https://m.land.naver.com/*")
    st.write("---")
    detail_descriptions = [item.get('detailDescription', '').replace('없음', '').replace('광고', '').replace('표시', '').replace('중개대상물의', '').replace('명시사항', '').replace('건축물용도', '').replace('방향기준', '') for item in data]
    article_descriptions = [item.get('articleDescription', '') for item in data]
    tag_lists = [', '.join(item.get('tagList', [])) for item in data]

    descriptions_combined = [f"{detail} {article} {tags}" for detail, article, tags in zip(detail_descriptions, article_descriptions, tag_lists)]
    text = ' '.join(descriptions_combined)

    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path, prefer_horizontal=0.9).generate(text)
    st.image(wordcloud.to_array(), use_column_width=True)

if __name__ == "__main__":
    df_daily = load_data()
    df_population = load_population_data()
    apartment_info = load_apartment_info()
    choose = render_sidebar()

    if choose == "한달살이 검색량":
        render_chart(df_daily, 2020)  # 초기 값으로 2020년을 선택하도록 수정
    elif choose == "대전청년인구 감소추이":
        render_bar_chart(df_population)
    elif choose == "연도별 빈집 개수 추이":
        st.header('연도별 빈집 개수 추이')
    elif choose == "한달살이 할 때 중요하게 생각하는 요소":
        st.header('한달살이 할 때 중요하게 생각하는 요소')
    elif choose == "한달살이 후에 해당 지역에 거주할 의향":
        st.header('한달살이 후에 해당 지역에 거주할 의향')
    elif choose == "대전 집 현황":
        render_wordcloud(apartment_info)