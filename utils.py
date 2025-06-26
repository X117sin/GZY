"""
utils - 数据分析智能体使用的工具函数
"""
import json
import pandas as pd
import openpyxl
from typing import List, Dict, Union, Optional
import re
import os
from datetime import datetime
import sqlite3
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

PROMPT_TEMPLATE = """你是一位数据分析助手，你的回应内容取决于用户的请求内容，请按照下面的步骤处理用户请求：
1. 思考阶段 (Thought) ：先分析用户请求类型（文字回答/表格/图表），并验证数据类型是否匹配。
2. 行动阶段 (Action) ：根据分析结果选择以下严格对应的格式。
   - 纯文字回答:
     {"answer": "不超过50个字符的明确答案"}

   - 表格数据：
     {"table":{"columns":["列名1", "列名2", ...], "data":[["第一行值1", "值2", ...], ["第二行值1", "值2", ...]]}}

   - 柱状图
     {"bar":{"columns": ["A", "B", "C", ...], "data":[35, 42, 29, ...]}}

   - 折线图
     {"line":{"columns": ["A", "B", "C", ...], "data": [35, 42, 29, ...]}}
     
3. 格式校验要求
   - 字符串值必须使用英文双引号
   - 数值类型不得添加引号
   - 确保数组闭合无遗漏
   错误案例：{'columns':['Product', 'Sales'], data:[[A001, 200]]}
   正确案例：{"columns":["product", "sales"], "data":[["A001", 200]]}

注意：响应数据的"output"中不要有换行符、制表符以及其他格式符号。

当前用户请求如下：\n"""


def dataframe_agent(df, query, model_config=None, api_key=None):
    """数据分析智能体
    
    Args:
        df: pandas DataFrame
        query: 用户查询
        model_config: 模型配置字典，包含provider, model, base_url等信息
        api_key: 用户输入的API密钥
    """
    # 不再从环境变量加载，使用用户提供的API密钥
    if not api_key:
        return {"answer": "请提供有效的API密钥！"}
    
    # 默认使用DeepSeek模型
    if model_config is None:
        model_config = {
            "provider": "deepseek", 
            "model": "deepseek-reasoner", 
            "base_url": "https://api.deepseek.com/"
        }
    
    try:
        # 根据不同的提供商创建模型实例
        if model_config["provider"] in ["deepseek", "openai"]:
            model = ChatOpenAI(
                base_url=model_config["base_url"],
                model=model_config["model"],
                api_key=api_key,
                temperature=0,
                max_tokens=8192
            )
        elif model_config["provider"] == "anthropic":
            # Claude模型需要不同的配置
            from langchain_anthropic import ChatAnthropic
            model = ChatAnthropic(
                model=model_config["model"],
                api_key=api_key,
                temperature=0,
                max_tokens=8192
            )
        else:
            # 对于其他提供商，暂时使用OpenAI兼容接口
            model = ChatOpenAI(
                base_url=model_config["base_url"],
                model=model_config["model"],
                api_key=api_key,
                temperature=0,
                max_tokens=8192
            )
        
        agent = create_pandas_dataframe_agent(
            llm=model,
            df=df,
            agent_executor_kwargs={"handle_parsing_errors": True},
            max_iterations=32,
            allow_dangerous_code=True,
            verbose=True
        )

        prompt = PROMPT_TEMPLATE + query
        response = agent.invoke({"input": prompt})
        return json.loads(response["output"])
        
    except ImportError as e:
        print(f"模型导入错误: {e}")
        return {"answer": f"当前模型 {model_config['model']} 暂不支持，请选择其他模型或安装相应依赖包！"}
    except Exception as err:
        error_msg = str(err).lower()
        print(f"分析错误: {err}")
        
        # 检查是否是API密钥相关错误
        if any(keyword in error_msg for keyword in ['api key', 'apikey', 'api_key', 'unauthorized', '401', 'authentication', 'invalid key', 'incorrect api key']):
            return {"answer": "❌ API密钥无效或不正确，请检查并重新输入正确的API密钥！"}
        elif any(keyword in error_msg for keyword in ['quota', 'limit', 'billing', 'insufficient']):
            return {"answer": "⚠️ API配额不足或账户余额不够，请检查您的账户状态！"}
        elif any(keyword in error_msg for keyword in ['network', 'connection', 'timeout', 'unreachable']):
            return {"answer": "🌐 网络连接错误，请检查网络连接后重试！"}
        else:
             return {"answer": "暂时无法提供分析结果，请稍后重试或尝试其他模型！"}


