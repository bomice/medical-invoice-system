## 统计和报表功能文档

### 概述

Medical Invoice System 现已支持完整的统计和报表功能，包括：
- 日/月/自定义日期范围统计
- 交款人排名分析
- 金额分布统计
- 多格式报表导出（CSV、Excel、JSON）

---

## 统计功能

### 1. 日统计 (Daily Statistics)

获取指定日期的统计数据。

**API 端点:**
```
GET /api/statistics/daily?date=2024-01-15
```

**返回示例:**
```json
{
  "status": "success",
  "data": {
    "date": "2024-01-15",
    "total_invoices": 150,
    "status_breakdown": {
      "completed": 145,
      "pending": 3,
      "failed": 2,
      "processing": 0,
      "verified": 0
    },
    "amount_summary": {
      "total_amount": 45230.50,
      "self_payment_1": 8500.00,
      "self_payment_2": 4200.00,
      "other_payment": 1200.00,
      "personal_out_of_pocket": 3200.00,
      "medical_insurance": 28130.50
    }
  }
}
```

### 2. 日期范围统计 (Date Range Statistics)

获取指定日期范围内的统计数据。

**API 端点:**
```
GET /api/statistics/date-range?start_date=2024-01-01&end_date=2024-01-31
```

**返回示例:**
```json
{
  "status": "success",
  "data": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "total_invoices": 3500,
    "status_breakdown": { ... },
    "amount_summary": { ... },
    "average_summary": {
      "avg_total_amount": 301.51,
      "avg_medical_insurance": 187.42
    }
  }
}
```

### 3. 趋势数据 (Trend Data)

获取最近N天的日趋势数据。

**API 端点:**
```
GET /api/statistics/trend?days=30
```

**返回示例:**
```json
{
  "status": "success",
  "days": 30,
  "data": [
    {
      "date": "2024-01-01",
      "total_invoices": 120,
      "status_breakdown": { ... },
      "amount_summary": { ... }
    },
    ...
  ]
}
```

### 4. 交款人排名 (Top Payers)

获取金额最多的交款人。

**API 端点:**
```
GET /api/statistics/top-payers?limit=10&days=30
```

**返回示例:**
```json
{
  "status": "success",
  "limit": 10,
  "days": 30,
  "data": [
    {
      "payer_name": "北京市第一医院",
      "invoice_count": 250,
      "total_amount": 125000.00,
      "avg_amount": 500.00
    },
    {
      "payer_name": "北京市第二医院",
      "invoice_count": 200,
      "total_amount": 98000.00,
      "avg_amount": 490.00
    }
  ]
}
```

### 5. 金额分布 (Amount Distribution)

获取不同金额范围的票据数量分布。

**API 端点:**
```
GET /api/statistics/amount-distribution?days=30
```

**返回示例:**
```json
{
  "status": "success",
  "days": 30,
  "data": {
    "0-100": 520,
    "100-500": 1200,
    "500-1000": 800,
    "1000-5000": 450,
    ">5000": 30
  }
}
```

### 6. 状态总结 (Status Summary)

获取处理状态的统计总结。

**API 端点:**
```
GET /api/statistics/status-summary?days=30
```

**返回示例:**
```json
{
  "status": "success",
  "days": 30,
  "data": {
    "completed": {
      "count": 2800,
      "percentage": 93.33
    },
    "verified": {
      "count": 150,
      "percentage": 5.00
    },
    "pending": {
      "count": 40,
      "percentage": 1.33
    },
    "processing": {
      "count": 10,
      "percentage": 0.33
    },
    "failed": {
      "count": 0,
      "percentage": 0.00
    }
  }
}
```

---

## 报表功能

### 1. 日报表 (Daily Report)

生成指定日期的完整报表。

**API 端点:**
```
GET /api/reports/daily?date=2024-01-15
```

**包含内容:**
- 日期统计数据
- 处理状态分布
- 金额汇总

### 2. 月报表 (Monthly Report)

生成月份的完整报表，包括趋势和排名。

**API 端点:**
```
GET /api/reports/monthly?year=2024&month=1
```

**包含内容:**
- 月份统计数据
- 日趋势数据
- 交款人排名（TOP 10）
- 金额分布

### 3. 自定义报表 (Custom Report)

生成自定义日期范围的报表。

