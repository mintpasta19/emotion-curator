import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from dotenv import load_dotenv
import numpy as np
import math

load_dotenv()

class ImageGenerator:
    """
    감정 비율 기반 예술적 그라데이션 아트 생성
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
    
    def generate_image(self, emotion_percentages, save_path=None, style='dynamic'):
        """
        감정 비율에 따른 예술적 그라데이션 이미지 생성
        
        Parameters:
        - emotion_percentages: dict {'분노': 10.5, '슬픔': 20.3, ...}
        - save_path: 저장 경로
        - style: 'dynamic', 'waves', 'aurora', 'abstract', 'marble'
        
        Returns:
        - PIL Image
        """
        if save_path is None:
            main_emotion = max(emotion_percentages.items(), key=lambda x: x[1])[0]
            save_path = f'emotion_art_{main_emotion}.png'
        
        print(f"\n🎨 예술적 그라데이션 생성 중... (스타일: {style})")
        
        # 이미지 크기
        width, height = 1920, 1080  # Full HD
        
        # 감정별 색상과 비율 준비
        emotions_sorted = sorted(emotion_percentages.items(), 
                                key=lambda x: x[1], 
                                reverse=True)
        
        print(f"   감정 비율:")
        for emotion, percent in emotions_sorted:
            print(f"   {emotion}: {percent:.1f}%")
        
        # 스타일별 이미지 생성
        if style == 'waves':
            image = self._create_wave_style(width, height, emotions_sorted)
        elif style == 'aurora':
            image = self._create_aurora_style(width, height, emotions_sorted)
        elif style == 'abstract':
            image = self._create_abstract_style(width, height, emotions_sorted)
        elif style == 'marble':
            image = self._create_marble_style(width, height, emotions_sorted)
        else:  # dynamic (기본)
            image = self._create_dynamic_style(width, height, emotions_sorted)
        
        # 후처리: 색상 강화
        image = self._enhance_colors(image)
        
        # 저장
        image.save(save_path, quality=95)
        print(f"✓ 이미지 저장: {save_path}")
        
        return image
    
    def _create_dynamic_style(self, width, height, emotions_sorted):
        """
        역동적인 곡선 스타일 (추천!)
        """
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # 감정별 위치 및 영향력 계산
        emotion_zones = []
        cumulative = 0
        
        for emotion, percent in emotions_sorted:
            if percent > 0:
                start = cumulative
                end = cumulative + percent
                emotion_zones.append({
                    'emotion': emotion,
                    'color': self.emotion_colors[emotion],
                    'start': start,
                    'end': end,
                    'strength': percent / 100
                })
                cumulative = end
        
        # 픽셀별 색상 계산 (다중 사인파 적용)
        for y in range(height):
            for x in range(width):
                # 정규화된 좌표
                norm_x = x / width
                norm_y = y / height
                
                # 다중 사인파로 역동적 효과
                wave1 = math.sin(norm_x * math.pi * 2 + norm_y * math.pi) * 0.3
                wave2 = math.cos(norm_x * math.pi * 3 - norm_y * math.pi * 2) * 0.2
                wave3 = math.sin((norm_x + norm_y) * math.pi * 4) * 0.15
                
                offset = wave1 + wave2 + wave3
                position = (norm_x + offset) % 1.0
                
                # 해당 위치의 색상 계산
                color = self._get_blended_color(position * 100, emotion_zones)
                
                # 미묘한 그라데이션 추가 (상하)
                brightness = 1.0 + (norm_y - 0.5) * 0.2
                color = tuple(int(c * brightness) for c in color)
                color = tuple(max(0, min(255, c)) for c in color)
                
                pixels[x, y] = color
        
        return image
    
    def _create_wave_style(self, width, height, emotions_sorted):
        """
        물결 스타일
        """
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # 여러 물결 레이어
        num_waves = len([e for e in emotions_sorted if e[1] > 5])
        
        for y in range(height):
            for x in range(width):
                norm_x = x / width
                norm_y = y / height
                
                # 다중 물결 효과
                wave_offset = 0
                for i in range(num_waves):
                    frequency = 2 + i * 1.5
                    amplitude = 0.1 / (i + 1)
                    wave_offset += math.sin(norm_x * math.pi * frequency + norm_y * math.pi) * amplitude
                
                position = (norm_x + wave_offset) % 1.0
                
                # 감정 구간 찾기
                color = self._get_smooth_gradient_color(position * 100, emotions_sorted)
                
                pixels[x, y] = color
        
        # 블러로 부드럽게
        image = image.filter(ImageFilter.GaussianBlur(radius=15))
        
        return image
    
    def _create_aurora_style(self, width, height, emotions_sorted):
        """
        오로라 스타일 (신비로운 느낌)
        """
        image = Image.new('RGB', (width, height), (10, 10, 30))
        draw = ImageDraw.Draw(image, 'RGBA')
        
        # 각 감정별 오로라 레이어
        for idx, (emotion, percent) in enumerate(emotions_sorted):
            if percent < 3:
                continue
            
            color = self.emotion_colors[emotion]
            
            # 반투명 레이어
            alpha = int(percent * 2.55)  # 0-255
            color_with_alpha = color + (alpha,)
            
            # 곡선 형태의 오로라
            num_curves = int(percent / 10) + 1
            
            for i in range(num_curves):
                # 곡선 경로 생성
                points = []
                y_offset = (idx + i) * height / (len(emotions_sorted) + 3)
                
                for x in range(0, width + 10, 10):
                    y = y_offset + math.sin(x / width * math.pi * 3 + idx) * height * 0.15
                    y += math.cos(x / width * math.pi * 5) * height * 0.1
                    points.append((x, int(y)))
                
                # 두꺼운 선으로 그리기
                if len(points) > 1:
                    draw.line(points, fill=color_with_alpha, width=80)
        
        # 블러로 오로라 효과
        image = image.filter(ImageFilter.GaussianBlur(radius=40))
        
        return image
    
    def _create_abstract_style(self, width, height, emotions_sorted):
        """
        추상화 스타일
        """
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image, 'RGBA')
        
        # 배경 그라데이션
        for y in range(height):
            ratio = y / height
            base_color = self._get_smooth_gradient_color(ratio * 100, emotions_sorted)
            draw.line([(0, y), (width, y)], fill=base_color)
        
        # 감정별 추상적 도형 추가
        for idx, (emotion, percent) in enumerate(emotions_sorted):
            if percent < 5:
                continue
            
            color = self.emotion_colors[emotion]
            alpha = int(percent * 1.5)
            color_with_alpha = color + (alpha,)
            
            # 원형 또는 타원 추가
            num_shapes = int(percent / 15) + 1
            
            for i in range(num_shapes):
                # 랜덤한 위치와 크기
                cx = int(width * (0.2 + idx * 0.15 + i * 0.1))
                cy = int(height * (0.3 + i * 0.2))
                radius_x = int(width * (0.1 + percent / 300))
                radius_y = int(height * (0.15 + percent / 400))
                
                bbox = [
                    cx - radius_x, cy - radius_y,
                    cx + radius_x, cy + radius_y
                ]
                
                draw.ellipse(bbox, fill=color_with_alpha)
        
        # 블러로 추상화
        image = image.filter(ImageFilter.GaussianBlur(radius=50))
        
        return image
    
    def _create_marble_style(self, width, height, emotions_sorted):
        """
        대리석 텍스처 스타일
        """
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # 펄린 노이즈 느낌의 대리석 효과
        for y in range(height):
            for x in range(width):
                norm_x = x / width
                norm_y = y / height
                
                # 복잡한 노이즈 패턴
                noise = 0
                frequency = 1
                amplitude = 1
                
                for octave in range(4):
                    noise += amplitude * (
                        math.sin(norm_x * math.pi * frequency * 5) * 
                        math.cos(norm_y * math.pi * frequency * 3) +
                        math.sin((norm_x + norm_y) * math.pi * frequency * 4)
                    )
                    frequency *= 2
                    amplitude *= 0.5
                
                # 노이즈를 0-1 범위로 정규화
                position = ((noise + 2) / 4) * 100
                position = max(0, min(100, position))
                
                # 색상 계산
                color = self._get_smooth_gradient_color(position, emotions_sorted)
                
                # 대리석 무늬 강조
                vein = abs(math.sin(norm_x * 20 + noise * 5)) < 0.1
                if vein:
                    color = tuple(int(c * 0.7) for c in color)
                
                pixels[x, y] = color
        
        # 약간의 블러
        image = image.filter(ImageFilter.GaussianBlur(radius=2))
        
        return image
    
    def _get_blended_color(self, position, emotion_zones):
        """
        여러 감정 색상을 블렌딩
        """
        # 가중 평균으로 색상 계산
        total_weight = 0
        blended_r, blended_g, blended_b = 0, 0, 0
        
        for zone in emotion_zones:
            # 거리 기반 가중치
            mid_point = (zone['start'] + zone['end']) / 2
            distance = abs(position - mid_point)
            range_width = (zone['end'] - zone['start']) / 2 + 20
            
            if distance < range_width:
                weight = (1 - distance / range_width) * zone['strength']
                total_weight += weight
                
                color = zone['color']
                blended_r += color[0] * weight
                blended_g += color[1] * weight
                blended_b += color[2] * weight
        
        if total_weight > 0:
            blended_r /= total_weight
            blended_g /= total_weight
            blended_b /= total_weight
        
        return (int(blended_r), int(blended_g), int(blended_b))
    
    def _get_smooth_gradient_color(self, position, emotions_sorted):
        """
        부드러운 그라데이션 색상
        """
        cumulative = 0
        
        for i, (emotion, percent) in enumerate(emotions_sorted):
            if percent == 0:
                continue
            
            start = cumulative
            end = cumulative + percent
            
            if start <= position <= end:
                # 구간 내 비율
                local_ratio = (position - start) / (end - start) if end > start else 0
                
                color1 = self.emotion_colors[emotion]
                
                # 다음 감정과 블렌딩
                if i < len(emotions_sorted) - 1 and local_ratio > 0.6:
                    next_emotion = emotions_sorted[i + 1][0]
                    color2 = self.emotion_colors[next_emotion]
                    blend_ratio = (local_ratio - 0.6) / 0.4
                    return self._blend_colors(color1, color2, blend_ratio)
                
                return color1
            
            cumulative = end
        
        # 기본값
        return self.emotion_colors[emotions_sorted[0][0]]
    
    def _blend_colors(self, color1, color2, ratio):
        """
        두 색상 블렌딩
        """
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        return (r, g, b)
    
    def _enhance_colors(self, image):
        """
        색상 강화 및 후처리
        """
        # 채도 증가
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.4)
        
        # 대비 증가
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # 선명도 증가
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        return image


# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("예술적 감정 그라데이션 아트 생성기")
    print("=" * 60)
    
    generator = ImageGenerator()
    
    # 테스트 감정
    test_emotions = {
        '기쁨': 45.5,
        '슬픔': 25.3,
        '불안': 15.2,
        '분노': 8.0,
        '상처': 4.0,
        '당황': 2.0
    }
    
    # 다양한 스타일 생성
    styles = ['dynamic', 'waves', 'aurora', 'abstract', 'marble']
    
    for style in styles:
        print(f"\n{'='*60}")
        print(f"스타일: {style}")
        image = generator.generate_image(
            test_emotions, 
            save_path=f'emotion_art_{style}.png',
            style=style
        )
        print(f"✓ 완료: emotion_art_{style}.png")
