"""
数据验证模块
"""
import re
from datetime import datetime
from typing import Dict, List, Tuple


class InvoiceValidator:
    """票据数据验证器"""
    
    @staticmethod
    def validate_invoice_number(invoice_number: str) -> Tuple[bool, str]:
        """
        验证票据号码
        
        Args:
            invoice_number: 票据号码
            
        Returns:
            (有效性, 错误消息)
        """
        if not invoice_number:
            return False, "票据号码不能为空"
        
        if len(invoice_number) < 10:
            return False, "票据号码格式不正确（长度过短）"
        
        if not re.match(r'^[A-Z0-9]+$', invoice_number):
            return False, "票据号码包含非法字符"
        
        return True, ""
    
    @staticmethod
    def validate_payer_name(payer_name: str) -> Tuple[bool, str]:
        """
        验证交款人信息
        
        Args:
            payer_name: 交款人名称
            
        Returns:
            (有效性, 错误消息)
        """
        if not payer_name:
            return False, "交款人不能为空"
        
        if len(payer_name) < 2:
            return False, "交款人名称过短"
        
        if len(payer_name) > 100:
            return False, "交款人名称过长"
        
        return True, ""
    
    @staticmethod
    def validate_amount(amount: float, field_name: str) -> Tuple[bool, str]:
        """
        验证金额
        
        Args:
            amount: 金额值
            field_name: 字段名称
            
        Returns:
            (有效性, 错误消息)
        """
        if amount < 0:
            return False, f"{field_name}不能为负数"
        
        if amount > 100000:
            return False, f"{field_name}异常高（> 10万元）"
        
        # 检查小数位数
        if len(str(amount).split('.')[-1]) > 2:
            return False, f"{field_name}小数位数过多"
        
        return True, ""
    
    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        """
        验证日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            (有效性, 错误消息)
        """
        if not date_str:
            return False, "日期不能为空"
        
        formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S']
        
        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True, ""
            except ValueError:
                continue
        
        return False, f"日期格式不正确: {date_str}"
    
    @staticmethod
    def validate_invoice_data(data: Dict) -> Tuple[bool, List[str]]:
        """
        验证完整的票据数据
        
        Args:
            data: 票据数据字典
            
        Returns:
            (有效性, 错误消息列表)
        """
        errors = []
        
        # 验证票据号码
        valid, msg = InvoiceValidator.validate_invoice_number(data.get('invoice_number', ''))
        if not valid:
            errors.append(msg)
        
        # 验证交款人
        valid, msg = InvoiceValidator.validate_payer_name(data.get('payer_name', ''))
        if not valid:
            errors.append(msg)
        
        # 验证各金额字段
        amount_fields = [
            ('self_payment_1', '自付一'),
            ('self_payment_2', '自付二'),
            ('other_payment', '其他支付'),
            ('personal_out_of_pocket', '个人自费'),
            ('annual_medical_insurance', '年度医保范围内'),
            ('medical_insurance', '医保范围内'),
        ]
        
        for field_key, field_name in amount_fields:
            amount = data.get(field_key, 0)
            valid, msg = InvoiceValidator.validate_amount(amount, field_name)
            if not valid:
                errors.append(msg)
        
        # 验证总金额
        total = (
            data.get('self_payment_1', 0) +
            data.get('self_payment_2', 0) +
            data.get('other_payment', 0) +
            data.get('personal_out_of_pocket', 0) +
            data.get('medical_insurance', 0)
        )
        
        if total <= 0:
            errors.append("总金额必须大于0")
        
        # 验证日期（如果提供）
        if data.get('invoice_date'):
            valid, msg = InvoiceValidator.validate_date(data.get('invoice_date'))
            if not valid:
                errors.append(msg)
        
        return len(errors) == 0, errors


def validate_and_clean(data: Dict) -> Dict:
    """
    验证并清洁数据
    
    Args:
        data: 原始数据字典
        
    Returns:
        清洁后的数据字典
    """
    cleaned = {}
    
    # 清洁字符串字段
    string_fields = ['invoice_number', 'payer_name', 'invoice_date']
    for field in string_fields:
        value = data.get(field, '')
        cleaned[field] = str(value).strip() if value else None
    
    # 清洁金额字段
    amount_fields = [
        'self_payment_1', 'self_payment_2', 'other_payment',
        'personal_out_of_pocket', 'annual_medical_insurance', 'medical_insurance'
    ]
    
    for field in amount_fields:
        value = data.get(field, 0)
        try:
            cleaned[field] = float(value) if value else 0.0
        except (ValueError, TypeError):
            cleaned[field] = 0.0
    
    return cleaned
