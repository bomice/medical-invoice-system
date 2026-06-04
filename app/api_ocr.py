"""
OCR增强API端点
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from datetime import datetime
from pathlib import Path
import logging

from app.pdf_ocr import OCREnhancedInvoiceParser, PDFOCRProcessor
from app.ocr_engine import AdvancedOCRProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ocr"])


@router.post("/ocr/process-image")
async def process_image(file: UploadFile = File(...)):
    """
    处理单个图像文件进行OCR
    
    Args:
        file: 上传的图像文件
        
    Returns:
        OCR处理结果
    """
    try:
        # 验证文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")
        
        # 保存临时文件
        temp_path = Path('temp_ocr') / f"{datetime.utcnow().timestamp()}_{file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # 处理图像
        ocr_processor = AdvancedOCRProcessor()
        result = ocr_processor.process_document(str(temp_path))
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图像OCR处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR处理失败: {str(e)}")


@router.post("/ocr/process-scanned-pdf")
async def process_scanned_pdf(file: UploadFile = File(...)):
    """
    处理扫描的PDF票据（纯图像型PDF）
    
    Args:
        file: 上传的PDF文件
        
    Returns:
        OCR处理结果
    """
    try:
        # 验证文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 保存临时文件
        temp_path = Path('temp_ocr') / f"{datetime.utcnow().timestamp()}_{file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # 处理PDF
        pdf_ocr = PDFOCRProcessor()
        result = pdf_ocr.process_scanned_pdf(str(temp_path))
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"扫描PDF处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/ocr/process-mixed-pdf")
async def process_mixed_pdf(file: UploadFile = File(...)):
    """
    处理混合类型的PDF（文本+扫描图像）
    
    Args:
        file: 上传的PDF文件
        
    Returns:
        处理结果
    """
    try:
        # 验证文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 保存临时文件
        temp_path = Path('temp_ocr') / f"{datetime.utcnow().timestamp()}_{file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # 处理混合PDF
        pdf_ocr = PDFOCRProcessor()
        result = pdf_ocr.process_mixed_pdf(str(temp_path))
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"混合PDF处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.post("/ocr/parse-invoice")
async def parse_invoice_with_ocr(file: UploadFile = File(...), use_ocr_fallback: bool = Query(True)):
    """
    使用OCR增强的发票解析
    
    Args:
        file: 上传的PDF文件
        use_ocr_fallback: 如果直接解析失败是否使用OCR
        
    Returns:
        解析的发票数据
    """
    try:
        # 验证文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 保存临时文件
        temp_path = Path('temp_ocr') / f"{datetime.utcnow().timestamp()}_{file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # 使用OCR增强解析器
        parser = OCREnhancedInvoiceParser()
        result = parser.parse_invoice_with_ocr(str(temp_path), use_ocr_fallback)
        
        return {
            "status": "success" if result.get('is_valid') else "warning",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发票OCR解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.post("/ocr/batch-process-images")
async def batch_process_images(files: list[UploadFile] = File(...)):
    """
    批量处理图像文件
    
    Args:
        files: 上传的图像文件列表
        
    Returns:
        处理结果列表
    """
    try:
        results = []
        ocr_processor = AdvancedOCRProcessor()
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
        
        for file in files:
            file_ext = file.filename.split('.')[-1].lower()
            
            if file_ext not in allowed_extensions:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": f"不支持的文件格式: {file_ext}"
                })
                continue
            
            try:
                # 保存临时文件
                temp_path = Path('temp_ocr') / f"{datetime.utcnow().timestamp()}_{file.filename}"
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                
                content = await file.read()
                with open(temp_path, 'wb') as f:
                    f.write(content)
                
                # 处理图像
                result = ocr_processor.process_document(str(temp_path))
                results.append({
                    "filename": file.filename,
                    "status": result['status'],
                    "data": result
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "total": len(files),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"批量处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")


@router.get("/ocr/quality-check")
async def check_image_quality(image_path: str = Query(...)):
    """
    检查图像质量
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        质量评估结果
    """
    try:
        ocr_processor = AdvancedOCRProcessor()
        
        # 加载和评估
        import cv2
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("无法读取图像")
        
        quality = ocr_processor.quality_assessor.assess_quality(image)
        
        return {
            "status": "success",
            "image_path": image_path,
            "quality": quality,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"质量检查失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"质量检查失败: {str(e)}")


@router.post("/ocr/detect-handwriting")
async def detect_handwriting(file: UploadFile = File(...)):
    """
    检测图像中的手写内容
    
    Args:
        file: 上传的图像文件
        
    Returns:
        手写检测结果
    """
    try:
        # 保存临时文件
        temp_path = Path('temp_ocr') / f"{datetime.utcnow().timestamp()}_{file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # 检测手写
        ocr_processor = AdvancedOCRProcessor()
        import cv2
        image = cv2.imread(str(temp_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("无法读取图像")
        
        is_handwritten, confidence = ocr_processor.handwriting_detector.detect_handwriting(image)
        
        return {
            "status": "success",
            "filename": file.filename,
            "is_handwritten": is_handwritten,
            "confidence": round(confidence, 3),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"手写检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.get("/ocr/health")
async def ocr_health():
    """OCR模块健康检查"""
    return {
        "status": "healthy",
        "ocr_enabled": True,
        "supported_formats": ["PNG", "JPG", "JPEG", "GIF", "BMP", "TIFF", "PDF"],
        "timestamp": datetime.utcnow().isoformat()
    }
