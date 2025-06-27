"""
main.py - 自助式数据分析（数据分析智能体）

"""
# 导入必要的库
import json  # JSON数据处理
import matplotlib.pyplot as plt  # 绘图库
import openpyxl  # Excel文件处理
import pandas as pd  # 数据处理库
import streamlit as st  # Streamlit Web应用框架
import uuid  # 生成唯一标识符

# 从utils模块导入自定义工具函数
from utils import (
    dataframe_agent,  # 数据分析智能体
    test_api_connection,  # API连接测试
    merge_multiple_files,  # 多文件合并
    join_dataframes,  # 数据表连接
    get_file_info,  # 获取文件信息
    get_analysis_history,  # 获取分析历史
    delete_analysis_history,  # 删除分析历史
    get_history_statistics,  # 获取历史统计
    analyze_mixed_format_data,  # 混合格式数据分析
    save_analysis_history,  # 保存分析历史
    init_history_database  # 初始化历史数据库
)

# 页面配置 - 设置Streamlit应用的基本配置
st.set_page_config(
    page_title="数据分析智能体",  # 页面标题
    page_icon="📊",  # 页面图标
    layout="wide",  # 宽屏布局
    initial_sidebar_state="expanded"  # 侧边栏默认展开
)

# 设置matplotlib中文字体 - 确保图表能正确显示中文
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']  # 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 自定义CSS样式 - 美化Streamlit应用界面
st.markdown("""
<style>
    /* 主标题样式 - 渐变色标题效果 */
    .main-title {
        font-size: 2.5rem;  /* 字体大小 */
        font-weight: bold;  /* 粗体 */
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);  /* 渐变背景 */
        -webkit-background-clip: text;  /* 背景裁剪到文字 */
        -webkit-text-fill-color: transparent;  /* 文字透明显示背景 */
        text-align: center;  /* 居中对齐 */
        margin-bottom: 2rem;  /* 底部边距 */
        padding: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);  /* 文字阴影 */
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* 卡片样式 */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* 成功消息样式 */
    .success-message {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* 数据框样式 */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* 图表容器样式 */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* 分析结果样式 */
    .analysis-result {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #e1e8ed;
    }
</style>
""", unsafe_allow_html=True)


def create_chart(input_data, chart_type):
    """生成统计图表函数
    
    Args:
        input_data: 图表数据，包含columns和data字段
        chart_type: 图表类型，'bar'为柱状图，'line'为折线图
    """
    # 创建DataFrame用于折线图
    df_data = pd.DataFrame(
        data={
            "x": input_data["columns"],
            "y": input_data["data"]
        }
    ).set_index("x")
    
    if chart_type == "bar":
        # 设置中文字体，确保图表能正确显示中文
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图表，设置图形大小和分辨率
        fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
        
        # 使用渐变色彩方案，提升视觉效果
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        bars = ax.bar(input_data["columns"], input_data["data"], 
                     color=colors[:len(input_data["columns"])], 
                     alpha=0.8, edgecolor='white', linewidth=2)
        
        # 添加数值标签，显示具体数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', 
                   fontsize=10, fontweight='bold')
        
        # 美化图表 - 设置背景色、网格线、边框样式
        ax.set_facecolor('#f8f9fa')  # 设置背景色
        ax.grid(True, alpha=0.3, linestyle='--')  # 添加网格线
        ax.spines['top'].set_visible(False)  # 隐藏顶部边框
        ax.spines['right'].set_visible(False)  # 隐藏右侧边框
        ax.spines['left'].set_color('#cccccc')  # 设置左侧边框颜色
        ax.spines['bottom'].set_color('#cccccc')  # 设置底部边框颜色
        
        # 旋转x轴标签，避免重叠
        plt.xticks(rotation=45, ha='right')
        # 自动调整布局
        plt.tight_layout()
        # 在Streamlit中显示图表
        st.pyplot(fig)
        # 关闭图形对象，释放内存
        plt.close()
        
    elif chart_type == "line":
        # 使用Streamlit的内置折线图，配置容器宽度和高度
        st.line_chart(df_data, use_container_width=True, height=400)


# 使用自定义样式的主标题 - 显示应用标题和功能描述
st.markdown('<h1 class="main-title">🚀 数据分析智能体</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #6c757d; margin-bottom: 2rem;">🤖 智能数据分析 | 📊 可视化图表 | 🔍 深度洞察</div>', unsafe_allow_html=True)