def test_api_connection(model_config, api_key):
    """测试API密钥连接
    
    Args:
        model_config: 模型配置字典
        api_key: API密钥
    
    Returns:
        dict: {"success": bool, "error": str}
    """
    try:
        # 根据不同的提供商创建模型实例进行测试
        if model_config["provider"] in ["deepseek", "openai"]:
            model = ChatOpenAI(
                base_url=model_config["base_url"],
                model=model_config["model"],
                api_key=api_key,
                temperature=0,
                max_tokens=10
            )
        elif model_config["provider"] == "anthropic":
            from langchain_anthropic import ChatAnthropic
            model = ChatAnthropic(
                model=model_config["model"],
                api_key=api_key,
                temperature=0,
                max_tokens=10
            )
        else:
            model = ChatOpenAI(
                base_url=model_config["base_url"],
                model=model_config["model"],
                api_key=api_key,
                temperature=0,
                max_tokens=10
            )
        
        # 发送一个简单的测试请求
        response = model.invoke("Hello")
        return {"success": True, "error": ""}
        
    except Exception as e:
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ['api key', 'apikey', 'api_key', 'unauthorized', '401', 'authentication', 'invalid key', 'incorrect api key']):
            return {"success": False, "error": "API密钥无效或不正确"}
        elif any(keyword in error_msg for keyword in ['quota', 'limit', 'billing', 'insufficient']):
            return {"success": False, "error": "API配额不足或账户余额不够"}
        elif any(keyword in error_msg for keyword in ['network', 'connection', 'timeout', 'unreachable']):
            return {"success": False, "error": "网络连接错误"}
        else:
            return {"success": False, "error": f"连接测试失败: {str(e)}"}


def merge_multiple_files(file_list: List[Dict], merge_type: str = "concat") -> pd.DataFrame:
    """合并多个数据文件
    
    Args:
        file_list: 文件列表，每个元素包含 {'file': file_object, 'type': 'excel/csv', 'sheet': sheet_name}
        merge_type: 合并方式 ('concat': 纵向合并, 'join': 横向连接)
    
    Returns:
        pd.DataFrame: 合并后的数据框
    """
    dataframes = []
    
    for file_info in file_list:
        try:
            file_obj = file_info['file']
            file_type = file_info['type']
            
            if file_type == 'excel':
                sheet_name = file_info.get('sheet', 0)
                # 重置文件指针到开始位置
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                
                # 尝试多种引擎读取Excel文件
                df = None
                engines = ['openpyxl', 'xlrd', None]
                
                for engine in engines:
                    try:
                        if hasattr(file_obj, 'seek'):
                            file_obj.seek(0)
                        if engine:
                            df = pd.read_excel(file_obj, sheet_name=sheet_name, engine=engine)
                        else:
                            df = pd.read_excel(file_obj, sheet_name=sheet_name)
                        break
                    except Exception:
                        continue
                
                if df is None:
                    raise Exception(f"无法读取Excel文件，请检查文件格式")
            elif file_type == 'csv':
                # 重置文件指针到开始位置
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                df = pd.read_csv(file_obj)
            else:
                continue
                
            # 添加文件来源标识
            df['数据来源'] = file_obj.name if hasattr(file_obj, 'name') else f"文件{len(dataframes)+1}"
            dataframes.append(df)
            
        except Exception as e:
            print(f"读取文件失败: {e}")
            continue
    
    if not dataframes:
        return pd.DataFrame()
    
    if merge_type == "concat":
        # 纵向合并（追加行）
        return pd.concat(dataframes, ignore_index=True, sort=False)
    elif merge_type == "join":
        # 横向连接（基于索引）
        result = dataframes[0]
        for df in dataframes[1:]:
            result = result.join(df, rsuffix='_merged')
        return result
    else:
        return dataframes[0]


def join_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, 
                   join_column: str, join_type: str = "inner") -> pd.DataFrame:
    """数据表连接功能
    
    Args:
        df1: 左表
        df2: 右表
        join_column: 连接字段
        join_type: 连接类型 ('inner', 'left', 'right', 'outer')
    
    Returns:
        pd.DataFrame: 连接后的数据框
    """
    try:
        if join_column not in df1.columns:
            raise ValueError(f"左表中不存在字段: {join_column}")
        if join_column not in df2.columns:
            raise ValueError(f"右表中不存在字段: {join_column}")
            
        return pd.merge(df1, df2, on=join_column, how=join_type, suffixes=('_左表', '_右表'))
    except Exception as e:
        print(f"数据表连接失败: {e}")
        return df1


