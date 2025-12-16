import os
import json
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split

# 간단 명확한 매핑 (E10~E69를 10단위로)
# 분노: E10~E19 → 0
# 슬픔: E20~E29 → 1
# 불안: E30~E39 → 2
# 상처: E40~E49 → 3
# 당황: E50~E59 → 4
# 기쁨: E60~E69 → 5

EMOTIONS = ['분노', '슬픔', '불안', '상처', '당황', '기쁨']

def get_emotion_from_code(emotion_code):
    """
    감정 코드를 6가지 감정으로 매핑
    E10~E19 → 0 (분노)
    E20~E29 → 1 (슬픔)
    E30~E39 → 2 (불안)
    E40~E49 → 3 (상처)
    E50~E59 → 4 (당황)
    E60~E69 → 5 (기쁨)
    """
    try:
        # E10 → 10, E25 → 25
        code_num = int(emotion_code[1:])
        
        if 10 <= code_num <= 19:
            return 0  # 분노
        elif 20 <= code_num <= 29:
            return 1  # 슬픔
        elif 30 <= code_num <= 39:
            return 2  # 불안
        elif 40 <= code_num <= 49:
            return 3  # 상처
        elif 50 <= code_num <= 59:
            return 4  # 당황
        elif 60 <= code_num <= 69:
            return 5  # 기쁨
    except:
        pass
    
    return None

def extract_text_emotion(item):
    """JSON에서 텍스트와 감정 추출"""
    try:
        emotion_code = item['profile']['emotion']['type']
        emotion = get_emotion_from_code(emotion_code)
        
        if emotion is None:
            return None, None
        
        talk = item.get('talk', {})
        content = talk.get('content', {})
        
        # Human Speech (HS01, HS02, ...) 추출
        text_parts = []
        for key in sorted(content.keys()):
            if key.startswith('HS'):
                text = content[key]
                if text and len(str(text).strip()) > 3:
                    text_parts.append(str(text).strip())
        
        if text_parts:
            full_text = ' '.join(text_parts)
            return full_text, emotion
    
    except:
        pass
    
    return None, None

def process_directory(directory):
    """디렉토리의 모든 JSON 파일 처리"""
    data_list = []
    
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    print(f"  JSON 파일: {len(json_files)}개")
    
    for json_file in tqdm(json_files, desc="  처리 중"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    text, emotion = extract_text_emotion(item)
                    if text and emotion is not None:
                        data_list.append({
                            'text': text,
                            'emotion': emotion
                        })
        except:
            pass
    
    return data_list

def main():
    """전체 전처리 프로세스"""
    print("=" * 60)
    print("AI Hub 감성 대화 데이터 전처리")
    print("6가지 감정 (분노, 슬픔, 불안, 상처, 당황, 기쁨)")
    print("=" * 60)
    
    # Training 데이터
    print("\n[1/2] Training 데이터 처리")
    train_dir = 'data/raw/Training'
    train_data = process_directory(train_dir)
    print(f"  ✓ 추출: {len(train_data)}개")
    
    # Validation 데이터
    print("\n[2/2] Validation 데이터 처리")
    val_dir = 'data/raw/Validation'
    val_data = process_directory(val_dir)
    print(f"  ✓ 추출: {len(val_data)}개")
    
    # DataFrame 생성
    train_df = pd.DataFrame(train_data)
    val_df = pd.DataFrame(val_data)
    
    # 중복 제거
    train_df = train_df.drop_duplicates(subset=['text'])
    val_df = val_df.drop_duplicates(subset=['text'])
    
    print(f"\n중복 제거 후:")
    print(f"  Training: {len(train_df):,}개")
    print(f"  Validation: {len(val_df):,}개")
    
    # 감정 분포
    print("\n📊 Training 데이터 감정 분포:")
    for i, emotion in enumerate(EMOTIONS):
        count = len(train_df[train_df['emotion'] == i])
        percentage = (count / len(train_df) * 100) if len(train_df) > 0 else 0
        print(f"   {emotion:6s} (E{(i+1)*10}~E{(i+1)*10+9}): {count:7,}개 ({percentage:5.1f}%)")
    
    # 샘플 확인
    print("\n📝 데이터 샘플 확인 (각 감정별 2개씩):")
    for i, emotion in enumerate(EMOTIONS):
        emotion_df = train_df[train_df['emotion'] == i]
        if len(emotion_df) > 0:
            print(f"\n{'='*60}")
            print(f"[{emotion}] E{(i+1)*10}~E{(i+1)*10+9} 범위 - 총 {len(emotion_df):,}개")
            print('='*60)
            samples = emotion_df.sample(min(2, len(emotion_df)))
            for idx, (_, row) in enumerate(samples.iterrows(), 1):
                print(f"{idx}. {row['text'][:80]}...")
    
    # Test 세트 분리
    val_df, test_df = train_test_split(
        val_df, 
        test_size=0.5, 
        random_state=42,
        stratify=val_df['emotion']
    )
    
    print(f"\n{'='*60}")
    print(f"✓ 최종 데이터 크기:")
    print(f"   학습:   {len(train_df):7,}개")
    print(f"   검증:   {len(val_df):7,}개")
    print(f"   테스트: {len(test_df):7,}개")
    print(f"   총합:   {len(train_df) + len(val_df) + len(test_df):7,}개")
    
    # 저장
    os.makedirs('data', exist_ok=True)
    train_df.to_csv('data/train.csv', index=False, encoding='utf-8-sig')
    val_df.to_csv('data/val.csv', index=False, encoding='utf-8-sig')
    test_df.to_csv('data/test.csv', index=False, encoding='utf-8-sig')
    
    print("\n✓ 저장 완료:")
    print("   - data/train.csv")
    print("   - data/val.csv")
    print("   - data/test.csv")
    
    print("\n" + "=" * 60)
    print("✅ 전처리 완료!")
    print("위 샘플을 확인하고 다음 단계로 진행하세요.")
    print("=" * 60)

if __name__ == "__main__":
    main()
