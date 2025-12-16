import streamlit as st
from emotion_analyzer import analyze_emotion_advanced
from image_generator import ImageGenerator
from music_recommender import MusicRecommender
import os

# 페이지 설정
st.set_page_config(
    page_title="Emotion Curator",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 키 로드 함수
def load_api_keys():
    """Streamlit Secrets 또는 .env에서 API 키 로드"""
    try:
        # Streamlit Cloud
        huggingface_key = st.secrets["HUGGINGFACE_API_KEY"]
        spotify_client_id = st.secrets["SPOTIFY_CLIENT_ID"]
        spotify_client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
    except:
        # 로컬 환경
        from dotenv import load_dotenv
        load_dotenv()
        huggingface_key = os.getenv("HUGGINGFACE_API_KEY")
        spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
        spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    return huggingface_key, spotify_client_id, spotify_client_secret

# CSS 스타일
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 18px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .emotion-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .color-box {
        padding: 12px;
        margin: 5px 0;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("<h1>🎭 Emotion Curator</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>감정을 예술로 표현합니다</p>", unsafe_allow_html=True)

# 세션 상태 초기화
if 'result' not in st.session_state:
    st.session_state.result = None

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 아트 스타일 선택
    st.subheader("🎨 아트 스타일")
    art_style = st.selectbox(
        "스타일 선택",
        ['dynamic', 'waves', 'aurora', 'abstract', 'marble'],
        format_func=lambda x: {
            'dynamic': '🌊 역동적 (추천)',
            'waves': '〰️ 물결',
            'aurora': '✨ 오로라',
            'abstract': '🎨 추상화',
            'marble': '💎 대리석'
        }[x],
        help="감정을 표현할 예술 스타일을 선택하세요"
    )
    
    # 스타일 설명
    style_descriptions = {
        'dynamic': '여러 곡선이 어우러진 역동적인 스타일',
        'waves': '부드럽게 흐르는 물결 효과',
        'aurora': '신비로운 오로라 빛 효과',
        'abstract': '현대 미술 느낌의 추상화',
        'marble': '고급스러운 대리석 텍스처'
    }
    st.caption(style_descriptions[art_style])
    
    st.markdown("---")
    
    # 기능 설정
    st.subheader("🛠️ 기능")
    generate_image = st.checkbox("🖼️ 이미지 생성", value=True)
    recommend_music = st.checkbox("🎵 음악 추천", value=True)
    
    if recommend_music:
        num_tracks = st.slider("추천 곡 수", 3, 10, 5)
    else:
        num_tracks = 5
    
    st.markdown("---")
    
    # 감정 색상 가이드
    st.subheader("🎨 감정 색상 가이드")
    colors = {
        '분노': '#DC143C',
        '슬픔': '#4682B4',
        '불안': '#8A2BE2',
        '상처': '#BA55D3',
        '당황': '#FFA500',
        '기쁨': '#FFD700'
    }
    
    for emotion, color in colors.items():
        st.markdown(
            f"<div class='color-box' style='background:{color};'>{emotion}</div>", 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.caption("💡 Tip: 다양한 스타일을 시도해보세요!")

# 메인 레이아웃
col1, col2 = st.columns([1, 1], gap="large")

# 왼쪽: 입력 섹션
with col1:
    st.header("✍️ 감정 입력")
    
    # 예시 텍스트
    with st.expander("💭 예시 보기"):
        st.markdown("""
        **기쁨:**
        - "오늘 정말 기분이 좋아요! 모든 일이 잘 풀렸어요."
        
        **슬픔:**
        - "너무 슬프고 우울해요. 아무것도 하기 싫어요."
        
        **불안:**
        - "시험이 다가와서 너무 불안하고 걱정돼요."
        
        **복합 감정:**
        - "기쁘기도 하지만 동시에 걱정도 되고 불안해요."
        """)
    
    # 텍스트 입력
    user_text = st.text_area(
        "지금 느끼는 감정을 자유롭게 작성해주세요:",
        height=200,
        placeholder="예: 오늘 프로젝트 발표가 성공적이었어요! 하지만 다음 주 시험이 걱정돼요...",
        help="여러 감정이 섞여 있어도 괜찮습니다. 자유롭게 표현해주세요."
    )
    
    # 분석 버튼
    if st.button("🔍 감정 분석 & 아트 생성", use_container_width=True):
        if user_text.strip():
            with st.spinner("✨ 감정을 분석하고 예술 작품을 만드는 중..."):
                try:
                    # API 키 로드
                    hf_key, spotify_id, spotify_secret = load_api_keys()
                    os.environ["HUGGINGFACE_API_KEY"] = hf_key
                    os.environ["SPOTIFY_CLIENT_ID"] = spotify_id
                    os.environ["SPOTIFY_CLIENT_SECRET"] = spotify_secret
                    
                    # 감정 분석
                    emotions = analyze_emotion_advanced(user_text, method='weighted')
                    main_emotion = max(emotions.items(), key=lambda x: x[1])
                    
                    result = {
                        'text': user_text,
                        'main_emotion': main_emotion[0],
                        'emotion_score': main_emotion[1],
                        'all_emotions': emotions,
                        'image_path': None,
                        'music': [],
                        'style': art_style
                    }
                    
                    # 이미지 생성
                    if generate_image:
                        image_gen = ImageGenerator()
                        image_path = 'emotion_gradient.png'
                        image_gen.generate_image(
                            emotions, 
                            save_path=image_path,
                            style=art_style
                        )
                        result['image_path'] = image_path
                    
                    # 음악 추천
                    if recommend_music:
                        try:
                            music_rec = MusicRecommender()
                            tracks = music_rec.recommend_music(
                                main_emotion[0], 
                                limit=num_tracks
                            )
                            result['music'] = tracks
                        except Exception as e:
                            st.warning(f"음악 추천 중 오류: {str(e)}")
                    
                    st.session_state.result = result
                    st.success("✅ 완료!")
                    st.balloons()
                
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
                    st.info("API 키를 확인해주세요.")
        else:
            st.warning("⚠️ 감정을 입력해주세요!")

# 오른쪽: 결과 섹션
with col2:
    st.header("📊 분석 결과")
    
    if st.session_state.result:
        result = st.session_state.result
        
        # 주요 감정 표시
        st.markdown("### ✨ 주요 감정")
        emotion_emoji = {
            '기쁨': '😊',
            '슬픔': '😢',
            '불안': '😰',
            '분노': '😠',
            '상처': '💔',
            '당황': '😳'
        }
        
        main_emotion_display = f"{emotion_emoji.get(result['main_emotion'], '🎭')} **{result['main_emotion']}**"
        st.markdown(f"<h2 style='text-align: center;'>{main_emotion_display}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 1.5rem; color: #667eea;'>{result['emotion_score']:.1f}%</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 감정 분포
        st.markdown("### 📊 감정 분포")
        sorted_emotions = sorted(
            result['all_emotions'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for emotion, score in sorted_emotions:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(score / 100, text=f"{emotion_emoji.get(emotion, '🎭')} {emotion}")
            with col_b:
                st.markdown(f"**{score:.1f}%**")
        
        st.markdown("---")
        
        # 이미지 표시
        if result['image_path'] and os.path.exists(result['image_path']):
            st.markdown(f"### 🎨 감정 아트 ({result['style']} 스타일)")
            st.image(result['image_path'], use_container_width=True)
            
            # 다운로드 버튼
            with open(result['image_path'], 'rb') as file:
                st.download_button(
                    label="🖼️ 이미지 다운로드",
                    data=file,
                    file_name=f"emotion_art_{result['main_emotion']}.png",
                    mime="image/png",
                    use_container_width=True
                )
        
        st.markdown("---")
        
        # 음악 추천
        if result['music']:
            st.markdown("### 🎵 추천 음악")
            st.caption(f"{result['main_emotion']} 감정에 어울리는 음악")
            
            for i, track in enumerate(result['music'], 1):
                with st.expander(f"🎵 {i}. {track['name']} - {track['artist']}", expanded=(i==1)):
                    col_img, col_info = st.columns([1, 3])
                    
                    with col_img:
                        if track.get('image'):
                            st.image(track['image'], width=120)
                    
                    with col_info:
                        st.markdown(f"**아티스트:** {track['artist']}")
                        if track.get('album'):
                            st.markdown(f"**앨범:** {track['album']}")
                        st.markdown(f"[🎧 Spotify에서 듣기]({track['url']})")
    
    else:
        # 초기 상태
        st.info("👈 왼쪽에 감정을 입력하고 분석 버튼을 눌러주세요!")
        
        # 안내 이미지 또는 플레이스홀더
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
            <h2>🎨 감정을 예술로</h2>
            <p style='font-size: 1.1rem; margin-top: 1rem;'>
                여러분의 감정을 아름다운 그라데이션 아트와<br>
                어울리는 음악으로 표현해드립니다
            </p>
        </div>
        """, unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem;'>
    <p><strong>🎭 Emotion Curator</strong></p>
    <p>Powered by KoBERT, Stable Diffusion & Spotify API</p>
    <p style='font-size: 0.9rem; margin-top: 0.5rem;'>
        Made with ❤️ for understanding emotions through art
    </p>
</div>
""", unsafe_allow_html=True)
