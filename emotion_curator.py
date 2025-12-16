from emotion_analyzer import analyze_emotion_with_model
from image_generator import ImageGenerator
from music_recommender import MusicRecommender

class EmotionCurator:
    def __init__(self, model_path='emotion_model_best.pth'):
        print("=" * 60)
        print("🎨 Emotion Curator 초기화 중...")
        print("=" * 60)
        
        self.model_path = model_path
        self.image_generator = ImageGenerator()
        
        try:
            self.music_recommender = MusicRecommender()
            print("✓ 음악 추천기 준비 완료")
        except Exception as e:
            print(f"⚠️  음악 추천기 초기화 실패: {e}")
            self.music_recommender = None
        
        print("✓ 감정 분석 모델 준비 완료")
        print("✓ 그라데이션 이미지 생성기 준비 완료")
        print()
    
    def curate(self, text, generate_image=True, recommend_music=True, num_tracks=5):
        print("=" * 60)
        print("🎭 감정 큐레이션 시작")
        print("=" * 60)
        
        # 1. 감정 분석
        print(f"\n📝 입력: {text}")
        print("\n🔍 감정 분석 중...")
        
        emotions = analyze_emotion_with_model(text, self.model_path)
        
        # 주요 감정
        main_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name = main_emotion[0]
        emotion_score = main_emotion[1]
        
        print(f"\n✨ 주요 감정: {emotion_name} ({emotion_score:.1f}%)")
        print("\n📊 감정 분포:")
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        for emotion, score in sorted_emotions:
            bar = "█" * int(score / 5)
            print(f"  {emotion:6s}: {score:5.1f}% {bar}")
        
        result = {
            'text': text,
            'main_emotion': emotion_name,
            'emotion_score': emotion_score,
            'all_emotions': emotions,
            'image_path': None,
            'music': []
        }
        
        # 2. 그라데이션 이미지 생성
        if generate_image:
            try:
                image_path = f'emotion_gradient.png'
                image = self.image_generator.generate_image(
                    emotions,
                    save_path=image_path
                )
                result['image_path'] = image_path
            except Exception as e:
                print(f"❌ 이미지 생성 중 오류: {e}")
        
        # 3. 음악 추천
        if recommend_music and self.music_recommender:
            try:
                tracks = self.music_recommender.recommend_music(
                    emotion_name,
                    limit=num_tracks
                )
                result['music'] = tracks
                
                if tracks:
                    print(f"\n🎵 추천 음악 TOP {len(tracks)}:")
                    for i, track in enumerate(tracks, 1):
                        print(f"{i}. {track['name']} - {track['artist']}")
            except Exception as e:
                print(f"❌ 음악 추천 중 오류: {e}")
        
        print("\n" + "=" * 60)
        print("✅ 큐레이션 완료!")
        print("=" * 60)
        
        return result


if __name__ == "__main__":
    curator = EmotionCurator()
    
    test_texts = [
        "오늘 정말 기분이 좋아요! 모든 일이 잘 풀렸어요.",
        "너무 슬프고 우울해요. 아무것도 하기 싫어요.",
        "시험이 다가와서 너무 불안하고 걱정돼요."
    ]
    
    for text in test_texts:
        result = curator.curate(text, generate_image=True, recommend_music=True)
        print("\n" + "="*60 + "\n")
        input("계속하려면 Enter...")
