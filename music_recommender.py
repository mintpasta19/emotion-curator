import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import random

class MusicRecommender:
    def __init__(self):
        """Spotify API 초기화"""
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                raise ValueError("Spotify API 키가 설정되지 않았습니다.")
            
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            self.sp = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager
            )
            
            print("✓ Spotify API 연결 성공")
            
        except Exception as e:
            print(f"❌ Spotify API 연결 실패: {e}")
            self.sp = None
    
    
    # 감정별 검색 키워드
    EMOTION_KEYWORDS = {
        '기쁨': ['happy', 'joy', 'cheerful', 'upbeat', 'positive', 'celebration'],
        '슬픔': ['sad', 'melancholy', 'emotional', 'lonely', 'heartbreak', 'tears'],
        '불안': ['anxiety', 'stress', 'nervous', 'tension', 'worry', 'restless'],
        '분노': ['angry', 'rage', 'furious', 'intense', 'aggressive', 'power'],
        '상처': ['hurt', 'pain', 'healing', 'comfort', 'sorrow', 'broken'],
        '당황': ['confused', 'chaos', 'surprise', 'unexpected', 'shock', 'dizzy']
    }
    
    
    def get_top_tracks_for_emotion(self, emotion, limit=50):
        """
        특정 감정에 맞는 인기 TOP 50 트랙 가져오기
        
        Parameters:
        - emotion: 감정 ('기쁨', '슬픔', ...)
        - limit: 가져올 트랙 수 (기본 50)
        
        Returns:
        - list: 트랙 정보 리스트
        """
        if not self.sp:
            return []
        
        try:
            # 감정에 맞는 키워드 선택
            keywords = self.EMOTION_KEYWORDS.get(emotion, ['music'])
            selected_keyword = random.choice(keywords)
            
            print(f"\n🔍 '{emotion}' 감정 검색: 키워드 '{selected_keyword}'")
            
            # Spotify 검색
            results = self.sp.search(
                q=selected_keyword,
                type='track',
                limit=limit,
                market='KR'  # 한국 시장
            )
            
            tracks = []
            for item in results['tracks']['items']:
                track_info = {
                    'name': item['name'],
                    'artist': ', '.join([artist['name'] for artist in item['artists']]),
                    'url': item['external_urls']['spotify'],
                    'preview_url': item.get('preview_url'),
                    'popularity': item['popularity'],
                    'emotion': emotion,
                    'keyword': selected_keyword
                }
                tracks.append(track_info)
            
            # 인기도순 정렬
            tracks = sorted(tracks, key=lambda x: x['popularity'], reverse=True)
            
            print(f"✓ {len(tracks)}개 트랙 가져옴")
            
            return tracks
            
        except Exception as e:
            print(f"❌ '{emotion}' 트랙 검색 실패: {e}")
            return []
    
    
    def recommend_music_by_emotions(self, emotions_dict, total_tracks=10):
        """
        여러 감정 비율에 따라 음악 추천
        
        Parameters:
        - emotions_dict: {'기쁨': 45.2, '불안': 32.8, ...} 형태
        - total_tracks: 추천할 총 트랙 수
        
        Returns:
        - list: 추천 트랙 리스트
        """
        if not self.sp:
            print("❌ Spotify API 연결 안 됨")
            return []
        
        print(f"\n{'='*60}")
        print("🎵 감정 기반 음악 추천 시작")
        print(f"{'='*60}")
        
        # 감정 비율에 따라 트랙 수 계산
        sorted_emotions = sorted(
            emotions_dict.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        print("\n📊 감정 분포:")
        for emotion, score in sorted_emotions:
            print(f"  {emotion}: {score:.1f}%")
        
        # 각 감정별 추천 트랙 수 계산
        emotion_track_counts = {}
        remaining_tracks = total_tracks
        
        for emotion, score in sorted_emotions:
            if score < 5.0:  # 5% 미만은 제외
                continue
            
            # 비율에 따라 트랙 수 계산
            count = max(1, round(total_tracks * (score / 100)))
            count = min(count, remaining_tracks)  # 남은 트랙 수 초과 방지
            
            emotion_track_counts[emotion] = count
            remaining_tracks -= count
            
            if remaining_tracks <= 0:
                break
        
        # 남은 트랙은 최상위 감정에 할당
        if remaining_tracks > 0 and emotion_track_counts:
            top_emotion = sorted_emotions[0][0]
            emotion_track_counts[top_emotion] += remaining_tracks
        
        print("\n🎯 감정별 추천 트랙 수:")
        for emotion, count in emotion_track_counts.items():
            print(f"  {emotion}: {count}곡")
        
        # 각 감정별로 트랙 가져오기
        all_tracks = []
        
        for emotion, count in emotion_track_counts.items():
            print(f"\n🎼 '{emotion}' 감정 트랙 가져오는 중...")
            
            # TOP 50에서 가져오기
            top_tracks = self.get_top_tracks_for_emotion(emotion, limit=50)
            
            if top_tracks:
                # 무작위로 선택
                selected = random.sample(
                    top_tracks, 
                    min(count, len(top_tracks))
                )
                all_tracks.extend(selected)
                print(f"✓ {len(selected)}곡 선택됨")
            else:
                print(f"⚠️  '{emotion}' 트랙을 찾을 수 없음")
        
        # 무작위 섞기
        random.shuffle(all_tracks)
        
        print(f"\n{'='*60}")
        print(f"✨ 총 {len(all_tracks)}곡 추천 완료!")
        print(f"{'='*60}\n")
        
        return all_tracks[:total_tracks]
    
    
    def recommend_music(self, main_emotion, limit=10):
        """
        단일 감정 기반 추천 (기존 호환성)
        
        Parameters:
        - main_emotion: 주요 감정
        - limit: 추천 곡 수
        
        Returns:
        - list: 추천 트랙 리스트
        """
        if not self.sp:
            return []
        
        try:
            # TOP 50에서 무작위 선택
            top_tracks = self.get_top_tracks_for_emotion(main_emotion, limit=50)
            
            if top_tracks:
                selected = random.sample(top_tracks, min(limit, len(top_tracks)))
                return selected
            
            return []
            
        except Exception as e:
            print(f"❌ 음악 추천 실패: {e}")
            return []
    
    
    def get_track_details(self, track_id):
        """트랙 상세 정보 가져오기"""
        if not self.sp:
            return None
        
        try:
            track = self.sp.track(track_id)
            return {
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'url': track['external_urls']['spotify'],
                'preview_url': track.get('preview_url'),
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity']
            }
        except Exception as e:
            print(f"❌ 트랙 정보 가져오기 실패: {e}")
            return None

