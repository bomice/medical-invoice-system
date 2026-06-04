"""
OCR增强模块 - 支持手写和扫描票据识别
"""
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """图像预处理类"""
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        加载图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            图像数组或None
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图像: {image_path}")
            return img
        except Exception as e:
            logger.error(f"图像加载失败: {str(e)}")
            return None
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        转换为灰度图
        
        Args:
            image: 原始图像
            
        Returns:
            灰度图像
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def apply_threshold(image: np.ndarray, method: str = 'binary') -> np.ndarray:
        """
        应用阈值处理
        
        Args:
            image: 灰度图像
            method: 阈值方法 ('binary', 'otsu', 'adaptive')
            
        Returns:
            二值化图像
        """
        if method == 'binary':
            _, thresholded = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
        elif method == 'otsu':
            _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive':
            thresholded = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        else:
            thresholded = image
        
        return thresholded
    
    @staticmethod
    def denoise(image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        图像去噪
        
        Args:
            image: 输入图像
            strength: 去噪强度
            
        Returns:
            去噪后的图像
        """
        return cv2.fastNlMeansDenoising(image, None, h=strength, templateWindowSize=7, searchWindowSize=21)
    
    @staticmethod
    def resize_image(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
        """
        缩放图像
        
        Args:
            image: 输入图像
            scale: 缩放比例
            
        Returns:
            缩放后的图像
        """
        height, width = image.shape[:2]
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        旋转图像
        
        Args:
            image: 输入图像
            angle: 旋转角度
            
        Returns:
            旋转后的图像
        """
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
        return rotated
    
    @staticmethod
    def correct_skew(image: np.ndarray) -> np.ndarray:
        """
        校正倾斜的图像
        
        Args:
            image: 输入图像
            
        Returns:
            校正后的图像
        """
        # 检测文本方向
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = 90 + angle
        
        # 旋转图像以校正倾斜
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        增强对比度
        
        Args:
            image: 输入图像
            
        Returns:
            对比度增强后的图像
        """
        # 使用CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return enhanced
    
    @staticmethod
    def preprocess_pipeline(image_path: str, enhance: bool = True) -> Optional[np.ndarray]:
        """
        完整的预处理管道
        
        Args:
            image_path: 图像路径
            enhance: 是否进行增强处理
            
        Returns:
            预处理后的图像
        """
        try:
            # 1. 加载图像
            image = ImagePreprocessor.load_image(image_path)
            if image is None:
                return None
            
            # 2. 转换为灰度
            gray = ImagePreprocessor.convert_to_grayscale(image)
            
            # 3. 去噪
            denoised = ImagePreprocessor.denoise(gray)
            
            # 4. 校正倾斜
            skew_corrected = ImagePreprocessor.correct_skew(denoised)
            
            # 5. 增强对比度
            if enhance:
                enhanced = ImagePreprocessor.enhance_contrast(skew_corrected)
            else:
                enhanced = skew_corrected
            
            # 6. 应用自适应阈值
            thresholded = ImagePreprocessor.apply_threshold(enhanced, method='adaptive')
            
            # 7. 放大图像（提高OCR准确度）
            upscaled = ImagePreprocessor.resize_image(thresholded, scale=1.5)
            
            logger.info(f"图像预处理完成: {image_path}")
            return upscaled
            
        except Exception as e:
            logger.error(f"预处理管道失败: {str(e)}")
            return None


class OCREngine:
    """OCR引擎"""
    
    # Tesseract配置
    TESSERACT_CONFIG = {
        'cn': r'--oem 3 --psm 6 -l chi_sim+eng',  # 简体中文+英文
        'en': r'--oem 3 --psm 6 -l eng',          # 英文
        'mixed': r'--oem 3 --psm 6 -l chi_sim+eng'  # 混合
    }
    
    @staticmethod
    def extract_text(image: np.ndarray, language: str = 'mixed') -> str:
        """
        提取图像中的文本
        
        Args:
            image: 图像数组
            language: 语言类型 ('cn', 'en', 'mixed')
            
        Returns:
            提取的文本
        """
        try:
            config = OCREngine.TESSERACT_CONFIG.get(language, OCREngine.TESSERACT_CONFIG['mixed'])
            text = pytesseract.image_to_string(image, config=config)
            return text
        except Exception as e:
            logger.error(f"OCR提取失败: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_with_confidence(image: np.ndarray, language: str = 'mixed') -> Dict:
        """
        提取文本及其置信度
        
        Args:
            image: 图像数组
            language: 语言类型
            
        Returns:
            包含文本和置信度的字典
        """
        try:
            config = OCREngine.TESSERACT_CONFIG.get(language, OCREngine.TESSERACT_CONFIG['mixed'])
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            
            # 计算平均置信度
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            text = pytesseract.image_to_string(image, config=config)
            
            return {
                'text': text,
                'avg_confidence': avg_confidence,
                'words': len([c for c in confidences if c > 50]),
                'total_words': len(confidences)
            }
        except Exception as e:
            logger.error(f"OCR提取失败: {str(e)}")
            return {
                'text': '',
                'avg_confidence': 0,
                'words': 0,
                'total_words': 0
            }
    
    @staticmethod
    def extract_regions(image: np.ndarray, regions: List[Tuple]) -> Dict[str, str]:
        """
        从图像的特定区域提取文本
        
        Args:
            image: 图像数组
            regions: 区域列表 [(name, x1, y1, x2, y2), ...]
            
        Returns:
            每个区域的提取文本
        """
        results = {}
        
        try:
            for region_name, x1, y1, x2, y2 in regions:
                roi = image[y1:y2, x1:x2]
                text = OCREngine.extract_text(roi)
                results[region_name] = text.strip()
                logger.debug(f"区域 {region_name} 文本: {text[:50]}")
        except Exception as e:
            logger.error(f"区域提取失败: {str(e)}")
        
        return results


class HandwritingDetector:
    """手写识别检测器"""
    
    @staticmethod
    def detect_handwriting(image: np.ndarray, threshold: float = 0.5) -> Tuple[bool, float]:
        """
        检测图像是否包含手写文本
        
        Args:
            image: 图像数组
            threshold: 置信度阈值
            
        Returns:
            (是否为手写, 置信度)
        """
        try:
            # 分析像素分布特征
            # 手写文本通常具有较低的对比度和不均匀的笔画
            
            # 计算边缘密度
            edges = cv2.Canny(image, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size
            
            # 计算方差 - 手写通常方差较大
            variance = np.var(image)
            
            # 计算纹理特征
            texture_score = edge_density * (variance / 255.0)
            
            is_handwritten = texture_score > threshold
            
            logger.debug(f"手写检测 - 边缘密度: {edge_density:.3f}, 方差: {variance:.1f}, 得分: {texture_score:.3f}")
            
            return is_handwritten, texture_score
            
        except Exception as e:
            logger.error(f"手写检测失败: {str(e)}")
            return False, 0.0


class QualityAssessment:
    """图像质量评估"""
    
    @staticmethod
    def assess_quality(image: np.ndarray) -> Dict:
        """
        评估图像质量
        
        Args:
            image: 图像数组
            
        Returns:
            质量评估结果
        """
        try:
            # 清晰度评估（拉普拉斯方差）
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # 亮度评估
            brightness = np.mean(image)
            
            # 对比度评估
            contrast = np.std(image)
            
            # 噪声评估（局部二值模式）
            noise_level = 1 - (contrast / 128)  # 归一化噪声
            
            # 综合质量评分 (0-100)
            quality_score = (
                min(sharpness / 500 * 100, 100) * 0.3 +  # 清晰度权重30%
                min(brightness / 255 * 100, 100) * 0.2 +  # 亮度权重20%
                min(contrast / 128 * 100, 100) * 0.3 +    # 对比度权重30%
                (1 - noise_level) * 100 * 0.2              # 噪声权重20%
            )
            
            return {
                'overall_score': round(quality_score, 2),
                'sharpness': round(sharpness, 2),
                'brightness': round(brightness, 2),
                'contrast': round(contrast, 2),
                'noise_level': round(noise_level, 2),
                'is_quality': quality_score > 50
            }
            
        except Exception as e:
            logger.error(f"质量评估失败: {str(e)}")
            return {
                'overall_score': 0,
                'sharpness': 0,
                'brightness': 0,
                'contrast': 0,
                'noise_level': 0,
                'is_quality': False
            }


class AdvancedOCRProcessor:
    """高级OCR处理器 - 综合处理"""
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.ocr_engine = OCREngine()
        self.handwriting_detector = HandwritingDetector()
        self.quality_assessor = QualityAssessment()
    
    def process_document(self, image_path: str) -> Dict:
        """
        完整的文档处理流程
        
        Args:
            image_path: 图像路径
            
        Returns:
            处理结果
        """
        try:
            # 1. 预处理
            processed_image = self.preprocessor.preprocess_pipeline(image_path)
            if processed_image is None:
                return {'status': 'failed', 'error': '图像预处理失败'}
            
            # 2. 质量评估
            quality = self.quality_assessor.assess_quality(processed_image)
            
            if not quality['is_quality']:
                logger.warning(f"图像质量不佳: {quality['overall_score']}")
            
            # 3. 手写检测
            is_handwritten, handwriting_score = self.handwriting_detector.detect_handwriting(processed_image)
            
            # 4. OCR提取
            ocr_result = self.ocr_engine.extract_text_with_confidence(processed_image)
            
            return {
                'status': 'success',
                'image_path': image_path,
                'processed_at': datetime.utcnow().isoformat(),
                'quality_assessment': quality,
                'handwriting_detection': {
                    'is_handwritten': is_handwritten,
                    'confidence': handwriting_score
                },
                'ocr_result': ocr_result
            }
            
        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'image_path': image_path
            }
    
    def process_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        批量处理图像
        
        Args:
            image_paths: 图像路径列表
            
        Returns:
            处理结果列表
        """
        results = []
        
        for idx, image_path in enumerate(image_paths, 1):
            logger.info(f"处理 {idx}/{len(image_paths)}: {image_path}")
            result = self.process_document(image_path)
            results.append(result)
        
        return results
    
    def save_processed_image(self, image_path: str, output_dir: str = 'processed_images') -> str:
        """
        保存预处理后的图像
        
        Args:
            image_path: 原始图像路径
            output_dir: 输出目录
            
        Returns:
            保存的图像路径
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            processed_image = self.preprocessor.preprocess_pipeline(image_path)
            if processed_image is None:
                raise ValueError("预处理失败")
            
            # 生成输出文件名
            filename = Path(image_path).stem + '_processed.png'
            output_path = Path(output_dir) / filename
            
            cv2.imwrite(str(output_path), processed_image)
            logger.info(f"预处理图像已保存: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"保存预处理图像失败: {str(e)}")
            return ""