# 侧边栏配置 - 创建配置面板，包含模型选择、API密钥等设置
with st.sidebar:
    # 配置面板标题
    st.markdown('<div class="info-card"><h2 style="color: #667eea; margin: 0;">⚙️ 配置面板</h2><p style="color: #6c757d; margin: 0.5rem 0 0 0;">配置您的AI分析环境</p></div>', unsafe_allow_html=True)
    
    # 大模型选择区域
    st.markdown('<div style="margin-top: 1.5rem;"><h3 style="color: #495057;">🤖 选择AI模型</h3></div>', unsafe_allow_html=True)
    
    # 选择服务提供商 - 用户可选择不同的AI服务提供商
    api_vendor = st.radio(
        label='请选择服务提供商：', 
        options=['DeepSeek', 'OpenAI', 'qwen3'],  # 支持的服务提供商列表
        horizontal=True,  # 水平排列选项
        help="不同服务提供商提供不同的AI模型"  # 帮助提示
    )
    
    # 根据服务提供商配置模型选项 - 不同提供商有不同的API地址和模型列表
    if api_vendor == 'OpenAI':
        base_url = 'https://twapi.openai-hk.com/v1'  # OpenAI API地址
        model_options = ['gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4.1-mini', 'gpt-4.1']  # OpenAI模型列表
        provider = 'openai'  # 提供商标识
    elif api_vendor == 'DeepSeek':
        base_url = 'https://api.deepseek.com'  # DeepSeek API地址
        model_options = ['deepseek-chat', 'deepseek-reasoner']  # DeepSeek模型列表
        provider = 'deepseek'  # 提供商标识
    elif api_vendor == 'qwen3':
        base_url = 'https://dashscope.aliyuncs.com'  # 阿里云API地址
        model_options = ['qwen-max', 'qwen-plus', 'qwen-turbo']  # 通义千问模型列表
        provider = 'qwen'  # 提供商标识
    
    # 选择具体模型 - 从当前提供商的模型列表中选择
    selected_model_name = st.selectbox(
        "请选择具体模型:",
        model_options,  # 当前提供商支持的模型列表
        help="不同模型在分析能力和响应速度上有所差异"  # 帮助提示
    )
    
    # 构建模型配置字典 - 包含提供商、模型名称、API地址等信息
    model_config = {
        "provider": provider,  # 提供商标识
        "model": selected_model_name,  # 选择的模型名称
        "base_url": base_url  # API基础地址
    }
    # 将模型配置保存到会话状态中
    st.session_state["selected_model"] = model_config
    
    # 显示当前选择的模型信息
    st.info(f"🎯 当前选择: {api_vendor} - {selected_model_name}")
    
    # API密钥输入区域
    st.markdown('<div style="margin-top: 1.5rem;"><h3 style="color: #495057;">🔑 API密钥配置</h3></div>', unsafe_allow_html=True)
    
    # 根据服务提供商设置API密钥占位符 - 不同提供商显示不同的提示文本
    api_key_placeholders = {
        "DeepSeek": "请输入DeepSeek API密钥",
        "OpenAI": "请输入OpenAI API密钥",
        "qwen3": "请输入阿里云API密钥"
    }
    
    # API密钥输入框 - 密码类型输入，确保安全性
    api_key = st.text_input(
        "API密钥:",
        type="password",  # 密码类型，输入内容会被隐藏
        placeholder=api_key_placeholders[api_vendor],  # 根据提供商显示对应占位符
        help="请输入您选择服务提供商对应的API密钥，密钥将安全存储在当前会话中"  # 帮助提示
    )

    # 将API密钥存储到session state并进行基本验证
    if api_key:
        # 基本的API密钥格式验证 - 检查不同提供商的密钥格式
        api_key_valid = True  # 验证标志
        validation_msg = ""  # 验证错误消息
        
        # DeepSeek API密钥格式验证
        if api_vendor == "DeepSeek":
            if not api_key.startswith("sk-") or len(api_key) < 20:
                api_key_valid = False
                validation_msg = "DeepSeek API密钥格式不正确，应以'sk-'开头"
        # OpenAI API密钥格式验证
        elif api_vendor == "OpenAI":
            if not (api_key.startswith("sk-") or api_key.startswith("hk-")) or len(api_key) < 20:
                api_key_valid = False
                validation_msg = "OpenAI API密钥格式不正确，应以'sk-'或'hk-'开头"
        # 阿里云API密钥格式验证
        elif api_vendor == "qwen3":
            if len(api_key) < 10:
                api_key_valid = False
                validation_msg = "阿里云API密钥格式不正确，请检查"
        
        # 如果API密钥格式验证通过
        if api_key_valid:
             # 将API密钥保存到会话状态
             st.session_state["api_key"] = api_key
             st.success("✅ API密钥格式正确")
             
             # 添加测试连接按钮 - 验证API密钥是否真正有效
             if st.button("🔍 测试API密钥连接", help="验证API密钥是否有效"):
                 with st.spinner("正在测试API连接..."):
                     try:
                         # 导入API连接测试函数
                         from utils import test_api_connection
                         # 使用当前选择的模型配置进行测试
                         test_result = test_api_connection(model_config, api_key)
                         if test_result["success"]:
                             st.success("🎉 API密钥连接成功！")
                         else:
                             st.error(f"❌ API密钥连接失败: {test_result['error']}")
                     except Exception as e:
                         st.error(f"❌ 连接测试失败: {str(e)}")
        else:
            # 如果API密钥格式验证失败，显示错误信息并清除会话状态
            st.error(f"❌ {validation_msg}")
            if "api_key" in st.session_state:
                del st.session_state["api_key"]
    else:
        # 如果没有输入API密钥，显示警告并清除会话状态
        st.warning("⚠️ 请输入API密钥以使用AI分析功能")
        if "api_key" in st.session_state:
            del st.session_state["api_key"]

    # 数据文件上传区域
    st.markdown('<div style="margin-top: 1.5rem;"><h3 style="color: #495057;">📁 数据文件上传</h3></div>', unsafe_allow_html=True)
    
    # 数据处理模式选择 - 提供三种不同的数据处理方式
    data_mode = st.radio(
        "📊 选择数据处理模式:", 
        ("单文件分析", "多文件数据合并"),  # 三种处理模式
        help="选择不同的数据处理方式"  # 帮助提示
    )
    
    # 单文件分析模式
    if data_mode == "单文件分析":
        # 文件类型选择 - 支持Excel和CSV两种格式
        option = st.radio("请选择数据文件类型:", ("Excel", "CSV"))
        # 根据选择的文件类型设置支持的文件扩展名
        if option == "Excel":
            file_types = ["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm"]  # Excel支持的格式
        else:
            file_types = ["csv"]  # CSV格式
        # 文件上传组件
        data = st.file_uploader(
            f"📎 上传你的{option}数据文件", 
            type=file_types, 
            help="支持拖拽上传，文件大小限制200MB\n支持的Excel格式：.xlsx, .xls, .xlsm, .xlsb, .xltx, .xltm"
        )
        
        # 如果用户上传了文件
        if data:
            # 获取文件扩展名
            file_extension = data.name.split('.')[-1].lower()
            # 处理Excel文件
            if file_extension in ["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm"]:
                try:
                    # 重置文件指针到开始位置，确保能正确读取文件
                    data.seek(0)
                    
                    # 尝试多种方式读取Excel文件 - 提高兼容性
                    success = False  # 读取成功标志
                    
                    # 方法1: 使用openpyxl引擎读取（推荐，支持新版Excel格式）
                    try:
                        # 先加载工作簿获取工作表列表
                        wb = openpyxl.load_workbook(data)
                        # 让用户选择要加载的工作表
                        sheet_option = st.radio(label="请选择要加载的工作表：", options=wb.sheetnames)
                        # 再次重置文件指针用于pandas读取
                        data.seek(0)
                        # 使用pandas读取指定工作表
                        st.session_state["df"] = pd.read_excel(data, sheet_name=sheet_option, engine='openpyxl')
                        success = True
                    except Exception as e1:
                        st.warning(f"⚠️ openpyxl引擎读取失败: {str(e1)}")
                        
                        # 方法2: 尝试使用xlrd引擎（适用于旧版.xls文件）
                        try:
                            data.seek(0)
                            st.session_state["df"] = pd.read_excel(data, engine='xlrd')
                            success = True
                            st.success("✅ 使用xlrd引擎成功读取文件")
                        except Exception as e2:
                            st.warning(f"⚠️ xlrd引擎读取失败: {str(e2)}")
                            
                            # 方法3: 尝试不指定引擎让pandas自动选择
                            try:
                                data.seek(0)
                                st.session_state["df"] = pd.read_excel(data)
                                success = True
                                st.success("✅ 使用默认引擎成功读取文件")
                            except Exception as e3:
                                st.error(f"❌ 所有方法都无法读取Excel文件")
                                st.error(f"详细错误信息: {str(e3)}")
                    
                    # 如果所有方法都失败，显示解决建议
                    if not success:
                        st.info("💡 解决建议：\n1. 确保文件未损坏\n2. 尝试用Excel重新保存文件为.xlsx格式\n3. 检查文件是否为有效的Excel格式\n4. 如果是.xls文件，请安装xlrd库: pip install xlrd")
                        st.stop()
                        
                except Exception as e:
                    # Excel文件读取的总体异常处理
                    st.error(f"❌ 读取Excel文件失败: {str(e)}")
                    st.info("💡 建议：\n1. 确保文件未损坏\n2. 尝试用Excel重新保存文件\n3. 检查文件是否为有效的Excel格式")
                    st.stop()
            else:
                # 处理CSV文件
                try:
                    st.session_state["df"] = pd.read_csv(data)
                except Exception as e:
                    st.error(f"❌ 读取CSV文件失败: {str(e)}")
                    st.stop()
            # 显示原始数据预览
            with st.expander("📋 原始数据预览"):
                st.dataframe(st.session_state["df"])
    
    # 多文件数据合并模式
    elif data_mode == "多文件数据合并":
        # 功能说明
        st.info("🔗 支持同时上传多个Excel和CSV文件进行合并分析")
        
        # 多文件上传组件
        uploaded_files = st.file_uploader(
            "📎 选择多个数据文件", 
            type=["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm", "csv"],  # 支持的文件格式
            accept_multiple_files=True,  # 允许多文件上传
            help="可同时选择多个Excel和CSV文件\n支持的Excel格式：.xlsx, .xls, .xlsm, .xlsb, .xltx, .xltm"
        )
        
        # 如果用户上传了文件
        if uploaded_files:
            # 合并方式选择
            merge_type = st.radio(
                "🔄 选择合并方式:", 
                ("纵向合并(追加行)", "横向连接(基于索引)"),
                help="纵向合并：将多个文件的数据行追加在一起；横向连接：将多个文件按索引横向连接"
            )
            
            # 存储文件数据和预览信息
            files_data = []  # 存储文件信息
            file_previews = []  # 存储预览数据
            
            # 遍历每个上传的文件
            for uploaded_file in uploaded_files:
                # 获取文件扩展名
                file_extension = uploaded_file.name.split('.')[-1].lower()
                # 判断文件类型
                file_type = "excel" if file_extension in ["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm"] else "csv"
                
                # 获取文件信息（如Excel的工作表列表）
                from utils import get_file_info
                file_info = get_file_info(uploaded_file, file_type)
                
                # 如果是Excel文件且有多个工作表，让用户选择
                if file_type == "excel" and len(file_info['sheets']) > 1:
                    selected_sheet = st.selectbox(
                        f"📋 选择 {uploaded_file.name} 的工作表:",
                        file_info['sheets'],
                        key=f"sheet_{uploaded_file.name}"  # 使用文件名作为唯一键
                    )
                else:
                    # 单工作表Excel或CSV文件
                    selected_sheet = 0 if file_type == "excel" else None
                
                # 保存文件信息
                files_data.append({
                    'file': uploaded_file,
                    'type': file_type,
                    'sheet': selected_sheet
                })
                
                # 预览每个文件的数据（读取前5行）
                try:
                    if file_type == "excel":
                        # 重置文件指针到开始位置
                        uploaded_file.seek(0)
                        
                        # 尝试多种引擎读取Excel文件（提高兼容性）
                        preview_df = None
                        engines = ['openpyxl', 'xlrd', None]  # None表示让pandas自动选择引擎
                        
                        # 依次尝试不同的引擎
                        for engine in engines:
                            try:
                                uploaded_file.seek(0)
                                if engine:
                                    # 使用指定引擎读取前5行数据
                                    preview_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, nrows=5, engine=engine)
                                else:
                                    # 使用默认引擎读取前5行数据
                                    preview_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, nrows=5)
                                break  # 成功读取，跳出循环
                            except Exception:
                                continue  # 当前引擎失败，尝试下一个引擎
                        
                        # 如果所有引擎都失败
                        if preview_df is None:
                            raise Exception("所有Excel引擎都无法读取此文件")
                    else:
                        # 处理CSV文件
                        uploaded_file.seek(0)
                        preview_df = pd.read_csv(uploaded_file, nrows=5)  # 读取前5行
                    
                    # 保存预览数据
                    file_previews.append((uploaded_file.name, preview_df))
                except Exception as e:
                    # 文件读取失败的错误处理
                    st.error(f"❌ 读取文件 {uploaded_file.name} 失败: {e}")
                    st.info(f"💡 建议：如果是Excel文件，请确保文件格式正确或尝试重新保存为.xlsx格式")
            
            # 显示文件预览
            if file_previews:
                with st.expander("👀 文件预览 (前5行)"):
                    for file_name, preview_df in file_previews:
                        st.write(f"**{file_name}**")  # 显示文件名
                        st.dataframe(preview_df)  # 显示预览数据
                        st.write("---")  # 分隔线
            
            # 执行合并按钮
            if st.button("🔄 执行数据合并", type="primary"):
                try:
                    # 导入合并函数
                    from utils import merge_multiple_files
                    # 根据用户选择确定合并方法
                    merge_method = "concat" if merge_type == "纵向合并(追加行)" else "join"
                    # 执行文件合并
                    merged_df = merge_multiple_files(files_data, merge_type=merge_method)
                    
                    # 检查合并结果
                    if not merged_df.empty:
                        # 保存合并后的数据到会话状态
                        st.session_state["df"] = merged_df
                        st.success(f"✅ 成功合并 {len(uploaded_files)} 个文件，共 {len(merged_df)} 行数据")
                        
                        # 显示合并后的数据预览
                        with st.expander("📊 合并后数据预览"):
                            st.dataframe(merged_df)
                    else:
                        st.error("❌ 数据合并失败，请检查文件格式")
                except Exception as e:
                    # 合并过程异常处理
                    st.error(f"❌ 合并过程中出错: {e}")
    
    # 数据表连接(JOIN操作)模式
    elif data_mode == "数据表连接(JOIN操作)":
        # 功能说明
        st.info("🔗 上传两个数据文件进行JOIN连接操作")
        
        # 创建两列布局，分别用于左表和右表
        col1, col2 = st.columns(2)
        
        # 左表（主表）上传区域
        with col1:
            st.write("**📄 左表 (主表)**")
            # 左表文件上传组件
            left_file = st.file_uploader(
                "上传左表文件", 
                type=["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm", "csv"],  # 支持的文件格式
                key="left_file",  # 唯一标识符
                help="支持的Excel格式：.xlsx, .xls, .xlsm, .xlsb, .xltx, .xltm"
            )
            
        # 右表（连接表）上传区域
        with col2:
            st.write("**📄 右表 (连接表)**")
            # 右表文件上传组件
            right_file = st.file_uploader(
                "上传右表文件", 
                type=["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm", "csv"],  # 支持的文件格式
                key="right_file",  # 唯一标识符
                help="支持的Excel格式：.xlsx, .xls, .xlsm, .xlsb, .xltx, .xltm"
            )
        
        # 如果两个文件都已上传
        if left_file and right_file:
            # 读取两个文件
            try:
                # 处理左表文件
                left_extension = left_file.name.split('.')[-1].lower()  # 获取文件扩展名
                if left_extension in ["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm"]:
                    # 处理Excel格式的左表
                    left_file.seek(0)  # 重置文件指针
                    
                    # 尝试多种引擎读取Excel文件（提高兼容性）
                    left_df = None
                    engines = ['openpyxl', 'xlrd', None]  # 可用的Excel读取引擎
                    
                    # 依次尝试不同引擎
                    for engine in engines:
                        try:
                            left_file.seek(0)
                            if engine:
                                left_df = pd.read_excel(left_file, engine=engine)
                            else:
                                left_df = pd.read_excel(left_file)  # 使用默认引擎
                            break  # 成功读取，跳出循环
                        except Exception:
                            continue  # 当前引擎失败，尝试下一个
                    
                    # 检查是否成功读取
                    if left_df is None:
                        raise Exception(f"无法读取左表文件 {left_file.name}，请检查文件格式")
                else:
                    # 处理CSV格式的左表
                    left_file.seek(0)
                    left_df = pd.read_csv(left_file)
                
                # 处理右表文件
                right_extension = right_file.name.split('.')[-1].lower()  # 获取文件扩展名
                if right_extension in ["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm"]:
                    # 处理Excel格式的右表
                    right_file.seek(0)  # 重置文件指针
                    
                    # 尝试多种引擎读取Excel文件（提高兼容性）
                    right_df = None
                    engines = ['openpyxl', 'xlrd', None]  # 可用的Excel读取引擎
                    
                    # 依次尝试不同引擎
                    for engine in engines:
                        try:
                            right_file.seek(0)
                            if engine:
                                right_df = pd.read_excel(right_file, engine=engine)
                            else:
                                right_df = pd.read_excel(right_file)  # 使用默认引擎
                            break  # 成功读取，跳出循环
                        except Exception:
                            continue  # 当前引擎失败，尝试下一个
                    
                    # 检查是否成功读取
                    if right_df is None:
                        raise Exception(f"无法读取右表文件 {right_file.name}，请检查文件格式")
                else:
                    # 处理CSV格式的右表
                    right_file.seek(0)
                    right_df = pd.read_csv(right_file)
                
                # 显示表预览（前5行）
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**左表预览:**")
                    st.dataframe(left_df.head())  # 显示左表前5行
                    
                with col2:
                    st.write("**右表预览:**")
                    st.dataframe(right_df.head())  # 显示右表前5行
                
                # 连接配置区域
                st.write("**🔗 连接配置**")
                
                # 找到两个表的共同字段（可用作连接键）
                common_columns = list(set(left_df.columns) & set(right_df.columns))
                
                # 如果存在共同字段
                if common_columns:
                    # 让用户选择连接字段
                    join_column = st.selectbox(
                        "选择连接字段:", 
                        common_columns,
                        help="选择两个表中都存在的字段作为连接键"
                    )
                    
                    # 连接类型选择
                    join_type = st.selectbox(
                        "选择连接类型:",
                        ["inner", "left", "right", "outer"],  # 支持的连接类型
                        format_func=lambda x: {  # 显示友好的中文名称
                            "inner": "内连接 (只保留匹配的记录)",
                            "left": "左连接 (保留左表所有记录)", 
                            "right": "右连接 (保留右表所有记录)",
                            "outer": "外连接 (保留所有记录)"
                        }[x]
                    )
                    
                    # 执行表连接按钮
                    if st.button("🔗 执行表连接", type="primary"):
                        try:
                            # 导入连接函数
                            from utils import join_dataframes
                            # 执行数据表连接
                            joined_df = join_dataframes(left_df, right_df, join_column, join_type)
                            
                            # 保存连接结果到会话状态
                            st.session_state["df"] = joined_df
                            st.success(f"✅ 成功连接两个表，结果包含 {len(joined_df)} 行数据")
                            
                            # 显示连接结果预览
                            with st.expander("📊 连接结果预览"):
                                st.dataframe(joined_df)
                                
                        except Exception as e:
                            # 连接失败的错误处理
                            st.error(f"❌ 表连接失败: {e}")
                else:
                    # 没有共同字段的警告
                    st.warning("⚠️ 两个表没有共同的字段，无法进行连接操作")
                    
            except Exception as e:
                # 文件读取失败的错误处理
                st.error(f"❌ 读取文件失败: {e}")

    # ==================== AI分析查询区域 ====================
    
    # 处理重新执行的查询（从历史记录重新运行）
    if 'rerun_query' in st.session_state:
        default_query = st.session_state['rerun_query']  # 获取要重新执行的查询
        del st.session_state['rerun_query']  # 清除标志
    else:
        default_query = ""  # 默认为空
    
    # 分析查询输入框
    query = st.text_area(
        "🔍 请描述你想要进行的数据分析:", 
        value=default_query,  # 设置默认值
        placeholder="例如：分析销售数据的趋势，找出最佳销售区域，预测未来销量等...",
        height=120,
        help="详细描述你的分析需求，AI将为你提供专业的数据洞察"
    )
    
    # 显示当前选择的AI模型信息
    if "selected_model" in st.session_state:
        model_info = st.session_state["selected_model"]
        st.info(f"🤖 当前使用模型: {model_info.get('provider', 'unknown')} - {model_info.get('model', 'unknown')}")
    
    # 检查是否配置了API密钥
    has_api_key = "api_key" in st.session_state and st.session_state["api_key"]
    
    # 生成分析按钮（需要API密钥和数据才能启用）
    button = st.button(
        "🚀 生成回答", 
        type="primary",
        disabled=not has_api_key or "df" not in st.session_state  # 没有API密钥或数据时禁用
    )

