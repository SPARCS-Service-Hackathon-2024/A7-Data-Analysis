# Sarabwayu 주택 추천 시스템

카이스트에서 주최하는 Sparcs 2024 서비스 해커톤의 주제인 "지역 사회 문제 해결하기"에서 "청년 인구 감소"를 핵심 문제로 정의했습니다.

빈 집을 활용해서 이주의 진입장벽을 낮추기 위해 다음과 같은 기능을 핵심 기능으로 설정했습니다.

- 빈 집을 활용한 한 달 살이: 낮은 가격대로 그 지역에서의 생활을 체험해 볼 수 있습니다.
- 자유로운 연장: 한 달 살이를 진행하면서 자유롭게 거주를 연장하고, 최종적으로는 구매할 수 있습니다.
- AI 추천: 사용자의 기본 정보를 바탕으로 자신에게 맞는 집을 추천받을 수 있습니다.

기대 효과

- 기업과의 연계: 단기 인턴십과 연계해 지역에 편하게 머무를 수 있도록 도와줍니다.
- 조각 투자: 상태가 좋지 못한 빈집에 대한 조각 투자를 진행하여 리모델링 자금을 마련하고 수익을 분배할 수 있습니다.
- 청년 인구 증가: 단기적으로라도 청년 인구의 유입이 많아진다면, 편의시설이 많아지고 그에 대한 더 많은 청년 인구의 유입이 기대됩니다.


## 데이터 분석

### 대전 청년인구 감소 추이


### 연도별 빈집 개수 추이


### 대전광역시 집 현황


### 대전광역시 직업 분야별 변화 추이


### 한달 살이 검색량 추이


### 설문 조사

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

우선 네이버 지도에서 대전 광역시의 주택 정보를 크롤링 해옵니다. [코드](https://github.com/SPARCS-Service-Hackathon-2024/A7-Data-Analysis/blob/main/crawling.ipynb)

```
{"aptName": "대전센트럴자이1단지", "tradeBuildingTypeCode": "APT", "aptHeatMethodTypeName": "개별난방", "aptHeatFuelTypeName": "도시가스", "aptParkingCountPerHousehold": "1.43", "aptHouseholdCount": "874", "exposureAddress": "대전시 중구 대흥동", "monthlyManagementCost": 180000, "articleFeatureDescription": "주방넓은구조로 이사협의 가능.", "detailDescription": "대흥초,대전중,대전고,대전여중,성모여고 최고의 학군이며\r\n도보로 중앙로역 5분거리입니다.\r\n또한 먹자골목 5분거리라 살기 너무 좋아요.\r\n대흥2구역재개발(kcc건설) 호재로 인해 투자가치 상당히 높습니다.\r\n자세한 상담은 자이 부동산(042-221-3003) 으로 언제든지 \r\n편하게 연락주세요!!", "floorLayerName": "단층", "principalUse": "공동주택", "tagList": ["15년이내", "방세개", "화장실두개", "세대당1대"], "schoolName": "대전대흥초등학교", "organizationType": "공립", "establishmentYmd": "19380702", "walkTime": 4, "studentCountPerTeacher": 16.7, "id": 2817, "url": "https://new.land.naver.com/complexes/103255?ms=36.322262,127.42776,17&a=APT:OBYG:PRE&e=RETAIL", "image_url": "https://landthumb-phinf.pstatic.net//20200525_259/apt_realimage_1590371141039Aun5e_JPEG/1865cbce9afe5320953dcbbfb29f0db0.JPG"}
```

약 2900개의 데이터를 수집했습니다.

### 데이터 전처리 및 라벨링

서비스에 필요한 모델의 입력과 출력은 다음과 같습니다.
- 입력: 사용자의 정보 + 후보 데이터셋 3개
- 출력: 후보 데이터셋 3개에 대한 순위 및 이유

사용에 필요한 퍼소나를 가상으로 생성하고 gemeni-pro로 예상되는 결과값을 라벨링합니다. [코드](https://github.com/SPARCS-Service-Hackathon-2024/A7-Data-Analysis/blob/main/labeling.ipynb)

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

라벨링한 데이터로 [beomi/open-llama-2-ko-7b](https://huggingface.co/beomi/llama-2-ko-7b) 모델을 활용해 파인튜닝을 해줍니다. 클라우드의 GPU VRAM은 40GB정도지만, 학습시킬 데이터의 길이가 길기 때문에 양자화를 진행하여 학습을 진행합니다.

[학습 코드](https://github.com/SPARCS-Service-Hackathon-2024/A7-Data-Analysis/blob/main/sarabwayu.ipynb)


학습이 완료된 adapter 모델은 [taewan2002/srabwayu-rec-7b](https://huggingface.co/taewan2002/srabwayu-rec-7b) peft모델로 다운 받아서 사용할 수 있습니다.

```
adapter_model = "taewan2002/srabwayu-rec-7b"
model = AutoPeftModelForCausalLM.from_pretrained(adapter_model, device_map="auto", torch_dtype="auto")
tokenizer = LlamaTokenizerFast.from_pretrained(adapter_model, trust_remote_code=True)
```

### 모델 활용

(시연 사진)