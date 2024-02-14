import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json
import matplotlib

from matplotlib import font_manager, rc
from streamlit_option_menu import option_menu

font_path = "C:/Users/USER/AppData/Local/Microsoft/Windows/Fonts/NotoSansKR-Regular.ttf"

matplotlib.rcParams['font.family'] ='Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] =False

def load_data():
    df = pd.read_excel('키워드사운드_한달살이_검색량.xlsx')
    df['날짜'] = pd.to_datetime(df['날짜'])
    df.set_index('날짜', inplace=True)

    total_search = df['총 검색량']
    df_daily = total_search.resample('D').sum()

    return df_daily

def load_population_data():
    df = pd.read_csv('대전시_10~30대_인구수.csv')
    return df

def load_num_data():
    df = pd.read_excel('빈집_현황_조회.xls')
    return df

def load_local_num_data():
    df = pd.read_csv('대전시_빈집비율.csv', encoding='cp949')
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

    st.line_chart(df_year, color="#864AE1")
    st.markdown(f'**기간 : {year}.01 ~ {year}.12**')

def render_bar_chart(df):
    st.header('대전시 10~30대 인구수')
    st.markdown("*[출처] 공공데이터포털: 통계청_SGIS오픈플랫폼_인구통계*")
    st.write("---")
    df['날짜'] = pd.to_datetime(df['날짜'], format='%Y년%m월') 
    df.set_index('날짜', inplace=True)

    fig, ax = plt.subplots()
    ax.plot(df.index, df['인구수'], marker='o',color='#864AE1')
    ax.set_title('인구 변화 그래프')
    ax.set_xlabel('날짜')
    ax.set_ylabel('인구수')
    ax.grid(True)

    st.pyplot(fig)

def render_wordcloud(data):
    st.header("대전 집 현황")
    st.markdown("*[출처] 네이버페이 부동산 크롤링 데이터: https://m.land.naver.com/*")
    st.write("---")
    detail_descriptions = [item.get('detailDescription', '').replace('없음', '').replace('광고', '').replace('표시', '').replace('중개대상물의', '').replace('명시사항', '').replace('건축물용도', '').replace('방향기준', '') for item in data]
    article_descriptions = [item.get('articleDescription', '') for item in data]
    tag_lists = [', '.join(item.get('tagList', [])) for item in data]

    descriptions_combined = [f"{detail} {article} {tags}" for detail, article, tags in zip(detail_descriptions, article_descriptions, tag_lists)]
    text = ' '.join(descriptions_combined)

    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path, prefer_horizontal=0.9).generate(text)
    st.image(wordcloud.to_array(), use_column_width=True)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def num_year(df):
    st.header('연도별 빈집 개수 추이')
    st.write("---")
    df.set_index('지역', inplace=True)
    col = df.columns
    for i in col:
        df[i] = df[i].str.replace(',', '')
        df[i] = df[i].astype(int)
    df['비율'] = (df['1등급(양호)'] + df['2등급(일반)']) / df['전체 빈집수']
    df_sorted = df.sort_values(by='비율', ascending=False)

    df_sorted.index = df_sorted.index.str.replace('광역시', '')
    df_sorted.index = df_sorted.index.str.replace('특별자치시도', '')
    df_sorted.index = df_sorted.index.str.replace('특별자치시', '')
    df_sorted.index = df_sorted.index.str.replace('특별자치도', '')
    df_sorted.index = df_sorted.index.str.replace('특별시', '')

    n = len(df_sorted)
    gradient_colors = [np.array(start_color) + (np.array(end_color) - np.array(start_color)) * i / (n - 1) for i in range(n)]
    gradient_colors = [tuple(c / 255 for c in color) for color in gradient_colors]

    fig, ax = plt.subplots()
    ax.bar(df_sorted.index, df_sorted['비율'], color=gradient_colors)
    ax.set_title('점수 분포')
    ax.set_xlabel('지역')
    ax.set_ylabel('1,2등급 비율')

    ax.tick_params(axis='x', labelsize=8)
    ax.set_xticklabels([label[:2] + '\n' + label[2:] if len(label) > 2 else label for label in df_sorted.index])
    st.pyplot(fig)


def local_num_year(df):
    df.set_index('행정구역별(시군구)',inplace=True)
    fig, ax1 = plt.subplots()

    color = '#864AE1'
    ax1.set_xlabel('날짜')
    ax1.set_ylabel('빈집비율', color=color)
    ax1.plot(df.index, df['빈집비율'], marker='o', color=color, label='빈집비율')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = '#E14A86'
    ax2.set_ylabel('빈집수', color=color)
    ax2.plot(df.index, df['빈집수'], marker='^', color=color, label='빈집수')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('대전')

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')
    ax1.grid(True)
    
    st.pyplot(fig)


start_color = hex_to_rgb("#5A25AA")
end_color = hex_to_rgb("#DC88FF")

if __name__ == "__main__":
    df_daily = load_data()
    df_population = load_population_data()
    apartment_info = load_apartment_info()
    df_num = load_num_data()
    df_local_num = load_local_num_data()
    choose = render_sidebar()

    if choose == "한달살이 검색량":
        render_chart(df_daily, 2020)
    elif choose == "대전청년인구 감소추이":
        render_bar_chart(df_population)
    elif choose == "연도별 빈집 개수 추이":
        num_year(df_num)
        local_num_year(df_local_num)
    elif choose == "한달살이 할 때 중요하게 생각하는 요소":
        st.header('한달살이 할 때 중요하게 생각하는 요소')
    elif choose == "한달살이 후에 해당 지역에 거주할 의향":
        st.header('한달살이 후에 해당 지역에 거주할 의향')
    elif choose == "대전 집 현황":
        render_wordcloud(apartment_info)