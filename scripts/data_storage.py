"""
数据存储模块 - 支持JSON格式存储每日数据
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class DataStorage:
    """数据存储管理类"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.data_dir = os.path.join(project_root, 'data')
        self.raw_dir = os.path.join(self.data_dir, 'raw')
        self.processed_dir = os.path.join(self.data_dir, 'processed')
        
        # 确保目录存在
        for dir_path in [self.data_dir, self.raw_dir, self.processed_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def save_daily_data(self, date: str, data: Dict[str, Any]) -> str:
        """
        保存每日原始数据
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)
            data: 包含所有数据的字典
        
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(self.raw_dir, f'{date}.json')
        
        # 添加元数据
        data_with_meta = {
            'date': date,
            'created_at': datetime.now().isoformat(),
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_with_meta, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存: {filepath}")
        return filepath
    
    def load_daily_data(self, date: str) -> Optional[Dict[str, Any]]:
        """
        加载指定日期的数据
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)
        
        Returns:
            数据字典，如果不存在返回None
        """
        filepath = os.path.join(self.raw_dir, f'{date}.json')
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_date_range_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取指定日期范围内的所有数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            数据列表
        """
        data_list = []
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            data = self.load_daily_data(date_str)
            if data:
                data_list.append(data)
            current += timedelta(days=1)
        
        return data_list
    
    def get_week_data(self, year: int, week: int) -> List[Dict[str, Any]]:
        """
        获取指定周的所有数据
        
        Args:
            year: 年份
            week: 周数 (1-53)，使用ISO标准
        
        Returns:
            数据列表
        """
        # 使用ISO标准计算周的起始和结束日期
        # ISO周从周一开始
        jan1 = datetime(year, 1, 1)
        
        # 获取1月1日所在的ISO周
        iso_year, iso_week, iso_weekday = jan1.isocalendar()
        
        # 计算目标周的起始日期（周一）
        # 如果1月1日不是周一，需要调整到上一年的最后一周或当前周的第一天
        if iso_weekday != 1:
            # 1月1日不是周一，计算当前周的第一天
            days_to_monday = iso_weekday - 1
            week_start = jan1 - timedelta(days=days_to_monday)
        else:
            week_start = jan1
        
        # 计算目标周的起始日期
        week_start = week_start + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        # 获取这周的数据
        return self.get_date_range_data(
            week_start.strftime('%Y-%m-%d'),
            week_end.strftime('%Y-%m-%d')
        )
    
    def get_month_data(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        获取指定月的所有数据
        
        Args:
            year: 年份
            month: 月份 (1-12)
        
        Returns:
            数据列表
        """
        # 计算月的起始和结束日期
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_date_range_data(
            month_start.strftime('%Y-%m-%d'),
            month_end.strftime('%Y-%m-%d')
        )
    
    def get_all_dates(self) -> List[str]:
        """
        获取所有已存储数据的日期列表
        
        Returns:
            日期字符串列表（按时间倒序）
        """
        dates = []
        
        if os.path.exists(self.raw_dir):
            for filename in os.listdir(self.raw_dir):
                if filename.endswith('.json'):
                    date_str = filename.replace('.json', '')
                    dates.append(date_str)
        
        return sorted(dates, reverse=True)
    
    def check_report_exists(self, report_type: str, identifier: str) -> bool:
        """
        检查报告是否已生成
        
        Args:
            report_type: 报告类型 ('weekly' 或 'monthly')
            identifier: 标识符 (如 '2026-W09' 或 '2026-03')
        
        Returns:
            是否存在
        """
        docs_dir = os.path.join(self.project_root, 'docs', report_type)
        filepath = os.path.join(docs_dir, f'{identifier}.md')
        return os.path.exists(filepath)


if __name__ == '__main__':
    # 测试代码
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    storage = DataStorage(project_root)
    
    # 测试保存数据
    test_data = {
        'model_ranking': 'test ranking',
        'model_news': ['news1', 'news2'],
        'open_source_apps': ['app1', 'app2'],
        'successful_cases': ['case1', 'case2']
    }
    
    storage.save_daily_data('2026-03-04', test_data)
    
    # 测试加载数据
    loaded = storage.load_daily_data('2026-03-04')
    print(f"加载的数据: {loaded}")
