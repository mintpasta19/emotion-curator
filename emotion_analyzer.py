import torch
import torch.nn as nn
from kobert_transformers import get_kobert_model, get_tokenizer

# 6가지 감정 (중립 제거)
EMOTIONS = ['분노', '슬픔', '불안', '상처', '당황', '기쁨']

class EmotionClassifier(nn.Module):
    """
    KoBERT 기반 감정 분류 모델 (6가지 감정)
    
    구조:
    1. KoBERT: 한국어 텍스트를 숫자 벡터로 변환
    2. Dropout: 과적합 방지
    3. Classifier: 6가지 감정 중 하나로 분류
    """
    def __init__(self, num_classes=6):
        super(EmotionClassifier, self).__init__()
        
        # KoBERT 모델 로드
        self.bert = get_kobert_model()
        
        # Dropout (과적합 방지)
        self.dropout = nn.Dropout(0.5)
        
        # 분류기: 768차원 → 6개 감정
        self.classifier = nn.Linear(768, num_classes)
    
    def forward(self, input_ids, attention_mask):
        """
        순전파: 입력 텍스트 → 감정 예측
        """
        # BERT 통과
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        
        # [CLS] 토큰의 출력 사용
        pooled_output = outputs[1]
        
        # Dropout 적용
        pooled_output = self.dropout(pooled_output)
        
        # 최종 분류 (6개 감정 점수)
        logits = self.classifier(pooled_output)
        
        return logits


def analyze_emotion_with_model(text, model_path='emotion_model_best.pth'):
    """
    학습된 모델로 텍스트의 감정을 분석
    
    Parameters:
    - text: 분석할 한국어 텍스트
    - model_path: 학습된 모델 파일 경로
    
    Returns:
    - emotion_percentages: 각 감정의 비율 (딕셔너리)
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 모델 로드
    model = EmotionClassifier(num_classes=6)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    
    # 토크나이저
    tokenizer = get_tokenizer()
    
    # 텍스트를 BERT 입력 형태로 변환
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    
    # 예측
    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
    
    # 결과를 딕셔너리로 변환
    emotion_percentages = {
        EMOTIONS[i]: round(probabilities[i].item() * 100, 2)
        for i in range(6)
    }
    
    return emotion_percentages


if __name__ == "__main__":
    print("=" * 60)
    print("감정 분석 모델 구조 확인 (6가지 감정)")
    print("=" * 60)
    
    # 모델 생성
    model = EmotionClassifier(num_classes=6)
    
    # 모델 파라미터 수
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"\n✓ 모델 생성 완료")
    print(f"✓ 전체 파라미터: {total_params:,}개")
    print(f"✓ 학습 가능 파라미터: {trainable_params:,}개")
    print(f"✓ 감정 카테고리: {EMOTIONS}")
    print("\n모델 준비 완료!")
