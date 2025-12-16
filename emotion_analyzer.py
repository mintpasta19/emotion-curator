import torch
from transformers import BertForSequenceClassification, AutoTokenizer
import numpy as np
import re

# 감정 레이블
EMOTION_LABELS = ['분노', '슬픔', '불안', '상처', '당황', '기쁨']

def split_sentences(text):
    """
    텍스트를 문장 단위로 분리 (개선된 버전)
    """
    # 한국어 문장 구분자
    text = text.strip()
    
    # 문장 종결 부호로 분리
    sentences = re.split(r'([.!?]+[\s]*)', text)
    
    # 분리된 구분자와 문장 재결합
    result = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = (sentences[i] + sentences[i + 1]).strip()
        if sentence:
            result.append(sentence)
    
    # 마지막 문장 (구분자 없을 수 있음)
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        result.append(sentences[-1].strip())
    
    # 문장이 없으면 원본 텍스트 반환
    if not result:
        result = [text]
    
    return result


def analyze_emotion_with_model(text, model_path='emotion_model_best.pth'):
    """
    개선된 감정 분석 (문장 단위 분석 + 가중 평균)
    
    Parameters:
    - text: 분석할 텍스트
    - model_path: 모델 파일 경로
    
    Returns:
    - dict: {'분노': 10.5, '슬픔': 20.3, ...}
    """
    print(f"\n{'='*60}")
    print("감정 분석 시작")
    print(f"{'='*60}")
    
    # 디바이스 설정
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"디바이스: {device}")
    
    # 모델 로드
    model = BertForSequenceClassification.from_pretrained(
        'monologg/kobert',
        num_labels=6,
        trust_remote_code=True
    )
    
    # 학습된 가중치 로드
    try:
        checkpoint = torch.load(model_path, map_location=device)
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        print(f"✓ 모델 로드 완료: {model_path}")
    except Exception as e:
        print(f"⚠️  모델 로드 실패: {e}")
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    model.to(device)
    model.eval()
    
    # 토크나이저
    tokenizer = AutoTokenizer.from_pretrained('monologg/kobert', trust_remote_code=True)
    
    # 텍스트를 문장으로 분리
    sentences = split_sentences(text)
    print(f"\n📝 분석할 문장 개수: {len(sentences)}")
    
    # 문장별 감정 분석
    sentence_emotions = []
    
    for i, sentence in enumerate(sentences, 1):
        if not sentence.strip():
            continue
        
        print(f"\n[문장 {i}] {sentence[:50]}{'...' if len(sentence) > 50 else ''}")
        
        # 토큰화
        inputs = tokenizer(
            sentence,
            return_tensors='pt',
            max_length=128,
            padding='max_length',
            truncation=True
        )
        inputs = {key: val.to(device) for key, val in inputs.items()}
        
        # 예측
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            
            # Softmax로 확률 변환
            probs = torch.softmax(logits, dim=1)[0]
            probs = probs.cpu().numpy()
        
        # 문장별 감정 저장
        sentence_emotion = {
            label: float(prob * 100) 
            for label, prob in zip(EMOTION_LABELS, probs)
        }
        
        sentence_emotions.append(sentence_emotion)
        
        # 문장별 결과 출력
        sorted_emotions = sorted(
            sentence_emotion.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        print(f"   주요 감정: {sorted_emotions[0][0]} ({sorted_emotions[0][1]:.1f}%)")
    
    # 전체 감정 통합 (가중 평균)
    if len(sentence_emotions) == 1:
        # 문장이 1개면 그대로 사용
        final_emotions = sentence_emotions[0]
    else:
        # 여러 문장의 감정을 평균
        final_emotions = {label: 0.0 for label in EMOTION_LABELS}
        
        for sent_emotion in sentence_emotions:
            for label in EMOTION_LABELS:
                final_emotions[label] += sent_emotion[label]
        
        # 평균 계산
        num_sentences = len(sentence_emotions)
        for label in EMOTION_LABELS:
            final_emotions[label] /= num_sentences
    
    # 정규화 (합이 100%가 되도록)
    total = sum(final_emotions.values())
    if total > 0:
        final_emotions = {
            label: (score / total) * 100 
            for label, score in final_emotions.items()
        }
    
    # 최종 결과 출력
    print(f"\n{'='*60}")
    print("최종 감정 분석 결과")
    print(f"{'='*60}")
    
    sorted_final = sorted(
        final_emotions.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for emotion, score in sorted_final:
        bar = "█" * int(score / 5)
        print(f"{emotion:6s}: {score:5.1f}% {bar}")
    
    return final_emotions


def analyze_emotion_advanced(text, model_path='emotion_model_best.pth', 
                             method='sentence_avg'):
    """
    고급 감정 분석 (여러 방법 선택 가능)
    
    Parameters:
    - text: 분석할 텍스트
    - model_path: 모델 파일 경로
    - method: 'sentence_avg', 'weighted', 'max_pool', 'whole'
    
    Returns:
    - dict: {'분노': 10.5, '슬픔': 20.3, ...}
    """
    print(f"\n🔍 분석 방법: {method}")
    
    # 디바이스 설정
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 모델 로드
    model = BertForSequenceClassification.from_pretrained(
        'monologg/kobert',
        num_labels=6
    )
    
    try:
        checkpoint = torch.load(model_path, map_location=device)
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
    except Exception as e:
        print(f"⚠️  모델 로드 실패: {e}")
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    model.to(device)
    model.eval()
    
    tokenizer = AutoTokenizer.from_pretrained('monologg/kobert')
    
    # 문장 분리
    sentences = split_sentences(text)
    print(f"📝 문장 개수: {len(sentences)}")
    
    # 방법 1: 전체 텍스트 한 번에 분석 (기존 방식)
    if method == 'whole':
        inputs = tokenizer(
            text,
            return_tensors='pt',
            max_length=128,
            padding='max_length',
            truncation=True
        )
        inputs = {key: val.to(device) for key, val in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)[0]
            probs = probs.cpu().numpy()
        
        return {label: float(prob * 100) for label, prob in zip(EMOTION_LABELS, probs)}
    
    # 방법 2~4: 문장별 분석
    sentence_emotions = []
    sentence_lengths = []
    
    for sentence in sentences:
        if not sentence.strip():
            continue
        
        inputs = tokenizer(
            sentence,
            return_tensors='pt',
            max_length=128,
            padding='max_length',
            truncation=True
        )
        inputs = {key: val.to(device) for key, val in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)[0]
            probs = probs.cpu().numpy()
        
        sentence_emotion = {
            label: float(prob * 100) 
            for label, prob in zip(EMOTION_LABELS, probs)
        }
        
        sentence_emotions.append(sentence_emotion)
        sentence_lengths.append(len(sentence))
    
    if not sentence_emotions:
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    # 방법 2: 단순 평균
    if method == 'sentence_avg':
        final_emotions = {label: 0.0 for label in EMOTION_LABELS}
        
        for sent_emotion in sentence_emotions:
            for label in EMOTION_LABELS:
                final_emotions[label] += sent_emotion[label]
        
        for label in EMOTION_LABELS:
            final_emotions[label] /= len(sentence_emotions)
    
    # 방법 3: 문장 길이 가중 평균 (긴 문장이 더 중요)
    elif method == 'weighted':
        final_emotions = {label: 0.0 for label in EMOTION_LABELS}
        total_length = sum(sentence_lengths)
        
        for sent_emotion, length in zip(sentence_emotions, sentence_lengths):
            weight = length / total_length
            for label in EMOTION_LABELS:
                final_emotions[label] += sent_emotion[label] * weight
    
    # 방법 4: Max Pooling (각 감정의 최댓값)
    elif method == 'max_pool':
        final_emotions = {label: 0.0 for label in EMOTION_LABELS}
        
        for label in EMOTION_LABELS:
            max_score = max(sent_emotion[label] for sent_emotion in sentence_emotions)
            final_emotions[label] = max_score
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # 정규화
    total = sum(final_emotions.values())
    if total > 0:
        final_emotions = {
            label: (score / total) * 100 
            for label, score in final_emotions.items()
        }
    
    # 결과 출력
    print(f"\n최종 감정 분석 결과 ({method}):")
    for emotion, score in sorted(final_emotions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {emotion}: {score:.1f}%")
    
    return final_emotions