# ==================== 主内容区域 ====================
# 使用横向布局：数据预览、AI分析、历史记录

# 数据预览模块
st.markdown('<div class="info-card"><h3 style="color: #495057; margin: 0;">📊 数据预览</h3><p style="color: #6c757d; margin: 0.5rem 0 0 0;">您上传的数据概览</p></div>', unsafe_allow_html=True)
if "df" in st.session_state:
    # 显示数据表格
    st.dataframe(st.session_state["df"], use_container_width=True, height=300)
else:
    st.info("📁 请先上传数据文件")

st.divider()  # 添加分隔线

# AI分析模块
st.markdown('<div class="info-card"><h3 style="color: #495057; margin: 0;">🤖 AI分析结果</h3><p style="color: #6c757d; margin: 0.5rem 0 0 0;">基于您的问题生成的智能分析</p></div>', unsafe_allow_html=True)

# 分析模式选择（标准分析 vs 混合格式分析）
analysis_mode = st.radio(
    "🎯 选择分析模式:",
    ("标准数据分析", "混合格式文件分析"),
    help="标准分析：分析已上传的结构化数据；混合格式分析：智能处理多种格式的混合数据"
)

# 混合格式文件分析模式
if analysis_mode == "混合格式文件分析":
    st.info("🔍 混合格式文件分析：支持同时分析文本、数值、日期等多种数据类型")
    
    # 混合格式文件上传组件
    mixed_files = st.file_uploader(
        "📎 上传混合格式文件",
        type=["xlsx", "xls", "xlsm", "xlsb", "xltx", "xltm", "csv", "txt", "json"],  # 支持多种文件格式
        accept_multiple_files=True,  # 允许上传多个文件
        help="支持Excel、CSV、TXT、JSON等多种格式文件\n支持的Excel格式：.xlsx, .xls, .xlsm, .xlsb, .xltx, .xltm",
        key="mixed_files_analysis"
    )
    
        # 当有文件上传时显示分析按钮
    if mixed_files:
        # 开始混合格式数据分析
        if st.button("🔍 开始混合格式分析", type="primary", key="mixed_analysis_main"):
            try:
                from utils import analyze_mixed_format_data
                
                # 显示分析进度
                with st.spinner("🤖 正在分析混合格式数据..."):
                    # 调用混合格式数据分析函数
                    analysis_result = analyze_mixed_format_data(mixed_files)
                    
                    if analysis_result:
                        st.success("✅ 混合格式分析完成！")
                        
                        # 显示详细的数据格式分析报告
                        with st.expander("📊 数据格式分析报告", expanded=True):
                            # 遍历每个文件的分析结果
                            for file_name, file_analysis in analysis_result.items():
                                st.write(f"**📄 {file_name}**")
                                st.write(f"- 文件类型: {file_analysis['file_type']}")
                                st.write(f"- 数据行数: {file_analysis['rows']}")
                                st.write(f"- 数据列数: {file_analysis['columns']}")
                                st.write(f"- 数值列: {file_analysis['numeric_columns']}")
                                st.write(f"- 文本列: {file_analysis['text_columns']}")
                                st.write(f"- 日期列: {file_analysis['date_columns']}")
                                    
                                # 显示数据预览（如果有）
                                if 'data_preview' in file_analysis:
                                    st.write("**数据预览:**")
                                    st.dataframe(file_analysis['data_preview'])
                                
                                st.write("---")  # 分隔线
                        
                        # 合并所有分析出的数据用于后续AI分析
                        combined_data = []
                        for file_name, file_analysis in analysis_result.items():
                            if 'dataframe' in file_analysis:
                                combined_data.append(file_analysis['dataframe'])
                        
                        # 处理数据合并逻辑
                        if combined_data:
                            # 如果有多个数据框，尝试纵向合并
                            if len(combined_data) > 1:
                                try:
                                    st.session_state["df"] = pd.concat(combined_data, ignore_index=True)
                                    st.info(f"🔗 已合并 {len(combined_data)} 个数据源，共 {len(st.session_state['df'])} 行数据")
                                except Exception as e:
                                    st.warning(f"⚠️ 数据合并失败，使用第一个数据源: {e}")
                                    st.session_state["df"] = combined_data[0]
                            else:
                                # 只有一个数据源，直接使用
                                st.session_state["df"] = combined_data[0]
                            
                            # 显示合并后的数据预览
                            with st.expander("📋 合并后数据预览"):
                                st.dataframe(st.session_state["df"])
                        else:
                            st.error("❌ 混合格式分析失败，请检查文件格式")
                            
            except Exception as e:
                st.error(f"❌ 分析过程中出错: {e}")

