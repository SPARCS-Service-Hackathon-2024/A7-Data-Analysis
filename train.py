import torch
from transformers import (
    AutoModelForCausalLM,
    LlamaTokenizerFast,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig,
)
from peft import (
    LoraConfig,
    get_peft_model,
)

base_model = "beomi/open-llama-2-ko-7b"

# QLoRA 모델을 사용하기 위한 설정
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16 
)
'''
torch.bfloat16은

16비트 브레인 플로팅 포인트(brain floating point)를 나타내며, 이는 텐서플로우에서도 널리 사용되는 형식입니다. 
bfloat16은 16비트 부동 소수점 형식이지만, float32와 유사한 정밀도를 제공하여 모델의 성능 저하를 최소화하면서도 메모리 사용량을 줄일 수 있습니다.
'''


model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config,
    device_map="auto",
)
model.config.use_cache = False
model.config.pretraining_tp = 1

# 토크나이저 로드
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false" # 토크나이저 병렬처리 방지(오류 방지)
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = 'true' # __cell__ 오류 방지

tokenizer = LlamaTokenizerFast.from_pretrained(
    base_model,
    trust_remote_code=True
)
tokenizer.pad_token = tokenizer.eos_token # 패딩 토큰을 문장의 끝으로 설정 </s>
tokenizer.padding_side = "right" # 패딩을 문장 뒤에 추가

# 학습 양식
import json
from datasets import load_dataset
file_name = 'recommendations.jsonl'


instruction = '''
사용자의 정보를 보고 집을 추천해줄 거야. 각 후보에 대해 순위를 지정하고, 추천 이유를 설명할 거야. must return json format
'''

# 데이터셋 로드
data = load_dataset('json', data_files=file_name, split="train")

# 데이터 매핑 함수 정의
def map_data_to_format(example):

    # 데이터 길이 제한..
    for candidate in example['candidate']:
        if len(candidate['articleFeatureDescription']) > 100:
            candidate['articleFeatureDescription'] = candidate['articleFeatureDescription'][:100] + '...'
    
    user_info_str = json.dumps(example['user_info'], ensure_ascii=False)
    candidates_str = json.dumps(example['candidate'], ensure_ascii=False)
    rank_str = json.dumps(example['rank'], ensure_ascii=False)
    reason_str = json.dumps(example['reason'], ensure_ascii=False)
    
    text = (
        f"###instruction:\n{instruction}\n\n"
        f"user_info:\n{user_info_str}\n\n"
        f"candidates:\n{candidates_str}\n\n"
        f"###rank:\n{rank_str}\n\n"
        f"reason:\n{reason_str}\n\n"
    )
    
    # completion은 모델이 생성해야 할 예상 출력을 포함합니다.
    # 여기서는 순위와 추천 이유를 JSON 형식으로 포함시킵니다.
    completion = f"{{\"rank\": {rank_str}, \"reason\": {reason_str}}}"
    
    return {'text': text, 'completion': completion}

# 데이터 매핑 적용
mapped_data = data.map(map_data_to_format)

# 데이터셋 분할
split_data = mapped_data.train_test_split(test_size=0.1)  # 10%를 테스트셋으로 사용

train_set = split_data['train']
eval_set = split_data['test']

train_set = train_set.map(lambda samples: tokenizer(samples["text"], padding=True, truncation=True, return_tensors="pt"), batched=True)
eval_set = eval_set.map(lambda samples: tokenizer(samples["text"], padding=True, truncation=True, return_tensors="pt"), batched=True)

# lora 파라미터 설정
peft_params = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, peft_params)

# prameter
epochs = 10

batch_size = 2

lr = 2e-4

training_params = TrainingArguments(
    output_dir="models",
    num_train_epochs=epochs,
    per_device_train_batch_size=batch_size,
    gradient_accumulation_steps=16,
    optim="adamw_torch",
    save_strategy="epoch",
    evaluation_strategy="steps",
    logging_strategy="steps",
    eval_steps=20,
    logging_steps=20,
    learning_rate=lr,
    weight_decay=0.001,
    fp16=False,
    bf16=False,
    max_grad_norm=0.3,
    max_steps=-1,
    warmup_ratio=0.03,
    group_by_length=True,
    lr_scheduler_type="cosine",
    report_to="wandb",
    dataloader_num_workers=1,
)

import transformers
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

trainer = Trainer(
    model=model,
    args=training_params,
    train_dataset=train_set,
    eval_dataset=eval_set,
    tokenizer=tokenizer,
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

trainer.train()