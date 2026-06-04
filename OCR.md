## OCR增强功能文档

### 概述

Medical Invoice System 现已集成高级OCR增强功能，支持：
- 📷 图像OCR处理
- 📄 扫描PDF识别
- 🖊️ 手写内容检测
- ⚙️ 图像预处理和优化
- 🎯 质量评估

---

## 核心功能

### 1. 图像预处理 (ImagePreprocessor)

自动优化图像质量以提高OCR准确度。

**功能:**
- 灰度转换
- 去噪处理
- 倾斜校正
- 对比度增强
- 自适应阈值处理
- 图像放大

**使用示例:**
```python
from app.ocr_engine import ImagePreprocessor

# 完整预处理管道
processed_image = ImagePreprocessor.preprocess_pipeline('image.png')

# 单步操作
gray = ImagePreprocessor.convert_to_grayscale(image)
denoised = ImagePreprocessor.denoise(gray)
enhanced = ImagePreprocessor.enhance_contrast(denoised)
```

### 2. OCR引擎 (OCREngine)

使用Tesseract OCR进行文本识别。

**支持语言:**
- 简体中文
- 英文
- 混合（中英文）

**使用示例:**
```python
from app.ocr_engine import OCREngine

# 提取文本
text = OCREngine.extract_text(image, language='mixed')

# 提取文本+置信度
result = OCREngine.extract_text_with_confidence(image)
print(f"文本: {result['text']}")
print(f"平均置信度: {result['avg_confidence']}%")

# 从特定区域提取
regions = [
    ('invoice_no', 10, 20, 100, 40),
    ('amount', 10, 100, 100, 120)
]
region_results = OCREngine.extract_regions(image, regions)
```

### 3. 手写检测 (HandwritingDetector)

检测图像中是否包含手写内容。

**返回:**
- `is_handwritten`: 是否为手写
- `confidence`: 置信度（0-1）

**使用示例:**
```python
from app.ocr_engine import HandwritingDetector

is_handwritten, confidence = HandwritingDetector.detect_handwriting(image)
print(f"是手写: {is_handwritten}, 置信度: {confidence:.2%}")
```

### 4. 质量评估 (QualityAssessment)

评估图像质量并给出改进建议。

**评估指标:**
- 清晰度（拉普拉斯方差）
- 亮度
- 对比度
- 噪声水平
- 综合质量评分（0-100）

**使用示例:**
```python
from app.ocr_engine import QualityAssessment

quality = QualityAssessment.assess_quality(image)
print(f"综合评分: {quality['overall_score']}/100")
print(f"清晰度: {quality['sharpness']}")
print(f"亮度: {quality['brightness']}")
print(f"对比度: {quality['contrast']}")
print(f"噪声水平: {quality['noise_level']}")
print(f"质量达标: {quality['is_quality']}")
```

### 5. 高级OCR处理器 (AdvancedOCRProcessor)

综合处理流程，集成所有功能。

**使用示例:**
```python
from app.ocr_engine import AdvancedOCRProcessor

processor = AdvancedOCRProcessor()

# 处理单个文档
result = processor.process_document('image.png')

# 批量处理
results = processor.process_batch(['image1.png', 'image2.png'])

# 保存预处理后的图像
output_path = processor.save_processed_image('image.png')
```

### 6. PDF OCR处理 (PDFOCRProcessor)

处理PDF票据。

**功能:**
- 将PDF转换为图像
- 处理扫描PDF
- 处理混合类型PDF

**使用示例:**
```python
from app.pdf_ocr import PDFOCRProcessor

pdf_processor = PDFOCRProcessor()

# 处理扫描的PDF
result = pdf_processor.process_scanned_pdf('ticket.pdf')

# 处理混合类型PDF（文本+扫描）
result = pdf_processor.process_mixed_pdf('ticket.pdf')
```

### 7. OCR增强发票解析 (OCREnhancedInvoiceParser)

结合OCR和发票解析的完整方案。

**特性:**
- 先尝试直接解析
- 失败时自动使用OCR
- 从OCR文本中提取结构化数据

**使用示例:**
```python
from app.pdf_ocr import OCREnhancedInvoiceParser

parser = OCREnhancedInvoiceParser()

# 使用OCR增强解析
result = parser.parse_invoice_with_ocr('ticket.pdf')
print(f"票据号: {result['invoice_number']}")
print(f"交款人: {result['payer_name']}")
print(f"医保支付: {result['medical_insurance']}")
print(f"OCR质量: {result['ocr_quality']}")
```

---

## API端点

### 1. 处理单个图像

```
POST /api/ocr/process-image
Content-Type: multipart/form-data

参数:
- file: 图像文件

返回示例:
{
  "status": "success",
  "data": {
    "status": "success",
    "image_path": "temp_ocr/1234567890.png",
    "quality_assessment": {
      "overall_score": 78.5,
      "sharpness": 150.3,
      "brightness": 180.5,
      "contrast": 75.2,
      "noise_level": 0.15,
      "is_quality": true
    },
    "handwriting_detection": {
      "is_handwritten": false,
      "confidence": 0.15
    },
    "ocr_result": {
      "text": "票据内容...",
      "avg_confidence": 92.5,
      "words": 150,
      "total_words": 160
    }
  }
}
```

