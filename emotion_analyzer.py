import torch
from transformers import BertForSequenceClassification, AutoTokenizer
import numpy as np
import re

# 감정 레이블
EMOTION_LABELS = ['분노', '슬픔', '불안', '상처', '당황', '기쁨']

def split_sentences(text):
    """
    텍스트를 문장 단위로 분리 (개선된 한국어 분리)
    """
    text = text.strip()
    
    # 문장 종결 부호로 분리
    sentences = re.split(r'([.!?]+[\s]*)', text)
    
    # 분리된 구분자와 문장 재결합
    result = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = (sentences[i] + sentences[i + 1]).strip()
        if sentence and len(sentence) > 2:  # 너무 짧은 문장 제외
            result.append(sentence)
    
    # 마지막 문장 (구분자 없을 수 있음)
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        if len(sentences[-1].strip()) > 2:
            result.append(sentences[-1].strip())
    
    # 문장이 없으면 원본 텍스트 반환
    if not result:
        result = [text]
    
    return result


def analyze_emotion_with_model(text, model_path='emotion_model_best.pth'):
    """
    감정 분석 (Weighted 방식 - 문장 길이 가중 평균)
    
    Parameters:
    - text: 분석할 텍스트
    - model_path: 학습된 모델 경로
    
    Returns:
    - dict: {'분노': 10.5, '슬픔': 20.3, ...}
    """
    print(f"\n{'='*60}")
    print("🔍 감정 분석 시작 (Weighted 방식)")
    print(f"{'='*60}")
    
    # 디바이스 설정
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"📱 디바이스: {device}")
    
    # KoBERT 모델 로드
    try:
        print("📦 KoBERT 모델 로드 중...")
        model = BertForSequenceClassification.from_pretrained(
            'monologg/kobert',
            num_labels=6,
            trust_remote_code=True  # ✅ 필수!
        )
        print("✓ 기본 모델 로드 완료")
        
        # 학습된 가중치 로드
        try:
            checkpoint = torch.load(model_path, map_location=device, weights_only=False)
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)
            print(f"✓ 학습된 가중치 로드 완료: {model_path}")
        except FileNotFoundError:
            print(f"⚠️  학습된 가중치 파일 없음: {model_path}")
            print("⚠️  기본 KoBERT 모델로 분석합니다 (정확도 낮을 수 있음)")
        except Exception as e:
            print(f"⚠️  가중치 로드 실패: {e}")
            print("⚠️  기본 KoBERT 모델로 분석합니다")
        
        model.to(device)
        model.eval()
        
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        # 오류 시 균등 분포 반환
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    # 토크나이저 로드
    try:
        print("📝 토크나이저 로드 중...")
        tokenizer = AutoTokenizer.from_pretrained(
            'monologg/kobert',
            trust_remote_code=True  # ✅ 필수!
        )
        print("✓ 토크나이저 로드 완료")
    except Exception as e:
        print(f"❌ 토크나이저 로드 실패: {e}")
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    # 텍스트를 문장으로 분리
    sentences = split_sentences(text)
    print(f"\n📝 분석할 문장 개수: {len(sentences)}")
    
    # 문장별 감정 분석
    sentence_emotions = []
    sentence_lengths = []
    
    for i, sentence in enumerate(sentences, 1):
        if not sentence.strip():
            continue
        
        print(f"\n[문장 {i}/{len(sentences)}] {sentence[:50]}{'...' if len(sentence) > 50 else ''}")
        
        # 토큰화
        try:
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
                probs = torch.softmax(logits, dim=1)[0]
                probs = probs.cpu().numpy()
            
            # 문장별 감정 저장
            sentence_emotion = {
                label: float(prob * 100) 
                for label, prob in zip(EMOTION_LABELS, probs)
            }
            
            sentence_emotions.append(sentence_emotion)
            sentence_lengths.append(len(sentence))
            
            # 문장별 결과 출력
            sorted_emotions = sorted(
                sentence_emotion.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            print(f"   주요 감정: {sorted_emotions[0][0]} ({sorted_emotions[0][1]:.1f}%)")
            print(f"   문장 길이: {len(sentence)}자 (가중치: {len(sentence)/sum([len(s) for s in sentences]):.2%})")
            
        except Exception as e:
            print(f"   ⚠️ 문장 분석 실패: {e}")
            continue
    
    # 분석 실패 시
    if not sentence_emotions:
        print("\n❌ 모든 문장 분석 실패")
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    # ✅ Weighted 방식: 문장 길이 기반 가중 평균
    print(f"\n{'='*60}")
    print("⚖️  가중 평균 계산 중...")
    print(f"{'='*60}")
    
    final_emotions = {label: 0.0 for label in EMOTION_LABELS}
    total_length = sum(sentence_lengths)
    
    for i, (sent_emotion, length) in enumerate(zip(sentence_emotions, sentence_lengths), 1):
        weight = length / total_length
        print(f"문장 {i}: 길이 {length}자 → 가중치 {weight:.2%}")
        
        for label in EMOTION_LABELS:
            final_emotions[label] += sent_emotion[label] * weight
    
    # 정규화 (합이 100%가 되도록)
    total = sum(final_emotions.values())
    if total > 0:
        final_emotions = {
            label: (score / total) * 100 
            for label, score in final_emotions.items()
        }
    
    # 최종 결과 출력
    print(f"\n{'='*60}")
    print("✨ 최종 감정 분석 결과 (Weighted)")
    print(f"{'='*60}")
    
    sorted_final = sorted(
        final_emotions.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for i, (emotion, score) in enumerate(sorted_final, 1):
        bar = "█" * int(score / 3)
        print(f"{i}. {emotion:6s}: {score:5.1f}% {bar}")
    
    print(f"{'='*60}\n")
    
    return final_emotions


def analyze_emotion_simple(text, model_path='emotion_model_best.pth'):
    """
    간단한 감정 분석 (전체 텍스트 한 번에)
    Weighted 방식보다 빠르지만 정확도는 낮음
    
    Parameters:
    - text: 분석할 텍스트
    - model_path: 학습된 모델 경로
    
    Returns:
    - dict: {'분노': 10.5, '슬픔': 20.3, ...}
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 모델 로드
    try:
        model = BertForSequenceClassification.from_pretrained(
            'monologg/kobert',
            num_labels=6,
            trust_remote_code=True
        )
        
        # 학습된 가중치 로드
        try:
            checkpoint = torch.load(model_path, map_location=device, weights_only=False)
            model.load_state_dict(checkpoint.get('model_state_dict', checkpoint))
        except:
            pass
        
        model.to(device)
        model.eval()
        
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    # 토크나이저
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            'monologg/kobert',
            trust_remote_code=True
        )
    except Exception as e:
        print(f"❌ 토크나이저 로드 실패: {e}")
        return {label: 100.0/6 for label in EMOTION_LABELS}
    
    # 토큰화 및 예측
    try:
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
        
        emotions = {
            label: float(prob * 100) 
            for label, prob in zip(EMOTION_LABELS, probs)
        }
        
        return emotions
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return {label: 100.0/6 for label in EMOTION_LABELS}