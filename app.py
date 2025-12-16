import streamlit as st
from emotion_analyzer import analyze_emotion_with_model
from image_generator import ImageGenerator
from music_recommender import MusicRecommender
import os

st.set_page_config(
    page_title="Emotion Curator",
    page_icon="🎭",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.main {padding: 2rem;}
.stButton button {
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    color: white;
    font-size: 20px;
    padding: 0.5rem 2rem;
    border-radius: 10px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.title("🎭 Emotion Curator")
st.markdown("### 감정을 색으로 표현합니다")

if 'result' not in st.session_state:
    st.session_state.result = None

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    generate_image = st.checkbox("이미지 생성", value=True)
    recommend_music = st.checkbox("음악 추천", value=True)
    num_tracks = st.slider("추천 곡 수", 3, 10, 5)
    
    st.markdown("---")
    st.markdown("### 🎨 감정 색상")
    colors = {
        '분노': '#DC143C',
        '슬픔': '#4682B4',
        '불안': '#8A2BE2',
        '상처': '#BA55D3',
        '당황': '#FFA500',
        '기쁨': '#FFD700'
    }
    for emotion, color in colors.items():
        st.markdown(f"<div style='background:{color}; padding:5px; margin:2px; border-radius:5px; color:white;'>{emotion}</div>", 
                   unsafe_allow_html=True)

# 메인
col1, col2 = st.columns([1, 1])

with col1:
    st.header("✍️ 감정 입력")
    user_text = st.text_area(
        "지금 느끼는 감정을 자유롭게 작성해주세요:",
        height=200,
        placeholder="예: 오늘 정말 기분이 좋아요!"
    )
    
    if st.button("🔍 감정 분석 시작", use_container_width=True):
        if user_text.strip():
            with st.spinner("감정을 분석하고 아트를 생성하는 중..."):
                try:
                    image_gen = ImageGenerator()
                    music_rec = MusicRecommender() if recommend_music else None
                    
                    emotions = analyze_emotion_with_model(user_text)
                    main_emotion = max(emotions.items(), key=lambda x: x[1])
                    
                    result = {
                        'text': user_text,
                        'main_emotion': main_emotion[0],
                        'emotion_score': main_emotion[1],
                        'all_emotions': emotions,
                        'image_path': None,
                        'music': []
                    }
                    
                    if generate_image:
                        image_path = 'emotion_gradient.png'
                        image_gen.generate_image(emotions, save_path=image_path)
                        result['image_path'] = image_path
                    
                    if recommend_music and music_rec:
                        tracks = music_rec.recommend_music(main_emotion[0], limit=num_tracks)
                        result['music'] = tracks
                    
                    st.session_state.result = result
                    st.success("✅ 완료!")
                
                except Exception as e:
                    st.error(f"오류: {str(e)}")
        else:
            st.warning("감정을 입력해주세요!")

with col2:
    st.header("📊 결과")
    
    if st.session_state.result:
        result = st.session_state.result
        
        st.markdown(f"### ✨ 주요 감정: **{result['main_emotion']}** ({result['emotion_score']:.1f}%)")
        
        st.markdown("#### 감정 분포")
        for emotion, score in sorted(result['all_emotions'].items(), 
                                     key=lambda x: x[1], reverse=True):
            st.progress(score / 100, text=f"{emotion}: {score:.1f}%")
        
        st.markdown("---")
        
        if result['image_path'] and os.path.exists(result['image_path']):
            st.markdown("### 🎨 감정 그라데이션 아트")
            st.image(result['image_path'], use_container_width=True)
        
        if result['music']:
            st.markdown("### 🎵 추천 음악")
            for i, track in enumerate(result['music'], 1):
                with st.expander(f"{i}. {track['name']} - {track['artist']}"):
                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        if track.get('image'):
                            st.image(track['image'], width=100)
                    with col_b:
                        st.markdown(f"**아티스트:** {track['artist']}")
                        st.markdown(f"[🔗 Spotify에서 듣기]({track['url']})")
    else:
        st.info("왼쪽에 감정을 입력하세요!")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><p>Emotion Curator | Powered by KoBERT & AI</p></div>", 
           unsafe_allow_html=True)
