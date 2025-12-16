import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class MusicRecommender:
    """
    감정 기반 음악 추천 (Spotify API)
    """
    def __init__(self):
        # .env에서 API 키 자동 로드
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("SPOTIFY_CLIENT_ID 또는 SPOTIFY_CLIENT_SECRET이 .env 파일에 없습니다!")
        
        # Spotify 클라이언트 초기화
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # 감정별 검색 키워드 (한국어 + 영어)
        self.emotion_keywords = {
            '분노': ['angry', 'rage', 'rock', 'metal', 'punk', 'intense', 'aggressive'],
            '슬픔': ['sad', 'melancholy', 'piano', 'acoustic', 'ballad', 'emotional', '슬픈'],
            '불안': ['anxious', 'ambient', 'chill', 'lo-fi', 'calm', 'relaxing', '불안'],
            '상처': ['hurt', 'pain', 'indie', 'folk', 'soul', 'emotional', '힐링'],
            '당황': ['confused', 'indie pop', 'alternative', 'quirky', 'upbeat', 'mixed'],
            '기쁨': ['happy', 'joy', 'upbeat', 'dance', 'pop', 'cheerful', '신나는']
        }
        
        # 감정별 Spotify 오디오 특성
        self.emotion_features = {
            '분노': {'min_energy': 0.7, 'max_valence': 0.4, 'min_tempo': 120},
            '슬픔': {'max_energy': 0.5, 'max_valence': 0.3, 'max_tempo': 100},
            '불안': {'min_energy': 0.3, 'max_energy': 0.6, 'min_acousticness': 0.4},
            '상처': {'max_energy': 0.6, 'max_valence': 0.4, 'min_acousticness': 0.3},
            '당황': {'min_energy': 0.5, 'min_valence': 0.4, 'max_valence': 0.7},
            '기쁨': {'min_energy': 0.6, 'min_valence': 0.6, 'min_tempo': 110}
        }
    
    def recommend_music(self, emotion, limit=10):
        """
        감정에 맞는 음악 추천
        
        Parameters:
        - emotion: 감정 이름
        - limit: 추천 곡 수
        
        Returns:
        - 추천 곡 리스트
        """
        print(f"\n🎵 음악 추천 중... (Spotify API)")
        print(f"   감정: {emotion}")
        
        keywords = self.emotion_keywords.get(emotion, self.emotion_keywords['기쁨'])
        
        tracks = []
        seen_ids = set()
        
        try:
            # 여러 키워드로 검색
            for keyword in keywords[:3]:  # 상위 3개 키워드만
                try:
                    results = self.sp.search(
                        q=keyword,
                        type='track',
                        limit=20,
                        market='KR'
                    )
                    
                    for item in results['tracks']['items']:
                        if item['id'] in seen_ids:
                            continue
                        
                        seen_ids.add(item['id'])
                        
                        track_info = {
                            'name': item['name'],
                            'artist': ', '.join([artist['name'] for artist in item['artists']]),
                            'album': item['album']['name'],
                            'url': item['external_urls']['spotify'],
                            'preview_url': item.get('preview_url'),
                            'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                            'duration_ms': item['duration_ms'],
                            'popularity': item['popularity']
                        }
                        
                        tracks.append(track_info)
                        
                        if len(tracks) >= limit * 2:
                            break
                
                except Exception as e:
                    print(f"   키워드 '{keyword}' 검색 실패: {e}")
                    continue
                
                if len(tracks) >= limit * 2:
                    break
            
            # 인기도 순으로 정렬 후 상위 곡 선택
            tracks.sort(key=lambda x: x['popularity'], reverse=True)
            final_tracks = tracks[:limit]
            
            print(f"✓ {len(final_tracks)}곡 추천 완료")
            
            return final_tracks
        
        except Exception as e:
            print(f"❌ 음악 추천 실패: {e}")
            return []


# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("Spotify 음악 추천 테스트")
    print("=" * 60)
    
    recommender = MusicRecommender()
    
    test_emotions = ['기쁨', '슬픔', '분노']
    
    for emotion in test_emotions:
        print(f"\n[{emotion}] 추천")
        tracks = recommender.recommend_music(emotion, limit=5)
        
        for i, track in enumerate(tracks, 1):
            print(f"{i}. {track['name']} - {track['artist']}")
            print(f"   인기도: {track['popularity']}, URL: {track['url']}")
        print()