st.divider()  # 添加分隔线

# 历史记录模块
st.markdown('<div class="info-card"><h3 style="color: #495057; margin: 0;">📚 历史记录</h3><p style="color: #6c757d; margin: 0.5rem 0 0 0;">管理您的分析历史</p></div>', unsafe_allow_html=True)

# 历史记录操作选择
history_option = st.radio(
    "📋 选择操作:",
    ("查看分析历史", "历史记录统计", "清理历史记录"),
    help="管理您的数据分析历史记录"
)
    
# 查看分析历史记录
if history_option == "查看分析历史":
    from utils import get_analysis_history
    
    # 获取最近20条历史记录
    history_records = get_analysis_history(limit=20)
    
    if history_records:
        st.success(f"📊 找到 {len(history_records)} 条历史记录")
        
        # 遍历并显示每条历史记录
        for i, record in enumerate(history_records):
            # 使用可展开的容器显示记录详情
            with st.expander(f"🕐 {record['timestamp']} - {record['query'][:30]}...", expanded=False):
                st.write(f"**📝 查询内容:** {record['query']}")
                st.write(f"**🤖 使用模型:** {record['model_used']}")
                
                # 显示分析结果（如果有）
                if record['result_text']:
                    st.write("**📊 分析结果:**")
                    # 限制显示长度，避免界面过长
                    st.info(record['result_text'][:300] + "..." if len(record['result_text']) > 300 else record['result_text'])
                
                st.write(f"**📅 时间:** {record['timestamp']}")
                
                # 显示生成的图表信息
                charts = record.get('charts_info', {})
                if charts:
                    chart_types = []
                    if charts.get('bar'): chart_types.append('📊柱状图')
                    if charts.get('line'): chart_types.append('📈折线图')
                    if charts.get('table'): chart_types.append('📋表格')
                    
                    if chart_types:
                        st.write(f"**📈 生成图表:** {', '.join(chart_types)}")
                
                # 重新执行查询按钮
                if st.button(f"🔄 重新执行", key=f"rerun_{record['id']}"):
                    st.session_state['rerun_query'] = record['query']  # 设置要重新执行的查询
                    st.rerun()  # 刷新页面
    else:
        st.info("📝 暂无分析历史记录")
    
