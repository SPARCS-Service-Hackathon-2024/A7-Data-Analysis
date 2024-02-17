# A7-Data-Analysis

카이스트에서 주최하는 Sparcs 2024 서비스 해커톤의 주제인 "지역 사회 문제 해결하기"에서 "청년 인구 감소"를 핵심 문제로 정의했습니다. 자세한 내용은 [여기](https://github.com/SPARCS-Service-Hackathon-2024/A7-Repo) 에서 확인할 수 있습니다.

## 데이터 분석

### '한달살이' 검색량 추이

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/53e447db-d241-4dc9-bfaf-550b806c44e7)

2021년부터 현재까지 ‘한달살이’의 검색량은 꾸준하게 발생한 것을 시각화한 자료로, ‘한달살이’에 대한 수요가 꾸준하게 존재한다는 것을 보여줍니다.


### 대전광역시 빈집 데이터 WordCloud

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/434687d5-553c-400f-96d3-53aa7d13a4dd)

대전광역시에 존재하는 부동산 데이터 중 1년이상 방치된 주거 데이터에 대한 특징을 WordCloud로 시각화한 자료로, 해당 특징들을 통해 사용자가 원하는 주거를 추천해서 제공할 수 있다는 점을 시사합니다.

### 대전광역시 청년 인구 감소 추이

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/a6ca0f15-6dd9-4c40-8f55-2672996029ce)

현재 대전광역시 지역 사회 문제를 파악하기 위해 시각화한 자료로, 꾸준하게 20세 이상 40세 미만의 청년 인구가 꾸준하게 유출되고 있음을 보여줍니다.

### 대전광역시 빈집 현황

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/f79cfe0d-f564-433a-bb9d-437aa2af1e29)

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/15495208-4113-4ad9-b708-87975046833c)

지역별 빈집 중, 1,2등급에 해당하는 빈집의 비율을 나타낸 시각화 자료로, 전국에서 대전 가장 높은 수치인 것을 알 수 있습니다. 이를 통해 해당 서비스를 진행할 때, 타 지역에 비해 시간적, 비용적 효율이 높다는 것을 보여줍니다. 또한 5%대로 꾸준하게 발생하고 있어, 해당 서비스를 제공하기 용이하다는 것을 알 수 있습니다.

### 대전광역시 직업 분야별 성장률 변화 추이

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/b97f27f9-658c-427b-9d2a-42f20b775cfa)

2022년 12월과 2023년 12월의 직업 분야별 사업체, 종사자, 매출액 성장의 총합을 나타낸 자료로, 다른 분야와는 달리 대전의 전문, 과학 및 기술 서비스업에 대한 성장이 특히 높으며 전반적으로 증가추세인 것을 알 수 있습니다, 이를 통해 근로자들의 꾸준한 유입을 위해서 주거문제가 해결되어야 한다는 점을 시사합니다.

### 대전 한달살이 서비스에 대한 설문조사 결과

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/114c9ce8-8e2c-493d-acc1-85c906696cf7)

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/79201ace-3fd4-4ba7-a1e5-efa796457b03)

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/33146d4e-a622-4b08-9da8-5288e2e6fc80)

## LLM을 활용한 집 추천 시스템

### 추천 시스템 구조

사용자에게 추천해줄 때 기본적으로 다음과 같은 정보를 입력받습니다.

- person_count : (1명, 2명, 3명, 4명 이상)
- period : (1주, 2주, 3주, 4주 이상)
- identity : (학생, 직장인, 기타)
- car : (자차, 대중교통)
- child : (아이 있음, 아이 없음)
- significant: (사용자가 직접 입력한 내용)

총 3단계로 이루어져 추천이 진행됩니다.

1. 데이터 필터링으로 데이터의 갯수를 줄입니다.
    - 아이가 있다. → walkTime 10분 이하
    - 차가 있다. → aptParkingCountPerHousehold > 0

2. 데이터 유사도 계산
    - TF-IDF를 활용한 코사인 유사도를 계산해 데이터의 정보와 사용자가 원하는 정보에 대한 데이터에 순위를 계산합니다.

3. LLM을 활용해 XAI(eXplainable AI) 추천
    - 유사도로 계산한 상위 데이터를 바탕으로 데이터의 추천 순위 및 그 이유를 생성합니다.

### 데이터 크롤링

