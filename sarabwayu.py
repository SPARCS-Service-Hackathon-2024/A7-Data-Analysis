import pandas as pd
import streamlit as st
import numpy as np
import json
import matplotlib
import re
import matplotlib.pyplot as plt

from wordcloud import WordCloud
from collections import Counter
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

def load_survey():
    df = pd.read_excel('Sparcs_해커톤_설문조사_응답.xlsx')
    return df

def load_job_change():
    df = pd.read_csv('대전광역시_직업_분야별_변화추이.csv', encoding='cp949')
    return df

def render_sidebar():
    with st.sidebar:
        choose = option_menu("데이터셋", ["한달살이 검색량", "대전청년인구 감소추이", "연도별 빈집 개수 추이", "설문조사", "대전 집 현황", "대전 직업 분야별 변화추이"],
                             icons=['house', 'people', 'kanban', 'check-square', 'graph-down', 'person'],
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
    st.markdown("*[출처] 네이버페이 부동산 데이터: https://m.land.naver.com/, 크롤링일자 : 2024.02.14*")
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

    cleaned_labels = [re.sub(r'\(\d+~\d+\)', '', label) for label in df_sorted.index]
    fig, ax = plt.subplots()

    ax.bar(df.index, df_sorted['비율'], color=gradient_colors)
    ax.set_title('점수 분포')
    ax.set_xlabel('지역')
    ax.set_ylabel('1, 2등급 비율')

    ax.tick_params(axis='x', labelsize=8)
    ax.set_xticklabels([label[:2] + '\n' + label[2:] if len(label) > 2 else label for label in cleaned_labels])
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

def survey(df):
    st.header('설문조사')
    filtered = df[df[' 한달살이 이후에 해당 지역에서 더 거주하고 싶다는 생각이 얼마나 들었나요?'].isin([1,2,3,4,5])]
    value_counts = filtered[' 한달살이 이후에 해당 지역에서 더 거주하고 싶다는 생각이 얼마나 들었나요?'].value_counts()

    values = range(1, 6) 
    heights = [0, 3, 2, 5, 0] 

    fig, ax = plt.subplots()
    ax.bar(values, heights, color='#864AE1') 
    ax.set_title('한달살이 이후 더 거주할 의향이 얼마나 있나요?')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')

    st.pyplot(fig)

    # 설문1
    all_values = []
    df['한달살이 지역을 선택할 때 \n가장 중요한 것은 어떤 것이라고 생각하나요?\n(중복 선택 가능)'].str.split(',').apply(all_values.extend)

    value_counts1 = Counter(all_values)

    # 설문2
    all_values = []
    df['타지역과 대전을 비교했을 때, \n대전만의 강점은 어떤 것이 있다고 생각하나요?'].str.split(',').apply(all_values.extend)

    value_counts2 = Counter(all_values)

    all_values = []
    def extend_non_empty_values(row):
        # row가 문자열인 경우에만 처리
        if isinstance(row, str):
            non_empty_values = [value for value in row.split(',') if value and value.strip()]
            all_values.extend(non_empty_values)

    # NaN 값이나 누락된 값이 있을 수 있는 컬럼에 대해 처리
    df['한달살기를 고려한다면,\n다음 선택지 중에서 대전에 부족한 부분은 어떤 것이 있나요?\n(중복 선택 가능)'].apply(extend_non_empty_values)

    # 모든 값의 빈도 계산
    value_counts3 = Counter(all_values)

    xlist = ['교통 편의성','거주 비용 및 시설','관광 인프라','원하는 기간 동안의 한달살이 서비스','편의 시설']  # 1부터 5까지의 값
    ylist1 = [25,16,30,15,12]
    ylist3 = [6,22,18,24,3]

    fig, ax = plt.subplots()
    ax.bar(xlist, ylist3,color='#864AE1')
    ax.set_title('대전에 한달살이 서비스를 하기 위해서 필요한 것은 어떤 것이 있을까요?')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')

    ax.tick_params(axis='x', labelsize=8)
    ax.set_xticklabels([label[:5] + '\n' + label[5:] if len(label) > 5 else label for label in xlist])
    
    st.pyplot(fig)


    category_counts = df['대전의 부족한 문제가 보완된다면\n대전에서 한달살이를 할 의향이 있나요?'].value_counts()

    fig, ax = plt.subplots()
    ax.set_title('대전의 부족한 문제가 보완된다면\n대전에서 한달살이를 할 의향이 있나요?')
    ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90, colors=['#864AE1','gold'])
    ax.axis('equal')

    st.pyplot(fig)

def job_change(df):
    st.header('대전광역시 직업 분야별 변화추이')
    df.set_index('산업별',inplace=True)
    df['사업체 변화율'] = df['2022 사업체 수']/ df['2020 사업체 수']
    df['종사자 변화율'] = df['2022 종사자수']/ df['2020 종사자 수']
    df['매출액 변화율'] = df['2022 매출액']/ df['2020 매출액']
    df['변화율 합'] = df['사업체 변화율'] + df['종사자 변화율'] + df['매출액 변화율']
    df['변화율 합'] = df['변화율 합'] -3
    df_sorted = df.sort_values(by = '변화율 합',ascending = False)

    n = len(df_sorted)
    gradient_colors = [np.array(start_color) + (np.array(end_color) - np.array(start_color)) * i / (n - 1) for i in range(n)]
    gradient_colors = [tuple(c / 255 for c in color) for color in gradient_colors]

    fig, ax = plt.subplots()
    ax.bar(df_sorted.index, df_sorted['변화율 합'], color=gradient_colors)
    ax.set_title('성장률 분석')
    ax.set_xlabel('분야')
    ax.set_ylabel('성장률')

    ax.tick_params(axis='x', labelsize=8)
    cleaned_labels = [re.sub(r'\(\d+~\d+\)', '', label) for label in df_sorted.index]
    ax.set_xticklabels([label[:2] + '\n' + label[2:] if len(label) > 2 else label for label in df_sorted.index])
    st.pyplot(fig)


start_color = hex_to_rgb("#5A25AA")
end_color = hex_to_rgb("#DC88FF")

if __name__ == "__main__":
    df_daily = load_data()
    df_population = load_population_data()
    apartment_info = load_apartment_info()
    df_num = load_num_data()
    df_local_num = load_local_num_data()
    df_survey = load_survey()
    df_job_change = load_job_change()
    choose = render_sidebar()

    if choose == "한달살이 검색량":
        render_chart(df_daily, 2020)
    elif choose == "대전청년인구 감소추이":
        render_bar_chart(df_population)
    elif choose == "연도별 빈집 개수 추이":
        num_year(df_num)
        local_num_year(df_local_num)
    elif choose == "설문조사":
        survey(df_survey)
    elif choose == "대전 집 현황":
        render_wordcloud(apartment_info)
    elif choose == "대전 직업 분야별 변화추이":
        job_change(df_job_change)