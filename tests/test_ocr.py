"""
测试 - OCR模块
"""
import pytest
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime

from app.ocr_engine import ImagePreprocessor, OCREngine, HandwritingDetector, QualityAssessment


@pytest.fixture
def sample_image():
    """创建示例图像"""
    # 创建一个简单的文本图像
    image = np.ones((200, 400, 3), dtype=np.uint8) * 255
    cv2.putText(image, 'Test Image', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    return image


class TestImagePreprocessor:
    """测试图像预处理"""
    
    def test_grayscale_conversion(self, sample_image):
        """测试灰度转换"""
        gray = ImagePreprocessor.convert_to_grayscale(sample_image)
        assert len(gray.shape) == 2  # 灰度图只有两个维度
        assert gray.dtype == np.uint8
    
    def test_threshold_binary(self, sample_image):
        """测试二值化阈值"""
        gray = ImagePreprocessor.convert_to_grayscale(sample_image)
        thresholded = ImagePreprocessor.apply_threshold(gray, method='binary')
        
        unique_values = np.unique(thresholded)
        assert len(unique_values) == 2  # 只有两个值：0和255
    
    def test_denoise(self, sample_image):
        """测试去噪"""
        gray = ImagePreprocessor.convert_to_grayscale(sample_image)
        denoised = ImagePreprocessor.denoise(gray)
        
        assert denoised.shape == gray.shape
        assert denoised.dtype == gray.dtype
    
    def test_resize_image(self, sample_image):
        """测试图像缩放"""
        gray = ImagePreprocessor.convert_to_grayscale(sample_image)
        resized = ImagePreprocessor.resize_image(gray, scale=2.0)
        
        assert resized.shape[0] == gray.shape[0] * 2
        assert resized.shape[1] == gray.shape[1] * 2


class TestQualityAssessment:
    """测试质量评估"""
    
    def test_assess_quality(self, sample_image):
        """测试质量评估"""
        gray = ImagePreprocessor.convert_to_grayscale(sample_image)
        quality = QualityAssessment.assess_quality(gray)
        
        assert 'overall_score' in quality
        assert 'sharpness' in quality
        assert 'brightness' in quality
        assert 'contrast' in quality
        assert 'noise_level' in quality
        
        # 检查得分范围
        assert 0 <= quality['overall_score'] <= 100
        assert quality['overall_score'] > 0  # 测试图像应该有一定质量
    
    def test_quality_score_range(self, sample_image):
        """测试质量得分范围"""
        gray = ImagePreprocessor.convert_to_grayscale(sample_image)
        quality = QualityAssessment.assess_quality(gray)
        
        assert 0 <= quality['brightness'] <= 255
        assert quality['noise_level'] >= 0


class TestHandwritingDetector:
    """测试手写检测"""
    
    def test_detect_handwriting(self, sample_image):
        """测试手写检测"""
        gray = ImagePreprocessor.convert_to_grayscale(sample_image)
        
        is_handwritten, confidence = HandwritingDetector.detect_handwriting(gray)
        
        assert isinstance(is_handwritten, bool)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
