# Medical Invoice System

北京市门诊医疗票据自动化处理系统

## 功能概述

- ✅ PDF票据批量上传和处理
- ✅ 结构化数据自动提取（固定格式票据）
- ✅ 数据验证和清洗
- ✅ 数据库存储和查询
- ✅ REST API接口
- ✅ Web管理后台
- ✅ 数据统计和报表

## 项目结构

```
medical-invoice-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Flask/FastAPI主程序
│   ├── config.py               # 配置文件
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   └── invoice.py
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── pdf_parser.py       # PDF解析
│   │   ├── data_validator.py   # 数据验证
│   │   └── invoice_service.py  # 票据服务
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── test_pdf_parser.py
│   └── test_data_validator.py
├── requirements.txt            # 依赖文件
├── .env.example               # 环境变量示例
├── docker-compose.yml         # Docker配置
├── Dockerfile                 # Docker镜像配置
└── README.md
```

## 快速开始

### 本地开发

1. 克隆仓库
```bash
git clone https://github.com/bomice/medical-invoice-system.git
cd medical-invoice-system
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

5. 初始化数据库
```bash
python -m app.main init-db
```

6. 运行应用
```bash
python -m app.main run
```

### Docker部署

```bash
docker-compose up -d
```

## API文档

### 上传票据

```
POST /api/invoices/upload
Content-Type: multipart/form-data

- file: PDF文件
- batch_id: 批次ID（可选）
```

### 查询票据

```
GET /api/invoices?page=1&per_page=20
```

### 获取统计数据

```
GET /api/invoices/stats
```

## 关键字段说明

| 字段 | 说明 |
|------|------|
| 自付一 | 医保范围内自付部分 |
| 自付二 | 医保范围外自付部分 |
| 其他支付 | 其他支付方式 |
| 个人自费 | 个人完全自费部分 |
| 年度医保范围内 | 年度医保支付额 |
| 医保范围内 | 单次医保支付额 |
| 票据号码 | 唯一标识符 |
| 交款人 | 支付人信息 |

## 技术栈

- **后端**: Python 3.9+, FastAPI
- **数据库**: PostgreSQL 12+
- **PDF处理**: pdfplumber, PyPDF2
- **任务队列**: Celery + Redis
- **前端**: Vue.js 3 (可选)
- **容器化**: Docker, Docker Compose

## 贡献指南

欢迎提交Issue和PR！

## 许可证

MIT License
