"""
报表导出模块 - 支持CSV和Excel格式
"""
import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from typing import Dict, List
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ReportExporter:
    """报表导出器"""
    
    @staticmethod
    def export_to_csv(data: Dict, filename: str = None) -> str:
        """
        导出报表为CSV格式
        
        Args:
            data: 报表数据
            filename: 输出文件名
            
        Returns:
            CSV字符串或文件路径
        """
        if filename is None:
            filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = StringIO()
        writer = csv.writer(output)
        
        # 报表头信息
        writer.writerow(['报表类型', data.get('report_type', 'unknown')])
        writer.writerow(['生成时间', data.get('generated_at', '')])
        writer.writerow([])
        
        # 根据报表类型导出不同内容
        if data.get('report_type') == 'daily':
            ReportExporter._export_daily_csv(writer, data)
        elif data.get('report_type') == 'monthly':
            ReportExporter._export_monthly_csv(writer, data)
        elif data.get('report_type') == 'custom':
            ReportExporter._export_custom_csv(writer, data)
        elif data.get('report_type') == 'summary':
            ReportExporter._export_summary_csv(writer, data)
        
        csv_content = output.getvalue()
        
        # 保存文件
        Path('reports').mkdir(parents=True, exist_ok=True)
        filepath = Path('reports') / filename
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(csv_content)
        
        return str(filepath)
    
    @staticmethod
    def _export_daily_csv(writer, data: Dict):
        """导出日报表CSV"""
        daily_stats = data.get('daily_stats', {})
        
        writer.writerow(['日期', daily_stats.get('date', '')])
        writer.writerow(['总票据数', daily_stats.get('total_invoices', 0)])
        writer.writerow([])
        
        # 状态明细
        writer.writerow(['处理状态', '数量'])
        for status, count in daily_stats.get('status_breakdown', {}).items():
            writer.writerow([status, count])
        writer.writerow([])
        
        # 金额明细
        writer.writerow(['金额类型', '金额（元）'])
        amount_summary = daily_stats.get('amount_summary', {})
        for key, value in amount_summary.items():
            writer.writerow([key, f"{value:.2f}"])
    
    @staticmethod
    def _export_monthly_csv(writer, data: Dict):
        """导出月报表CSV"""
        writer.writerow(['月份', f"{data.get('year')}-{data.get('month'):02d}"])
        writer.writerow([])
        
        # 月度统计
        range_stats = data.get('range_stats', {})
        writer.writerow(['总票据数', range_stats.get('total_invoices', 0)])
        writer.writerow([])
        
        # 金额汇总
        writer.writerow(['金额类型', '金额（元）'])
        amount_summary = range_stats.get('amount_summary', {})
        for key, value in amount_summary.items():
            writer.writerow([key, f"{value:.2f}"])
        writer.writerow([])
        
        # 交款人排名
        writer.writerow(['交款人排名'])
        writer.writerow(['排名', '交款人', '票据数', '总金额', '平均金额'])
        for idx, payer in enumerate(data.get('top_payers', []), 1):
            writer.writerow([
                idx,
                payer.get('payer_name'),
                payer.get('invoice_count'),
                f"{payer.get('total_amount', 0):.2f}",
                f"{payer.get('avg_amount', 0):.2f}",
            ])
        writer.writerow([])
        
        # 金额分布
        writer.writerow(['金额分布'])
        writer.writerow(['金额范围', '数量'])
        for range_name, count in data.get('amount_distribution', {}).items():
            writer.writerow([range_name, count])
    
    @staticmethod
    def _export_custom_csv(writer, data: Dict):
        """导出自定义报表CSV"""
        writer.writerow(['开始日期', data.get('start_date')])
        writer.writerow(['结束日期', data.get('end_date')])
        writer.writerow([])
        
        range_stats = data.get('range_stats', {})
        writer.writerow(['总票据数', range_stats.get('total_invoices', 0)])
        writer.writerow(['时间段', f"{data.get('start_date')} 至 {data.get('end_date')}"])
        writer.writerow([])
        
        # 金额统计
        writer.writerow(['金额统计'])
        writer.writerow(['项目', '金额（元）'])
        amount_summary = range_stats.get('amount_summary', {})
        for key, value in amount_summary.items():
            writer.writerow([key, f"{value:.2f}"])
    
    @staticmethod
    def _export_summary_csv(writer, data: Dict):
        """导出总结报表CSV"""
        writer.writerow(['综合总结报表'])
        writer.writerow([])
        
        # 全部统计
        writer.writerow(['全部数据统计'])
        total_summary = data.get('total_summary', {})
        for key, value in total_summary.items():
            if key.endswith('amount'):
                writer.writerow([key, f"{value:.2f}"])
            else:
                writer.writerow([key, value])
        writer.writerow([])
        
        # 状态分布
        writer.writerow(['处理状态分布'])
        writer.writerow(['状态', '数量'])
        for status, count in data.get('status_breakdown', {}).items():
            writer.writerow([status, count])
    
    @staticmethod
    def export_to_excel(data: Dict, filename: str = None) -> str:
        """
        导出报表为Excel格式
        
        Args:
            data: 报表数据
            filename: 输出文件名
            
        Returns:
            Excel文件路径
        """
        if not OPENPYXL_AVAILABLE:
            raise ImportError("需要安装openpyxl: pip install openpyxl")
        
        if filename is None:
            filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "报表"
        
        # 设置样式
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # 报表标题
        title_cell = ws['A1']
        title_cell.value = f"医疗票据{data.get('report_type', '').upper()}报表"
        title_cell.font = Font(size=14, bold=True)
        ws.merge_cells('A1:D1')
        
        # 生成时间
        ws['A2'] = f"生成时间: {data.get('generated_at', '')}"
        
        row = 4
        
        # 根据报表类型导出
        if data.get('report_type') == 'daily':
            row = ReportExporter._export_daily_excel(ws, data, row, header_fill, header_font, border)
        elif data.get('report_type') == 'monthly':
            row = ReportExporter._export_monthly_excel(ws, data, row, header_fill, header_font, border)
        elif data.get('report_type') == 'summary':
            row = ReportExporter._export_summary_excel(ws, data, row, header_fill, header_font, border)
        
        # 调整列宽
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        
        # 保存文件
        Path('reports').mkdir(parents=True, exist_ok=True)
        filepath = Path('reports') / filename
        wb.save(filepath)
        
        return str(filepath)
    
    @staticmethod
    def _export_daily_excel(ws, data: Dict, start_row: int, header_fill, header_font, border) -> int:
        """导出日报表到Excel"""
        daily_stats = data.get('daily_stats', {})
        row = start_row
        
        # 基本信息
        ws[f'A{row}'] = '日期'
        ws[f'B{row}'] = daily_stats.get('date', '')
        row += 1
        ws[f'A{row}'] = '总票据数'
        ws[f'B{row}'] = daily_stats.get('total_invoices', 0)
        row += 2
        
        # 状态明细
        ws[f'A{row}'] = '处理状态'
        ws[f'B{row}'] = '数量'
        for cell in [ws[f'A{row}'], ws[f'B{row}']]:
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        
        for status, count in daily_stats.get('status_breakdown', {}).items():
            ws[f'A{row}'] = status
            ws[f'B{row}'] = count
            row += 1
        
        row += 1
        
        # 金额明细
        ws[f'A{row}'] = '金额类型'
        ws[f'B{row}'] = '金额（元）'
        for cell in [ws[f'A{row}'], ws[f'B{row}']]:
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        
        amount_summary = daily_stats.get('amount_summary', {})
        for key, value in amount_summary.items():
            ws[f'A{row}'] = key
            ws[f'B{row}'] = value
            ws[f'B{row}'].number_format = '0.00'
            row += 1
        
        return row
    
    @staticmethod
    def _export_monthly_excel(ws, data: Dict, start_row: int, header_fill, header_font, border) -> int:
        """导出月报表到Excel"""
        row = start_row
        
        # 月份信息
        ws[f'A{row}'] = '统计月份'
        ws[f'B{row}'] = f"{data.get('year')}-{data.get('month'):02d}"
        row += 2
        
        range_stats = data.get('range_stats', {})
        ws[f'A{row}'] = '总票据数'
        ws[f'B{row}'] = range_stats.get('total_invoices', 0)
        row += 2
        
        # 金额汇总
        ws[f'A{row}'] = '金额类型'
        ws[f'B{row}'] = '金额（元）'
        for cell in [ws[f'A{row}'], ws[f'B{row}']]:
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        
        amount_summary = range_stats.get('amount_summary', {})
        for key, value in amount_summary.items():
            ws[f'A{row}'] = key
            ws[f'B{row}'] = value
            ws[f'B{row}'].number_format = '0.00'
            row += 1
        
        row += 1
        
        # 交款人排名
        ws[f'A{row}'] = '排名'
        ws[f'B{row}'] = '交款人'
        ws[f'C{row}'] = '票据数'
        ws[f'D{row}'] = '总金额'
        for cell in [ws[f'A{row}'], ws[f'B{row}'], ws[f'C{row}'], ws[f'D{row}']]:
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        
        for idx, payer in enumerate(data.get('top_payers', []), 1):
            ws[f'A{row}'] = idx
            ws[f'B{row}'] = payer.get('payer_name')
            ws[f'C{row}'] = payer.get('invoice_count')
            ws[f'D{row}'] = payer.get('total_amount', 0)
            ws[f'D{row}'].number_format = '0.00'
            row += 1
        
        return row
    
    @staticmethod
    def _export_summary_excel(ws, data: Dict, start_row: int, header_fill, header_font, border) -> int:
        """导出总结报表到Excel"""
        row = start_row
        
        # 全部统计
        ws[f'A{row}'] = '全部数据统计'
        ws[f'A{row}'].font = Font(bold=True, size=12)
        row += 1
        
        total_summary = data.get('total_summary', {})
        for key, value in total_summary.items():
            ws[f'A{row}'] = key
            ws[f'B{row}'] = value
            if key.endswith('amount'):
                ws[f'B{row}'].number_format = '0.00'
            row += 1
        
        row += 1
        
        # 状态分布
        ws[f'A{row}'] = '处理状态分布'
        ws[f'B{row}'] = '数量'
        for cell in [ws[f'A{row}'], ws[f'B{row}']]:
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        
        for status, count in data.get('status_breakdown', {}).items():
            ws[f'A{row}'] = status
            ws[f'B{row}'] = count
            row += 1
        
        return row
    
    @staticmethod
    def export_to_json(data: Dict, filename: str = None) -> str:
        """
        导出报表为JSON格式
        
        Args:
            data: 报表数据
            filename: 输出文件名
            
        Returns:
            JSON文件路径
        """
        if filename is None:
            filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        Path('reports').mkdir(parents=True, exist_ok=True)
        filepath = Path('reports') / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