# 历史记录统计分析
elif history_option == "历史记录统计":
    from utils import get_history_statistics
    
    # 获取统计数据
    stats = get_history_statistics()
    
    # 显示关键统计指标
    st.metric("📊 总记录数", stats['total_records'])
    st.metric("🔗 总会话数", stats['total_sessions'])
    st.metric("🤖 常用模型", stats['most_used_model'])
    st.metric("📅 近7天记录", stats['recent_records'])
    
    # 显示详细的使用趋势图表
    if stats['total_records'] > 0:
        st.write("**📈 使用趋势分析**")
        
        # 获取最近100条记录用于趋势分析
        history_records = get_analysis_history(limit=100)
        if history_records:
            # 按日期统计使用频率
            dates = [record['timestamp'][:10] for record in history_records]  # 提取日期部分
            date_counts = pd.Series(dates).value_counts().sort_index()  # 统计每日使用次数
            
            # 显示使用趋势折线图
            st.line_chart(date_counts, height=200)

# 清理历史记录功能
elif history_option == "清理历史记录":
    from utils import delete_analysis_history
    
    # 警告提示
    st.warning("⚠️ 清理操作不可恢复，请谨慎操作")
    
    # 清理方式选择
    clean_option = st.selectbox(
        "选择清理方式:",
        ["清理7天前的记录", "清理30天前的记录", "清理所有记录"]
    )
    
    # 确认清理按钮
    if st.button("🗑️ 确认清理", type="secondary"):
        # 根据选择的清理方式执行相应操作
        if clean_option == "清理7天前的记录":
            success = delete_analysis_history(days_old=7)  # 清理7天前的记录
        elif clean_option == "清理30天前的记录":
            success = delete_analysis_history(days_old=30)  # 清理30天前的记录
        else:
            success = delete_analysis_history()  # 清理所有记录
        
        # 显示清理结果
        if success:
            st.success("✅ 历史记录清理完成")
        else:
            st.error("❌ 清理失败，请重试")

