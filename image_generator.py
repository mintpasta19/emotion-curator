import os
from PIL import Image, ImageDraw, ImageFilter
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class ImageGenerator:
    """
    감정 비율 기반 그라데이션 아트 생성
    """
    def __init__(self):
        # 감정별 대표 색상 (RGB)
        self.emotion_colors = {
            '분노': (220, 20, 60),      # Crimson Red
            '슬픔': (70, 130, 180),     # Steel Blue
            '불안': (138, 43, 226),     # Blue Violet
            '상처': (186, 85, 211),     # Medium Orchid
            '당황': (255, 165, 0),      # Orange
            '기쁨': (255, 215, 0)       # Gold
        }
    
    def generate_image(self, emotion_percentages, save_path=None):
        """
        감정 비율에 따른 그라데이션 이미지 생성
        
        Parameters:
        - emotion_percentages: dict {'분노': 10.5, '슬픔': 20.3, ...}
        - save_path: 저장 경로
        
        Returns:
        - PIL Image
        """
        if save_path is None:
            main_emotion = max(emotion_percentages.items(), key=lambda x: x[1])[0]
            save_path = f'emotion_{main_emotion}.png'
        
        print(f"\n🎨 그라데이션 아트 생성 중...")
        
        # 이미지 크기
        width, height = 1920, 1080  # Full HD
        
        # 감정별 색상과 비율 준비
        emotions_sorted = sorted(emotion_percentages.items(), 
                                key=lambda x: x[1], 
                                reverse=True)
        
        print(f"   감정 비율:")
        for emotion, percent in emotions_sorted:
            print(f"   {emotion}: {percent:.1f}%")
        
        # 방법 1: 수평 그라데이션 (비율대로)
        image = self._create_horizontal_gradient(
            width, height, emotions_sorted
        )
        
        # 방법 2: 물결 효과 추가
        image = self._add_wave_effect(image)
        
        # 방법 3: 부드러운 블렌딩
        image = self._smooth_blend(image)
        
        # 저장
        image.save(save_path, quality=95)
        print(f"✓ 이미지 저장: {save_path}")
        
        return image
    
    def _create_horizontal_gradient(self, width, height, emotions_sorted):
        """
        감정 비율에 따른 수평 그라데이션
        """
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # 각 감정의 시작/끝 위치 계산
        positions = []
        cumulative = 0
        
        for emotion, percent in emotions_sorted:
            if percent > 0:
                start = cumulative
                end = cumulative + (percent / 100)
                positions.append((emotion, start, end))
                cumulative = end
        
        # 픽셀별로 색상 계산
        for x in range(width):
            ratio = x / width
            
            # 현재 위치의 색상 찾기
            color = self._get_color_at_position(ratio, positions)
            
            # 세로로 같은 색상
            for y in range(height):
                pixels[x, y] = color
        
        return image
    
    def _get_color_at_position(self, ratio, positions):
        """
        특정 위치의 색상 계산 (그라데이션)
        """
        # 어느 구간에 속하는지 찾기
        for i, (emotion, start, end) in enumerate(positions):
            if start <= ratio <= end:
                # 구간 내 위치
                local_ratio = (ratio - start) / (end - start) if end > start else 0
                
                color1 = self.emotion_colors[emotion]
                
                # 다음 감정과 블렌딩
                if i < len(positions) - 1:
                    next_emotion = positions[i + 1][0]
                    color2 = self.emotion_colors[next_emotion]
                    
                    # 경계 부근에서 부드럽게 섞기
                    if local_ratio > 0.7:
                        blend = (local_ratio - 0.7) / 0.3
                        return self._blend_colors(color1, color2, blend)
                
                return color1
        
        # 기본값
        return self.emotion_colors[positions[0][0]]
    
    def _blend_colors(self, color1, color2, ratio):
        """
        두 색상을 비율에 따라 블렌딩
        """
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        return (r, g, b)
    
    def _add_wave_effect(self, image):
        """
        물결 효과 추가 (이미지처럼 곡선 느낌)
        """
        width, height = image.size
        new_image = Image.new('RGB', (width, height))
        pixels = image.load()
        new_pixels = new_image.load()
        
        # 웨이브 파라미터
        amplitude = height * 0.15  # 물결 높이
        frequency = 3  # 물결 개수
        
        for x in range(width):
            for y in range(height):
                # 사인 곡선으로 y 좌표 변형
                wave_offset = int(amplitude * np.sin(2 * np.pi * frequency * x / width))
                source_y = y + wave_offset
                
                # 범위 체크
                if 0 <= source_y < height:
                    new_pixels[x, y] = pixels[x, source_y]
                else:
                    # 경계 처리
                    source_y = max(0, min(height - 1, source_y))
                    new_pixels[x, y] = pixels[x, source_y]
        
        return new_image
    
    def _smooth_blend(self, image):
        """
        부드러운 블렌딩 효과
        """
        # 가우시안 블러로 부드럽게
        image = image.filter(ImageFilter.GaussianBlur(radius=20))
        
        # 색상 강도 조정
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)  # 채도 증가
        
        return image


# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("감정 비율 기반 그라데이션 아트 테스트")
    print("=" * 60)
    
    generator = ImageGenerator()
    
    # 테스트 케이스
    test_cases = [
        {
            '기쁨': 60.5,
            '슬픔': 20.3,
            '불안': 10.2,
            '분노': 5.0,
            '상처': 3.0,
            '당황': 1.0
        },
        {
            '슬픔': 45.0,
            '불안': 30.0,
            '상처': 15.0,
            '기쁨': 10.0,
            '분노': 0,
            '당황': 0
        },
        {
            '분노': 50.0,
            '당황': 25.0,
            '기쁨': 15.0,
            '슬픔': 10.0,
            '불안': 0,
            '상처': 0
        }
    ]
    
    for i, emotions in enumerate(test_cases, 1):
        print(f"\n테스트 {i}")
        image = generator.generate_image(emotions, save_path=f'gradient_test_{i}.png')
        print()
