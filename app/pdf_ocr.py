"""
PDF OCR处理 - 支持扫���和混合类型的PDF票据
"""
import pdf2image
import logging
from typing import List, Dict, Optional
from pathlib import Path

from app.ocr_engine import AdvancedOCRProcessor
from app.pdf_parser import parse_invoice_pdf

logger = logging.getLogger(__name__)


class PDFOCRProcessor:
    """PDF OCR处理器"""
    
    def __init__(self):
        self.ocr_processor = AdvancedOCRProcessor()
        self.temp_dir = Path('temp_pdf_images')
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def pdf_to_images(self, pdf_path: str, dpi: int = 300) -> List[str]:
        """
        将PDF转换为图像
        
        Args:
            pdf_path: PDF文件路径
            dpi: 分辨率
            
        Returns:
            生成的图像文件路径列表
        """
        try:
            images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
            image_paths = []
            
            for idx, image in enumerate(images, 1):
                image_path = self.temp_dir / f"page_{idx:03d}.png"
                image.save(str(image_path), 'PNG')
                image_paths.append(str(image_path))
                logger.info(f"PDF页面转换成功: {image_path}")
            
            return image_paths
            
        except Exception as e:
            logger.error(f"PDF转图像失败: {str(e)}")
            return []
    
    def process_scanned_pdf(self, pdf_path: str, extract_text_from_images: bool = True) -> Dict:
        """
        处理扫描的PDF票据
        
        Args:
            pdf_path: PDF文件路径
            extract_text_from_images: 是否从图像提取文本
            
        Returns:
            处理结果
        """
        try:
            # 1. 转换为图像
            image_paths = self.pdf_to_images(pdf_path, dpi=300)
            if not image_paths:
                return {'status': 'failed', 'error': 'PDF转图像失败'}
            
            # 2. 处理每个页面
            page_results = []
            for image_path in image_paths:
                result = self.ocr_processor.process_document(image_path)
                page_results.append(result)
            
            # 3. 合并所有页面的文本
            combined_text = '\n'.join([
                result.get('ocr_result', {}).get('text', '')
                for result in page_results
                if result['status'] == 'success'
            ])
            
            # 4. 计算质量评分
            quality_scores = [
                result['quality_assessment']['overall_score']
                for result in page_results
                if result['status'] == 'success'
            ]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                'status': 'success',
                'pdf_path': pdf_path,
                'page_count': len(image_paths),
                'combined_text': combined_text,
                'average_quality': round(avg_quality, 2),
                'page_results': page_results
            }
            
        except Exception as e:
            logger.error(f"扫描PDF处理失败: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
    
    def process_mixed_pdf(self, pdf_path: str) -> Dict:
        """
        处理混合类型的PDF（既有文本又有扫描图像）
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            处理结果
        """
        try:
            # 先尝试直接提取文本（用于文本型PDF）
            try:
                import PyPDF2
                text_extracted = ""
                with open(pdf_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text_extracted += page.extract_text()
            except:
                text_extracted = ""
            
            # 如果文本提取不足，使用OCR
            if len(text_extracted) < 100:
                logger.info("文本提取不足，使用OCR处理")
                ocr_result = self.process_scanned_pdf(pdf_path)
                ocr_result['extraction_method'] = 'ocr'
                return ocr_result
            else:
                logger.info("使用直接文本提取")
                return {
                    'status': 'success',
                    'pdf_path': pdf_path,
                    'extraction_method': 'text',
                    'text': text_extracted
                }
            
        except Exception as e:
            logger.error(f"混合PDF处理失败: {str(e)}")
            return {'status': 'failed', 'error': str(e)}


class OCREnhancedInvoiceParser:
    """支持OCR增强的发票解析器"""
    
    def __init__(self):
        self.pdf_ocr_processor = PDFOCRProcessor()
        self.ocr_processor = AdvancedOCRProcessor()
    
    def parse_invoice_with_ocr(self, pdf_path: str, use_ocr_fallback: bool = True) -> Dict:
        """
        使用OCR增强的发票解析
        
        Args:
            pdf_path: PDF文件路径
            use_ocr_fallback: 如果直接解析失败是否使用OCR
            
        Returns:
            解析结果
        """
        try:
            # 1. 先尝试直接解析
            try:
                result = parse_invoice_pdf(pdf_path)
                if result.get('is_valid'):
                    result['extraction_method'] = 'direct'
                    return result
            except Exception as e:
                logger.warning(f"直接解析失败: {str(e)}")
                if not use_ocr_fallback:
                    raise
            
            # 2. 使用OCR作为备选方案
            logger.info("使用OCR进行发票解析")
            ocr_result = self.pdf_ocr_processor.process_mixed_pdf(pdf_path)
            
            if ocr_result['status'] != 'success':
                return {'is_valid': False, 'error': 'OCR处理失败'}
            
            # 3. 从OCR文本中提取信息
            extracted_text = ocr_result.get('text', '') or ocr_result.get('combined_text', '')
            
            # 4. 使用正则表达式从OCR文本中解析字段
            parsed_data = self._parse_text_to_invoice(extracted_text)
            parsed_data['extraction_method'] = 'ocr'
            parsed_data['ocr_quality'] = ocr_result.get('average_quality', 0)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"OCR增强解析失败: {str(e)}")
            return {'is_valid': False, 'error': str(e)}
    
    def _parse_text_to_invoice(self, text: str) -> Dict:
        """
        从提取的文本中解析发票信息
        
        Args:
            text: 提取的文本
            
        Returns:
            解析的发票数据
        """
        import re
        
        result = {
            'raw_text': text,
            'invoice_number': None,
            'payer_name': None,
            'self_payment_1': 0.0,
            'self_payment_2': 0.0,
            'other_payment': 0.0,
            'personal_out_of_pocket': 0.0,
            'medical_insurance': 0.0,
            'invoice_date': None,
            'parsing_errors': []
        }
        
        # 使用regex进行模式匹配
        patterns = {
            'invoice_number': r'票据号(?:码)?[\s：:]*([A-Z0-9]{10,})',
            'payer_name': r'交款(?:人)?(?:姓名)?[\s：:]*([^\n]+?)(?=\n|$)',
            'self_payment_1': r'自付(?:一)?[\s：:]*¥?\s*([\d.]+)',
            'self_payment_2': r'自付(?:二)?[\s：:]*¥?\s*([\d.]+)',
            'other_payment': r'其他(?:支付)?[\s：:]*¥?\s*([\d.]+)',
            'personal_out_of_pocket': r'个人自费[\s：:]*¥?\s*([\d.]+)',
            'medical_insurance': r'(?:医保范围内|医保支付)[\s：:]*¥?\s*([\d.]+)',
            'invoice_date': r'(?:日期|票据日期|开票日期)[\s：:]*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        }
        
        for field, pattern in patterns.items():
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    
                    if field in ['invoice_number', 'payer_name', 'invoice_date']:
                        result[field] = value
                    else:
                        try:
                            result[field] = float(value)
                        except ValueError:
                            result['parsing_errors'].append(f"无法解析{field}: {value}")
                else:
                    if field in ['invoice_number', 'payer_name']:
                        result['parsing_errors'].append(f"未找到字段: {field}")
            except Exception as e:
                result['parsing_errors'].append(f"解析{field}异常: {str(e)}")
        
        # 验证结果
        is_valid = bool(result['invoice_number'] and result['payer_name'])
        result['is_valid'] = is_valid
        
        return result