# ==================== AI分析结果显示区域 ====================
# 在主要内容区域下方显示AI分析结果
st.markdown('<div style="margin-top: 2rem;"><hr style="border: none; height: 2px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 2rem 0;"></div>', unsafe_allow_html=True)

# ==================== AI分析请求处理 ====================

# 验证数据是否已上传
if button and not data:
    st.error("⚠️ 请先上传数据文件")
    st.stop()

# 验证API密钥是否已配置
if button and not has_api_key:
    st.error("⚠️ 请先输入API密钥")
    st.stop()

# 执行AI数据分析
if query and button:
    with st.spinner("🤖 AI正在思考中，请稍等..."):
        # 获取用户选择的模型信息和API密钥
        selected_model = st.session_state.get("selected_model", {"provider": "deepseek", "model": "deepseek-reasoner", "base_url": "https://api.deepseek.com"})
        api_key = st.session_state.get("api_key")
        # 调用AI数据分析代理函数
        result = dataframe_agent(st.session_state["df"], query, selected_model, api_key)
        
        # ==================== 分析结果显示 ====================
        # 创建分析结果容器
        st.markdown('<div class="analysis-result">', unsafe_allow_html=True)
        
        # 初始化图表信息记录（用于历史记录）
        charts_info = {}
        result_text = ""
        
        # 显示文本分析结果
        if "answer" in result:
            st.markdown('<h4 style="color: #495057; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem;">📝 分析结果</h4>', unsafe_allow_html=True)
            st.markdown(f'<div style="background: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">{result["answer"]}</div>', unsafe_allow_html=True)
            result_text = result["answer"]  # 保存文本结果用于历史记录
        
        # 显示数据表格结果
        if "table" in result:
            st.markdown('<h4 style="color: #495057; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem;">📋 数据表格</h4>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # 将表格数据转换为DataFrame并显示
            st.table(pd.DataFrame(result["table"]["data"],
                                  columns=result["table"]["columns"]))
            st.markdown('</div>', unsafe_allow_html=True)
            charts_info['table'] = True  # 记录生成了表格
        
        # 显示柱状图结果
        if "bar" in result:
            st.markdown('<h4 style="color: #495057; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem;">📊 柱状图</h4>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            create_chart(result["bar"], "bar")  # 调用图表创建函数
            st.markdown('</div>', unsafe_allow_html=True)
            charts_info['bar'] = True  # 记录生成了柱状图
        
        # 显示折线图结果
        if "line" in result:
            st.markdown('<h4 style="color: #495057; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem;">📈 折线图</h4>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            create_chart(result["line"], "line")  # 调用图表创建函数
            st.markdown('</div>', unsafe_allow_html=True)
            charts_info['line'] = True  # 记录生成了折线图
         
        # 关闭分析结果容器
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ==================== 保存分析历史记录 ====================
        try:
            from utils import save_analysis_history, init_history_database
            
            # 初始化历史记录数据库
            init_history_database()
            
            # 保存本次分析的历史记录
            save_analysis_history(
                query=query,  # 用户查询内容
                model_used=selected_model.get('model', 'unknown'),  # 使用的AI模型
                data_info={'columns': len(st.session_state["df"].columns), 'rows': len(st.session_state["df"])},  # 数据信息
                result={'answer': result_text, 'bar': charts_info.get('bar', False), 'line': charts_info.get('line', False), 'table': charts_info.get('table', False)}  # 分析结果信息
            )
            
            st.info("💾 分析结果已保存到历史记录")
        except Exception as save_error:
            st.warning(f"⚠️ 保存历史记录失败: {save_error}")

# ==================== 页脚信息 ====================
# 显示应用程序的页脚信息，包括品牌信息和联系方式
st.markdown("""
<div style="margin-top: 3rem; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 15px; text-align: center;">
    <h4 style="color: white; margin: 0;">🚀 数据分析智能体</h4>
    <p style="color: #e9ecef; margin: 0.5rem 0 0 0;">让数据分析变得简单高效 | Powered by AI</p>
    <div style="margin-top: 1rem; color: #ced4da; font-size: 0.9rem;">
        <span>📧 支持: support@qianfeng.com</span> | 
        <span>🌐 官网: www.qianfeng.com</span> | 
        <span>📚 文档: docs.qianfeng.com</span>
    </div>
</div>
""", unsafe_allow_html=True)