우선 네이버 지도에서 대전 광역시의 주택 정보를 크롤링 해옵니다. [링크](https://github.com/SPARCS-Service-Hackathon-2024/A7-Data-Analysis/blob/main/crawling.ipynb)

```
{"aptName": "대전센트럴자이1단지", "tradeBuildingTypeCode": "APT", "aptHeatMethodTypeName": "개별난방", "aptHeatFuelTypeName": "도시가스", "aptParkingCountPerHousehold": "1.43", "aptHouseholdCount": "874", "exposureAddress": "대전시 중구 대흥동", "monthlyManagementCost": 180000, "articleFeatureDescription": "주방넓은구조로 이사협의 가능.", "detailDescription": "대흥초,대전중,대전고,대전여중,성모여고 최고의 학군이며\r\n도보로 중앙로역 5분거리입니다.\r\n또한 먹자골목 5분거리라 살기 너무 좋아요.\r\n대흥2구역재개발(kcc건설) 호재로 인해 투자가치 상당히 높습니다.\r\n자세한 상담은 자이 부동산(042-221-3003) 으로 언제든지 \r\n편하게 연락주세요!!", "floorLayerName": "단층", "principalUse": "공동주택", "tagList": ["15년이내", "방세개", "화장실두개", "세대당1대"], "schoolName": "대전대흥초등학교", "organizationType": "공립", "establishmentYmd": "19380702", "walkTime": 4, "studentCountPerTeacher": 16.7, "id": 2817, "url": "https://new.land.naver.com/complexes/103255?ms=36.322262,127.42776,17&a=APT:OBYG:PRE&e=RETAIL", "image_url": "https://landthumb-phinf.pstatic.net//20200525_259/apt_realimage_1590371141039Aun5e_JPEG/1865cbce9afe5320953dcbbfb29f0db0.JPG"}
```

약 2900개의 데이터를 수집했습니다.

### 데이터 전처리 및 라벨링

서비스에 필요한 모델의 입력과 출력은 다음과 같습니다.
- 입력: 사용자의 정보 + 후보 데이터셋 3개
- 출력: 후보 데이터셋 3개에 대한 순위 및 이유

사용에 필요한 퍼소나를 가상으로 생성하고 gemeni-pro로 예상되는 결과값을 라벨링합니다. [링크](https://github.com/SPARCS-Service-Hackathon-2024/A7-Data-Analysis/blob/main/labeling.ipynb)

후보 데이터셋 정보

```
{"aptName": "경남아너스빌1단지", "articleFeatureDescription": "올확장 풀옵션의 조용하고 조망좋은 최고급아파트", "tagList": ["25년이내", "1층", "대형평수", "방네개이상"], "walkTime": 7, "studentCountPerTeacher": 16.2, "aptParkingCountPerHousehold": "2.42"}
```
- aptName: 집 이름
- articleFeatureDescription: 기본적인 설명 + 관계자가 쓴 글 (100자 이내로 슬라이싱)
- tagList: 키워드 정보
- walkTime: 학교까지의 거리
- studentCountPerTeacher: 교사당 학생수
- aptParkingCountPerHousehold: 가구당 주자 자리 수

walkTime와 studentCountPerTeacher는 아이가 있는 가구에 중요한 정보, aptParkingCountPerHousehold는 차가 있는 가구에 중요한 정보입니다.

사용자가 입력한 특이 사항과 코사인 유사도를 계산할 때 articleFeatureDescription를 사용합니다.

### 모델 학습

라벨링한 데이터로 [beomi/open-llama-2-ko-7b](https://huggingface.co/beomi/llama-2-ko-7b) 모델을 활용해 파인튜닝을 해줍니다. 지원받은 [엘리스 클라우드](https://elice.io/ko/products/cloud/info)의 GPU VRAM은 40GB정도지만, 학습시킬 데이터의 길이가 길기 때문에 양자화를 진행하여 학습을 진행합니다. [자세히 보기](https://github.com/SPARCS-Service-Hackathon-2024/A7-Data-Analysis/blob/main/sarabwayu.ipynb)


학습이 완료된 adapter 모델은 [taewan2002/srabwayu-rec-7b](https://huggingface.co/taewan2002/srabwayu-rec-7b) peft모델로 다운 받아서 사용할 수 있습니다.

```
adapter_model = "taewan2002/srabwayu-rec-7b"
model = AutoPeftModelForCausalLM.from_pretrained(adapter_model, device_map="auto", torch_dtype="auto")
tokenizer = LlamaTokenizerFast.from_pretrained(adapter_model, trust_remote_code=True)
```

### 모델 활용

```
persona = {
            "person_count": "3명 이상",
            "period": "한달 이상",
            "identity": "직장인",
            "car": "차 없음",
            "child": "아이 없음",
            "significant": "주변에 공원이 있었으면 좋겠어"
        }
```

이렇게 입력시 다음과 같은 결과물을 추천해줍니다.
```
[
    [
      "효동현대",
      "소라",
      "e편한세상대전법동"
    ],
    [
      "효동현대는 남향으로 올리모델링이 완료되어 깨끗하고 쾌적한 주거 환경을 제공합니다. 또한, 주변에 공원이 있어 자연을 즐길 수 있으며, 주변에 초등학교와 중학교가 있어 자녀 교육에 편리합니다.",
      "소라는 남향으로 완전 리모델링이 완료되어 깨끗하고 편안한 주거 환경을 제공합니다. 또한, 초등학교와 오정공원이 가까워 아이들과 산책하기 좋습니다.",
      "e편한세상대전법동은 대단지 아파트로 주변 환경이 안정적이며, 주변에 중리시장이 있어 생활이 편리합니다. 또한, 전면이 탁트이고 아름다운 공원이 있어 자연을 즐길 수 있습니다."
    ]
  ]
```

### 활용 예시

![](https://github.com/SPARCS-Service-Hackathon-2024/A7-Backend/assets/89565530/526708d3-6743-4029-a58c-607869ed6145)