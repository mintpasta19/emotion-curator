import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from dotenv import load_dotenv
import numpy as np
import math
import random

load_dotenv()

class ImageGenerator:
    """
    감정 비율 기반 예술적 그라데이션 아트 생성 (랜덤 변형)
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
        
        # 랜덤 시드 (매번 다른 결과)
        random.seed()
        
        print(f"\n🎨 예술적 그라데이션 생성 중... (스타일: {style})")
        
        # 이미지 크기
        width, height = 1920, 1080
        
        # 감정별 색상과 비율 준비
        emotions_sorted = sorted(emotion_percentages.items(), 
                                key=lambda x: x[1], 
                                reverse=True)
        
        print(f"   감정 비율:")
        for emotion, percent in emotions_sorted:
            print(f"   {emotion}: {percent:.1f}%")
        
        # 스타일별 이미지 생성 (랜덤 파라미터 포함)
        if style == 'waves':
            image = self._create_wave_style(width, height, emotions_sorted)
        elif style == 'aurora':
            image = self._create_aurora_style(width, height, emotions_sorted)
        elif style == 'abstract':
            image = self._create_abstract_style(width, height, emotions_sorted)
        elif style == 'marble':
            image = self._create_marble_style(width, height, emotions_sorted)
        else:  # dynamic
            image = self._create_dynamic_style(width, height, emotions_sorted)
        
        # 후처리: 색상 강화 (랜덤 강도)
        image = self._enhance_colors(image)
        
        # 저장
        image.save(save_path, quality=95)
        print(f"✓ 이미지 저장: {save_path}")
        
        return image
    
    def _create_dynamic_style(self, width, height, emotions_sorted):
        """
        역동적인 곡선 스타일 (랜덤 변형)
        """
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # 랜덤 파라미터
        num_waves = random.randint(3, 6)  # 물결 개수
        wave_speeds = [random.uniform(1.5, 4.0) for _ in range(num_waves)]
        wave_amplitudes = [random.uniform(0.1, 0.4) for _ in range(num_waves)]
        phase_shifts = [random.uniform(0, math.pi * 2) for _ in range(num_waves)]
        
        # 랜덤 방향 (수평/수직/대각선)
        direction = random.choice(['horizontal', 'vertical', 'diagonal', 'radial'])
        
        print(f"   🎲 랜덤 설정: {num_waves}개 물결, {direction} 방향")
        
        # 감정별 위치 및 영향력
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
        
        # 픽셀별 색상 계산
        for y in range(height):
            for x in range(width):
                norm_x = x / width
                norm_y = y / height
                
                # 방향에 따른 기본 위치
                if direction == 'horizontal':
                    base_position = norm_x
                elif direction == 'vertical':
                    base_position = norm_y
                elif direction == 'diagonal':
                    base_position = (norm_x + norm_y) / 2
                else:  # radial
                    cx, cy = 0.5, 0.5
                    distance = math.sqrt((norm_x - cx)**2 + (norm_y - cy)**2)
                    base_position = distance
                
                # 다중 랜덤 사인파
                wave_offset = 0
                for i in range(num_waves):
                    wave_offset += math.sin(
                        norm_x * math.pi * wave_speeds[i] + 
                        norm_y * math.pi * wave_speeds[i] * 0.7 +
                        phase_shifts[i]
                    ) * wave_amplitudes[i]
                
                # 추가 노이즈
                noise = random.uniform(-0.05, 0.05)
                position = (base_position + wave_offset + noise) % 1.0
                
                # 색상 계산
                color = self._get_blended_color(position * 100, emotion_zones)
                
                # 랜덤 밝기 변화 (미묘하게)
                brightness = 1.0 + random.uniform(-0.1, 0.1)
                color = tuple(int(c * brightness) for c in color)
                color = tuple(max(0, min(255, c)) for c in color)
                
                pixels[x, y] = color
        
        return image
    
    def _create_wave_style(self, width, height, emotions_sorted):
        """
        물결 스타일 (랜덤 변형)
        """
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # 랜덤 물결 파라미터
        num_layers = random.randint(3, 6)
        frequencies = [random.uniform(1.5, 4.5) for _ in range(num_layers)]
        amplitudes = [random.uniform(0.05, 0.2) for _ in range(num_layers)]
        
        print(f"   🎲 랜덤 설정: {num_layers}개 레이어")
        
        for y in range(height):
            for x in range(width):
                norm_x = x / width
                norm_y = y / height
                
                # 다중 물결
                wave_offset = 0
                for i in range(num_layers):
                    phase = random.uniform(0, math.pi)
                    wave_offset += math.sin(
                        norm_x * math.pi * frequencies[i] + 
                        norm_y * math.pi + phase
                    ) * amplitudes[i] / (i + 1)
                
                position = (norm_x + wave_offset) % 1.0
                color = self._get_smooth_gradient_color(position * 100, emotions_sorted)
                
                pixels[x, y] = color
        
        # 랜덤 블러 강도
        blur_radius = random.randint(10, 25)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        return image
    
    def _create_aurora_style(self, width, height, emotions_sorted):
        """
        오로라 스타일 (랜덤 변형)
        """
        # 랜덤 배경색
        bg_darkness = random.randint(5, 25)
        image = Image.new('RGB', (width, height), (bg_darkness, bg_darkness, bg_darkness + 20))
        draw = ImageDraw.Draw(image, 'RGBA')
        
        print(f"   🎲 랜덤 설정: 배경 어두움 {bg_darkness}")
        
        # 각 감정별 오로라 레이어
        for idx, (emotion, percent) in enumerate(emotions_sorted):
            if percent < 3:
                continue
            
            color = self.emotion_colors[emotion]
            alpha = int(percent * random.uniform(1.8, 2.8))
            color_with_alpha = color + (min(255, alpha),)
            
            # 랜덤 곡선 개수
            num_curves = random.randint(2, 5)
            
            for i in range(num_curves):
                points = []
                
                # 랜덤 시작 위치
                y_base = random.uniform(0.2, 0.8) * height
                frequency = random.uniform(2, 5)
                amplitude = random.uniform(0.1, 0.2) * height
                
                for x in range(0, width + 10, 10):
                    phase = random.uniform(0, math.pi * 2)
                    y = y_base + math.sin(x / width * math.pi * frequency + phase) * amplitude
                    y += math.cos(x / width * math.pi * (frequency * 1.3)) * amplitude * 0.5
                    points.append((x, int(y)))
                
                # 랜덤 선 두께
                line_width = random.randint(60, 120)
                
                if len(points) > 1:
                    draw.line(points, fill=color_with_alpha, width=line_width)
        
        # 랜덤 블러
        blur_radius = random.randint(30, 50)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        return image
    
    def _create_abstract_style(self, width, height, emotions_sorted):
        """
        추상화 스타일 (랜덤 변형)
        """
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image, 'RGBA')
        
        # 배경 그라데이션
        for y in range(height):
            ratio = y / height
            base_color = self._get_smooth_gradient_color(ratio * 100, emotions_sorted)
            draw.line([(0, y), (width, y)], fill=base_color)
        
        # 감정별 추상 도형
        for idx, (emotion, percent) in enumerate(emotions_sorted):
            if percent < 5:
                continue
            
            color = self.emotion_colors[emotion]
            alpha = int(percent * random.uniform(1.2, 2.0))
            color_with_alpha = color + (min(255, alpha),)
            
            # 랜덤 도형 개수
            num_shapes = random.randint(2, 6)
            
            print(f"   🎲 {emotion}: {num_shapes}개 도형")
            
            for i in range(num_shapes):
                # 랜덤 위치와 크기
                cx = random.randint(0, width)
                cy = random.randint(0, height)
                radius_x = random.randint(int(width * 0.05), int(width * 0.2))
                radius_y = random.randint(int(height * 0.1), int(height * 0.25))
                
                bbox = [
                    cx - radius_x, cy - radius_y,
                    cx + radius_x, cy + radius_y
                ]
                
                # 랜덤 도형 선택
                shape_type = random.choice(['ellipse', 'ellipse', 'rectangle'])
                
                if shape_type == 'ellipse':
                    draw.ellipse(bbox, fill=color_with_alpha)
                else:
                    draw.rectangle(bbox, fill=color_with_alpha)
        
        # 랜덤 블러
        blur_radius = random.randint(40, 70)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        return image
    
    def _create_marble_style(self, width, height, emotions_sorted):
        """
        대리석 스타일 (랜덤 변형)
        """
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # 랜덤 대리석 파라미터
        num_octaves = random.randint(4, 7)
        vein_frequency = random.uniform(15, 30)
        vein_threshold = random.uniform(0.08, 0.15)
        
        print(f"   🎲 랜덤 설정: {num_octaves}개 옥타브, 무늬 빈도 {vein_frequency:.1f}")
        
        # 랜덤 시드로 노이즈 변형
        seed_offset_x = random.uniform(0, 100)
        seed_offset_y = random.uniform(0, 100)
        
        for y in range(height):
            for x in range(width):
                norm_x = x / width
                norm_y = y / height
                
                # 펄린 노이즈 느낌
                noise = 0
                frequency = 1
                amplitude = 1
                
                for octave in range(num_octaves):
                    noise += amplitude * (
                        math.sin((norm_x + seed_offset_x) * math.pi * frequency * 5) * 
                        math.cos((norm_y + seed_offset_y) * math.pi * frequency * 3) +
                        math.sin(((norm_x + norm_y) + seed_offset_x) * math.pi * frequency * 4)
                    )
                    frequency *= 2
                    amplitude *= 0.5
                
                # 노이즈 정규화
                position = ((noise + 2) / 4) * 100
                position = max(0, min(100, position))
                
                # 색상
                color = self._get_smooth_gradient_color(position, emotions_sorted)
                
                # 대리석 무늬 (랜덤)
                vein = abs(math.sin(norm_x * vein_frequency + noise * 5)) < vein_threshold
                if vein:
                    darken = random.uniform(0.6, 0.8)
                    color = tuple(int(c * darken) for c in color)
                
                pixels[x, y] = color
        
        # 랜덤 블러
        blur_radius = random.randint(1, 4)
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        return image
    
    def _get_blended_color(self, position, emotion_zones):
        """
        여러 감정 색상을 블렌딩 (랜덤 변형)
        """
        total_weight = 0
        blended_r, blended_g, blended_b = 0, 0, 0
        
        for zone in emotion_zones:
            mid_point = (zone['start'] + zone['end']) / 2
            distance = abs(position - mid_point)
            
            # 랜덤 범위 폭
            range_width = (zone['end'] - zone['start']) / 2 + random.uniform(15, 25)
            
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
                local_ratio = (position - start) / (end - start) if end > start else 0
                
                color1 = self.emotion_colors[emotion]
                
                # 다음 감정과 블렌딩 (랜덤 블렌드 시작점)
                blend_start = random.uniform(0.5, 0.7)
                
                if i < len(emotions_sorted) - 1 and local_ratio > blend_start:
                    next_emotion = emotions_sorted[i + 1][0]
                    color2 = self.emotion_colors[next_emotion]
                    blend_ratio = (local_ratio - blend_start) / (1 - blend_start)
                    return self._blend_colors(color1, color2, blend_ratio)
                
                return color1
            
            cumulative = end
        
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
        색상 강화 (랜덤 강도)
        """
        # 랜덤 채도
        saturation = random.uniform(1.3, 1.6)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)
        
        # 랜덤 대비
        contrast = random.uniform(1.1, 1.4)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        
        # 랜덤 선명도
        sharpness = random.uniform(1.0, 1.3)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness)
        
        print(f"   🎨 색상 보정: 채도 {saturation:.2f}, 대비 {contrast:.2f}, 선명도 {sharpness:.2f}")
        
        return image


# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("예술적 감정 그라데이션 아트 생성기 (랜덤 변형)")
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
    
    # 같은 스타일을 3번 생성 (매번 다른 결과)
    style = 'dynamic'
    
    for i in range(3):
        print(f"\n{'='*60}")
        print(f"생성 #{i+1} - {style} 스타일")
        image = generator.generate_image(
            test_emotions, 
            save_path=f'test_{style}_{i+1}.png',
            style=style
        )