### 2. 处理扫描的PDF

```
POST /api/ocr/process-scanned-pdf
Content-Type: multipart/form-data

参数:
- file: PDF文件

返回示例:
{
  "status": "success",
  "data": {
    "status": "success",
    "pdf_path": "temp_ocr/ticket.pdf",
    "page_count": 2,
    "combined_text": "合并的文本内容...",
    "average_quality": 82.3,
    "page_results": [...]
  }
}
```

### 3. 处理混合类型PDF

```
POST /api/ocr/process-mixed-pdf
Content-Type: multipart/form-data

参数:
- file: PDF文件

返回:
自动检测并使用合适的处理方法
```

### 4. OCR增强发票解析

```
POST /api/ocr/parse-invoice?use_ocr_fallback=true
Content-Type: multipart/form-data

参数:
- file: PDF文件
- use_ocr_fallback: 是否使用OCR备选方案
```

### 5. 批量处理图像

```
POST /api/ocr/batch-process-images
Content-Type: multipart/form-data

参数:
- files: 多个图像文件

返回:
{
  "status": "completed",
  "total": 3,
  "results": [
    {
      "filename": "image1.png",
      "status": "success",
      "data": {...}
    },
    ...
  ]
}
```

### 6. 质量检查

```
GET /api/ocr/quality-check?image_path=/path/to/image.png

返回:
{
  "status": "success",
  "image_path": "/path/to/image.png",
  "quality": {
    "overall_score": 75.5,
    "is_quality": true
  }
}
```

### 7. 手写检测

```
POST /api/ocr/detect-handwriting
Content-Type: multipart/form-data

参数:
- file: 图像文件

返回:
{
  "status": "success",
  "filename": "image.png",
  "is_handwritten": true,
  "confidence": 0.85
}
```

### 8. 健康检查

```
GET /api/ocr/health

返回:
{
  "status": "healthy",
  "ocr_enabled": true,
  "supported_formats": ["PNG", "JPG", "JPEG", "GIF", "BMP", "TIFF", "PDF"]
}
```

---

## 环境配置

### 系统依赖

**Ubuntu/Debian:**
```bash
sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
- 下载并安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- 下载并安装 [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/)

### Python依赖

```bash
pip install -r requirements.txt
```

关键库：
- `pytesseract` - Tesseract的Python接口
- `opencv-python` - 图像处理
- `pdf2image` - PDF转图像
- `pdfplumber` - PDF文本提取

---

## 使用场景

### 场景1：处理扫描的医疗票据

```python
from app.pdf_ocr import OCREnhancedInvoiceParser

parser = OCREnhancedInvoiceParser()

# 处理扫描的PDF（自动降级到OCR）
result = parser.parse_invoice_with_ocr('scanned_ticket.pdf')

if result['is_valid']:
    print("票据识别成功")
    print(f"质量评分: {result['ocr_quality']}")
else:
    print("识别失败:", result['error'])
```

### 场景2：批量处理多张票据

```python
from app.ocr_engine import AdvancedOCRProcessor
import glob

processor = AdvancedOCRProcessor()

# 获取所有图像文件
image_files = glob.glob('tickets/*.png')

# 批量处理
results = processor.process_batch(image_files)

# 统计结果
successful = sum(1 for r in results if r['status'] == 'success')
print(f"成功处理: {successful}/{len(results)}")
```

### 场景3：质量控制

```python
from app.ocr_engine import QualityAssessment

quality = QualityAssessment.assess_quality(image)

if quality['is_quality']:
    print("图像质量达标，可进行OCR")
else:
    print("建议改进:")
    print(f"- 清晰度较低: {quality['sharpness']}")
    print(f"- 亮度不足: {quality['brightness']}")
    print(f"- 噪声过多: {quality['noise_level']}")
```

---

## 性能优化

### 1. 使用较低分辨率

```python
# 较低分辨率更快，但可能降低准确度
pdf_processor.pdf_to_images('ticket.pdf', dpi=150)
```

### 2. 缓存预处理结果

```python
# 保存预处理后的图像，避免重复处理
processor.save_processed_image('image.png')
```

### 3. 异步处理

```python
# 在Celery中使用批量处理
from celery import shared_task

@shared_task
def process_batch_task(image_paths):
    processor = AdvancedOCRProcessor()
    return processor.process_batch(image_paths)
```

---

## 常见问题

**Q: 如何提高OCR准确度？**

A: 
1. 使用高质量图像（DPI ≥ 300）
2. 使用预处理管道增强对比度
3. 使用合适的语言配置

**Q: 支持哪些文件格式？**

A: 图像格式：PNG、JPG、JPEG、GIF、BMP、TIFF；PDF格式：标准PDF

**Q: 如何处理超大PDF？**

A: 使用批处理和异步任务，配合内存管理

**Q: 手写检测的准确度如何？**

A: 大约 80-85%，仅用于初步判断，需人工确认

---

**最后更新**: 2024年
**维护者**: bomice