def analyze_mixed_format_data(files_data: List[Dict], analysis_query: str, 
                             model_config: Dict = None, api_key: str = None) -> Dict:
    """支持不同格式文件的混合分析
    
    Args:
        files_data: 文件数据列表
        analysis_query: 分析查询
        model_config: 模型配置
        api_key: API密钥
    
    Returns:
        Dict: 分析结果
    """
    try:
        # 合并所有文件数据
        merged_df = merge_multiple_files(files_data, merge_type="concat")
        
        if merged_df.empty:
            return {"answer": "没有有效的数据文件可供分析"}
        
        # 使用现有的数据分析智能体进行分析
        return dataframe_agent(merged_df, analysis_query, model_config, api_key)
        
    except Exception as e:
        return {"answer": f"混合数据分析失败: {str(e)}"}


def get_file_info(file_obj, file_type: str) -> Dict:
    """获取文件信息
    
    Args:
        file_obj: 文件对象
        file_type: 文件类型
    
    Returns:
        Dict: 文件信息
    """
    info = {
        'name': getattr(file_obj, 'name', '未知文件'),
        'type': file_type,
        'sheets': []
    }
    
    try:
        if file_type == 'excel':
            # 重置文件指针到开始位置
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            wb = openpyxl.load_workbook(file_obj)
            info['sheets'] = wb.sheetnames
        elif file_type == 'csv':
            # CSV文件只有一个"工作表"
            info['sheets'] = ['默认']
    except Exception as e:
        print(f"获取文件信息失败: {e}")
        # 如果是Excel文件读取失败，提供更详细的错误信息
        if file_type == 'excel':
            info['error'] = f"Excel文件读取失败: {str(e)}"
        
    return info


# ==================== 历史记录管理功能 ====================

