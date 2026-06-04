"""
测试 - 统计模块
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Invoice, InvoiceStatus
from app.statistics import InvoiceStatistics, ReportGenerator


@pytest.fixture
def test_db():
    """创建测试数据库"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 创建测试数据
    test_invoices = [
        Invoice(
            invoice_number=f"BJ202401{str(i):02d}",
            payer_name=f"交款人{i}",
            self_payment_1=100.0 * i,
            self_payment_2=50.0 * i,
            other_payment=0.0,
            personal_out_of_pocket=0.0,
            medical_insurance=200.0 * i,
            total_amount=350.0 * i,
            invoice_date=datetime.utcnow(),
            status=InvoiceStatus.COMPLETED,
        )
        for i in range(1, 6)
    ]
    
    for invoice in test_invoices:
        session.add(invoice)
    session.commit()
    
    yield session
    session.close()


class TestInvoiceStatistics:
    """测试票据统计���"""
    
    def test_get_daily_stats(self, test_db):
        """测试获取日统计"""
        stats = InvoiceStatistics.get_daily_stats(test_db)
        
        assert stats['total_invoices'] == 5
        assert 'status_breakdown' in stats
        assert 'amount_summary' in stats
        assert stats['amount_summary']['total_amount'] > 0
    
    def test_get_daily_stats_specific_date(self, test_db):
        """测试指定日期的日统计"""
        target_date = (datetime.utcnow() - timedelta(days=1)).date()
        stats = InvoiceStatistics.get_daily_stats(test_db, target_date)
        
        assert stats['date'] == target_date.isoformat()
        assert stats['total_invoices'] == 0  # 昨天没有数据
    
    def test_get_top_payers(self, test_db):
        """测试获取交款人排名"""
        payers = InvoiceStatistics.get_top_payers(test_db, limit=3)
        
        assert len(payers) <= 3
        assert all('payer_name' in p for p in payers)
        assert all('total_amount' in p for p in payers)
        
        # 验证排序
        if len(payers) > 1:
            assert payers[0]['total_amount'] >= payers[1]['total_amount']
    
    def test_get_amount_distribution(self, test_db):
        """测试获取金额分布"""
        distribution = InvoiceStatistics.get_amount_distribution(test_db)
        
        assert isinstance(distribution, dict)
        assert sum(distribution.values()) == 5  # 总共5张票据
    
    def test_get_status_summary(self, test_db):
        """测试获取状态总结"""
        summary = InvoiceStatistics.get_status_summary(test_db)
        
        assert 'completed' in summary
        assert summary['completed']['count'] == 5
        assert 0 <= summary['completed']['percentage'] <= 100


class TestReportGenerator:
    """测试报表生成器"""
    
    def test_generate_daily_report(self, test_db):
        """测试生成日报表"""
        report = ReportGenerator.generate_daily_report(test_db)
        
        assert report['report_type'] == 'daily'
        assert 'daily_stats' in report
        assert 'status_summary' in report
    
    def test_generate_monthly_report(self, test_db):
        """测试生成月报表"""
        now = datetime.utcnow()
        report = ReportGenerator.generate_monthly_report(test_db, now.year, now.month)
        
        assert report['report_type'] == 'monthly'
        assert report['year'] == now.year
        assert report['month'] == now.month
        assert 'top_payers' in report
        assert 'amount_distribution' in report
    
    def test_generate_summary_report(self, test_db):
        """测试生成总结报表"""
        report = ReportGenerator.generate_summary_report(test_db)
        
        assert report['report_type'] == 'summary'
        assert 'total_summary' in report
        assert 'status_breakdown' in report
        assert report['total_summary']['total_invoices'] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
