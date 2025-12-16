# 🎭 Emotion Curator

감정 분석 기반 이미지 및 음악 큐레이션 시스템

## 📌 주요 기능

- **감정 분석**: KoBERT 기반 6가지 감정 분류 (분노, 슬픔, 불안, 상처, 당황, 기쁨)
- **이미지 생성**: Stable Diffusion을 통한 감정 표현 이미지 생성
- **음악 추천**: Spotify API 기반 감정에 맞는 음악 추천

## 🚀 설치 방법

### 1. 저장소 복제
git clone https://github.com/YOUR_USERNAME/emotion-curator.git
cd emotion-curator


### 2. 가상환경 생성
python -m venv venv
source venv/bin/activate # Mac/Linux
venv\Scripts\activate # Windows


### 3. 패키지 설치
pip install -r requirements.txt


### 4. 환경 변수 설정
`.env` 파일 생성:
HUGGINGFACE_API_KEY=your_key_here
SPOTIFY_CLIENT_ID=your_key_here
SPOTIFY_CLIENT_SECRET=your_key_here

API 키 발급:
- Hugging Face: https://huggingface.co/settings/tokens
- Spotify: https://developer.spotify.com/dashboard


## 💻 실행 방법
streamlit run app.py

브라우저에서 자동으로 열립니다: http://localhost:8501

## 📊 모델 정보

- **Base Model**: KoBERT (Korean BERT)
- **Training Data**: AI Hub 감성 대화 데이터
- **Accuracy**: 78.13%

## 🛠️ 기술 스택

- Python 3.8+
- PyTorch
- Transformers (KoBERT)
- Streamlit
- Hugging Face API
- Spotify API

## 📝 라이선스

MIT License

## 👨‍💻 개발자

진성범 - 캡스톤 디자인 프로젝트