def init_history_database():
    """初始化历史记录数据库"""
    db_path = Path("analysis_history.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建历史记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            query TEXT NOT NULL,
            model_used TEXT NOT NULL,
            data_info TEXT,
            result_text TEXT,
            result_data TEXT,
            charts_info TEXT,
            session_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def save_analysis_history(query: str, model_used: str, data_info: Dict, 
                         result: Dict, session_id: str = None) -> bool:
    """保存分析历史记录
    
    Args:
        query: 用户查询
        model_used: 使用的模型
        data_info: 数据信息
        result: 分析结果
        session_id: 会话ID
    
    Returns:
        bool: 保存是否成功
    """
    try:
        init_history_database()
        
        conn = sqlite3.connect("analysis_history.db")
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 提取图表信息
        charts_info = {}
        if "bar" in result:
            charts_info["bar"] = True
        if "line" in result:
            charts_info["line"] = True
        if "table" in result:
            charts_info["table"] = True
            
        cursor.execute('''
            INSERT INTO analysis_history 
            (timestamp, query, model_used, data_info, result_text, result_data, charts_info, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            query,
            model_used,
            json.dumps(data_info, ensure_ascii=False),
            result.get("answer", ""),
            json.dumps(result, ensure_ascii=False),
            json.dumps(charts_info, ensure_ascii=False),
            session_id or "default"
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"保存历史记录失败: {e}")
        return False


def get_analysis_history(limit: int = 50, session_id: str = None) -> List[Dict]:
    """获取分析历史记录
    
    Args:
        limit: 返回记录数量限制
        session_id: 会话ID过滤
    
    Returns:
        List[Dict]: 历史记录列表
    """
    try:
        if not Path("analysis_history.db").exists():
            return []
            
        conn = sqlite3.connect("analysis_history.db")
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT * FROM analysis_history 
                WHERE session_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM analysis_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            record = dict(zip(columns, row))
            
            # 解析JSON字段
            try:
                record['data_info'] = json.loads(record['data_info']) if record['data_info'] else {}
                record['result_data'] = json.loads(record['result_data']) if record['result_data'] else {}
                record['charts_info'] = json.loads(record['charts_info']) if record['charts_info'] else {}
            except:
                pass
                
            history.append(record)
        
        conn.close()
        return history
        
    except Exception as e:
        print(f"获取历史记录失败: {e}")
        return []


def delete_analysis_history(record_id: int = None, session_id: str = None, 
                           days_old: int = None) -> bool:
    """删除分析历史记录
    
    Args:
        record_id: 特定记录ID
        session_id: 会话ID（删除该会话所有记录）
        days_old: 删除多少天前的记录
    
    Returns:
        bool: 删除是否成功
    """
    try:
        if not Path("analysis_history.db").exists():
            return True
            
        conn = sqlite3.connect("analysis_history.db")
        cursor = conn.cursor()
        
        if record_id:
            cursor.execute('DELETE FROM analysis_history WHERE id = ?', (record_id,))
        elif session_id:
            cursor.execute('DELETE FROM analysis_history WHERE session_id = ?', (session_id,))
        elif days_old:
            cutoff_date = datetime.now() - pd.Timedelta(days=days_old)
            cursor.execute('DELETE FROM analysis_history WHERE created_at < ?', 
                         (cutoff_date.strftime("%Y-%m-%d %H:%M:%S"),))
        else:
            # 删除所有记录
            cursor.execute('DELETE FROM analysis_history')
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"删除历史记录失败: {e}")
        return False


def get_history_statistics() -> Dict:
    """获取历史记录统计信息
    
    Returns:
        Dict: 统计信息
    """
    try:
        if not Path("analysis_history.db").exists():
            return {"total_records": 0, "total_sessions": 0, "most_used_model": "无", "recent_records": 0}
            
        conn = sqlite3.connect("analysis_history.db")
        cursor = conn.cursor()
        
        # 获取基本统计信息
        cursor.execute('SELECT COUNT(*) FROM analysis_history')
        total_records = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT session_id) FROM analysis_history')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT model_used, COUNT(*) as count 
            FROM analysis_history 
            GROUP BY model_used 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        most_used = cursor.fetchone()
        most_used_model = most_used[0] if most_used else "无"
        
        # 获取最近7天的记录数
        cursor.execute('''
            SELECT COUNT(*) FROM analysis_history 
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        recent_records = cursor.fetchone()[0]
        
        conn.close()
        return {
            "total_records": total_records,
            "total_sessions": total_sessions,
            "most_used_model": most_used_model,
            "recent_records": recent_records
        }
        
    except Exception as e:
        print(f"获取历史统计信息失败: {e}")
        return {
            "total_records": 0,
            "total_sessions": 0,
            "most_used_model": "无",
            "recent_records": 0
        }


def analyze_mixed_format_data(files) -> Dict:
    """分析混合格式文件数据
    
    Args:
        files: 上传的文件列表
    
    Returns:
        Dict: 分析结果字典
    """
    analysis_results = {}
    
    for uploaded_file in files:
        try:
            file_name = uploaded_file.name
            file_extension = file_name.split('.')[-1].lower()
            
            # 判断文件类型并读取数据
            if file_extension in ["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm"]:
                # 重置文件指针到开始位置
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                
                # 尝试多种引擎读取Excel文件
                df = None
                engines = ['openpyxl', 'xlrd', None]
                
                for engine in engines:
                    try:
                        if hasattr(uploaded_file, 'seek'):
                            uploaded_file.seek(0)
                        if engine:
                            df = pd.read_excel(uploaded_file, engine=engine)
                        else:
                            df = pd.read_excel(uploaded_file)
                        break
                    except Exception:
                        continue
                
                if df is None:
                    raise Exception(f"无法读取Excel文件 {file_name}，请检查文件格式")
                file_type = "Excel"
            elif file_extension == "csv":
                df = pd.read_csv(uploaded_file)
                file_type = "CSV"
            elif file_extension == "txt":
                df = pd.read_csv(uploaded_file, sep='\t')
                file_type = "TXT"
            elif file_extension == "json":
                df = pd.read_json(uploaded_file)
                file_type = "JSON"
            else:
                continue
            
            # 分析数据特征
            numeric_columns = len(df.select_dtypes(include=['number']).columns)
            text_columns = len(df.select_dtypes(include=['object']).columns)
            date_columns = len(df.select_dtypes(include=['datetime']).columns)
            
            analysis_results[file_name] = {
                'file_type': file_type,
                'rows': len(df),
                'columns': len(df.columns),
                'numeric_columns': numeric_columns,
                'text_columns': text_columns,
                'date_columns': date_columns,
                'data_preview': df.head(),
                'dataframe': df
            }
            
        except Exception as e:
            print(f"分析文件 {uploaded_file.name} 失败: {e}")
            continue
    
    return analysis_results