**API 端点:**
```
GET /api/reports/custom?start_date=2024-01-01&end_date=2024-01-31&include_top_payers=true&include_distribution=true
```

**参数:**
- `start_date`: 开始日期
- `end_date`: 结束日期
- `include_top_payers`: 是否包含交款人排名（默认true）
- `include_distribution`: 是否包含金额分布（默认true）

### 4. 综合总结报表 (Summary Report)

生成包含全部数据和最近30天对比的综合报表。

**API 端点:**
```
GET /api/reports/summary
```

**包含内容:**
- 全部数据统计
- 处理状态分布
- 今日数据
- 最近30天数据

---

## 报表导出

### 导出为CSV格式

**API 端点:**
```
GET /api/reports/export/csv?report_type=monthly&year=2024&month=1
```

**参数:**
- `report_type`: daily / monthly / custom / summary
- 其他参数取决于报表类型

**返回:**
```json
{
  "status": "success",
  "filepath": "reports/report_20240115_143025.csv",
  "format": "csv"
}
```

### 导出为Excel格式

**API 端点:**
```
GET /api/reports/export/excel?report_type=monthly&year=2024&month=1
```

**特性:**
- 包含格式化的表头（蓝色背景、白色字体）
- 自动调整列宽
- 金额字段格式化（保留两位小数）

### 导出为JSON格式

**API 端点:**
```
GET /api/reports/export/json?report_type=summary
```

**优点:**
- 便于数据集成
- 保持完整的数据结构
- 支持进一步处理和分析

---

## 使用示例

### Python 示例

```python
from app.statistics import InvoiceStatistics, ReportGenerator
from datetime import datetime, timedelta

# 获取日统计
daily_stats = InvoiceStatistics.get_daily_stats(session)
print(daily_stats)

# 获取日期范围统计
start = datetime(2024, 1, 1).date()
end = datetime(2024, 1, 31).date()
range_stats = InvoiceStatistics.get_date_range_stats(session, start, end)
print(range_stats)

# 获取交款人排名
top_payers = InvoiceStatistics.get_top_payers(session, limit=10, days=30)
print(top_payers)

# 生成月报表
report = ReportGenerator.generate_monthly_report(session, 2024, 1)
print(report)

# 导出为Excel
from app.report_exporter import ReportExporter
filepath = ReportExporter.export_to_excel(report)
print(f"报表已导出到: {filepath}")
```

### cURL 示例

```bash
# 获取日统计
curl "http://localhost:8000/api/statistics/daily?date=2024-01-15"

# 获取交款人排名
curl "http://localhost:8000/api/statistics/top-payers?limit=10&days=30"

# 生成月报表
curl "http://localhost:8000/api/reports/monthly?year=2024&month=1"

# 导出为CSV
curl "http://localhost:8000/api/reports/export/csv?report_type=monthly&year=2024&month=1" \
  -o report.csv
```

### JavaScript/Fetch 示例

```javascript
// 获取日统计
fetch('/api/statistics/daily?date=2024-01-15')
  .then(res => res.json())
  .then(data => console.log(data))

// 生成月报表并下载
async function downloadMonthlyReport() {
  const response = await fetch('/api/reports/export/excel?report_type=monthly&year=2024&month=1');
  const data = await response.json();
  window.open(data.data.filepath);
}
```

---

## 性能优化建议

1. **使用缓存**
   - 对日报表结果进行缓存，避免重复计算
   - 设置合理的缓存过期时间

2. **数据库索引**
   - 在 `created_at` 字段创建索引
   - 在 `status` 字段创建索引
   - 在 `payer_name` 字段创建索引

3. **异步处理**
   - 对于大规模报表导出，使用Celery后台任务
   - 返回任务ID，用户可查询处理进度

4. **分页查询**
   - 对大量数据的查询使用分页
   - 减少单次查询的数据量

---

## 常见问题

**Q: 如何自定义金额分布范围？**

A: 修改 `app/statistics.py` 中 `get_amount_distribution` 方法的 `ranges` 列表。

**Q: 导出的Excel报表如何添加图表？**

A: 使用 `openpyxl` 的 Chart API，参考官方文档添加图表功能。

**Q: 如何生成定期自动报表？**

A: 使用Celery Beat配合定时任务，定期生成并邮件发送报表。

---

**最后更新**: 2024年
**维护者**: bomice
