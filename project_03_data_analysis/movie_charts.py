"""
TMDB-TOP300电影榜单数据统计分析
================================
功能说明：
1. 统计TOP300的电影中，每一年上映的电影数量的变化（折线图）
2. 统计对比不同语言电影数量（柱状图）
3. 统计对比不同类型电影数量（柱状图）
4. 统计对比各个电影评分的比例（饼状图）
"""

import logging
from pathlib import Path

import pandas as pd
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib

logger = logging.getLogger(__name__)

# 资源路径（相对于本项目目录）
_RESOURCES_DIR = Path(__file__).resolve().parent / "resources"


def configure_matplotlib():
    """配置Matplotlib中文显示和基础参数"""
    # 解决PyCharm后端兼容性问题
    try:
        matplotlib.use('TkAgg')  # 尝试使用TkAgg后端
    except ImportError:
        pass  # 如果失败则使用默认后端
    
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def load_movie_data(file_path=None):
    """
    加载电影数据

    Args:
        file_path: CSV文件路径（默认: resources/movies.csv）

    Returns:
        DataFrame: 包含电影数据的DataFrame对象
    """
    if file_path is None:
        file_path = _RESOURCES_DIR / "movies.csv"
    df = pd.read_csv(
        file_path,
        usecols=['电影名', '年份', '上映时间', '语言', '类型', '评分'],
    )
    df['年份'] = df['年份'].astype(str).str.replace(r'[\(\)]', '', regex=True)
    df['年份'] = pd.to_numeric(df['年份'], errors='coerce').astype('Int64')
    return df


def preprocess_year_data(df):
    """
    预处理年份数据，处理缺失值
    
    Args:
        df: 原始DataFrame
        
    Returns:
        DataFrame: 处理后的DataFrame
    """
    df_copy = df.copy()
    # 使用上映时间的前4位填充缺失的年份
    df_copy['年份'] = df_copy['年份'].fillna(df_copy['上映时间'].str[:4])
    return df_copy


def calculate_year_statistics(df):
    """
    计算每年电影数量统计
    
    Args:
        df: 处理后的DataFrame
        
    Returns:
        tuple: (x轴年份列表, y轴数量列表)
    """
    year_count = df.groupby('年份').size()
    
    min_year = year_count.index.min()
    max_year = year_count.index.max()
    
    x = [i for i in range(min_year, max_year + 1)]
    y = [int(year_count.get(i, 0)) for i in x]
    
    return x, y


def plot_year_trend(ax, x, y):
    """
    绘制不同年份电影数量折线图
    
    Args:
        ax: Matplotlib Axes对象
        x: 年份列表
        y: 电影数量列表
    """
    ax.set_title('不同年份电影数量', fontsize=15)
    ax.plot(x, y)
    
    # X轴设置
    ax.set_xlabel('年份')
    ax.set_xticks(x[::10])
    
    # Y轴设置
    ax.set_ylabel('电影数量')
    ax.set_yticks(range(0, 31, 5))
    
    # 网格线
    ax.grid(linestyle='--', alpha=0.3)


def calculate_language_statistics(df):
    """
    计算不同语言电影数量统计
    
    Args:
        df: DataFrame对象
        
    Returns:
        Series: 按数量降序排列的语言统计
    """
    language_count = df.groupby('语言')['语言'].count().sort_values(ascending=False)
    return language_count


def plot_language_distribution(ax, language_count):
    """
    绘制不同语言电影数量柱状图
    
    Args:
        ax: Matplotlib Axes对象
        language_count: 语言统计数据
    """
    ax.bar(language_count.index, language_count.values, width=0.5)
    ax.tick_params(axis='x', rotation=45)
    
    ax.set_title('不同语言电影数量', fontsize=15)
    ax.set_xlabel('语言', fontsize=15)
    ax.set_ylabel('电影数量', fontsize=15)
    ax.grid(linestyle='--', alpha=0.3)


def calculate_type_statistics(df):
    """
    计算不同类型电影数量统计（处理多类型拆分）
    
    Args:
        df: DataFrame对象
        
    Returns:
        Series: 类型统计数据
    """
    # explode将多个类型拆分，value_counts计算数量
    type_count = df['类型'].str.split(',').explode().value_counts()
    return type_count


def plot_type_distribution(ax, type_count):
    """
    绘制不同类型电影数量柱状图
    
    Args:
        ax: Matplotlib Axes对象
        type_count: 类型统计数据
    """
    ax.bar(type_count.index, type_count.values, width=0.4)
    ax.set_title('不同类型电影数量', fontsize=15)
    ax.set_xlabel('类型')
    ax.set_ylabel('电影数量')
    ax.grid(linestyle='--', alpha=0.3)
    ax.tick_params(axis='x', rotation=45)


def calculate_score_statistics(df, threshold=0.02):
    """
    计算电影评分比例统计，合并小数据
    
    Args:
        df: DataFrame对象
        threshold: 小数据阈值（默认2%）
        
    Returns:
        Series: 合并后的评分统计数据
    """
    score_count = df.groupby('评分')['评分'].count()
    total = score_count.sum()
    
    # 分离大数据和小数据
    large_scores = score_count.loc[score_count >= total * threshold]
    small_scores = score_count.loc[score_count < total * threshold]
    
    # 合并小数据为"其他"
    if small_scores.shape[0] > 0:
        large_scores['其他'] = small_scores.sum()
    
    return large_scores


def plot_score_distribution(ax, score_count):
    """
    绘制电影评分比例饼图
    
    Args:
        ax: Matplotlib Axes对象
        score_count: 评分统计数据
    """
    ax.pie(
        score_count,
        labels=score_count.index.tolist(),
        autopct='%1.1f%%',
        startangle=0
    )
    ax.set_title('电影评分的比例',fontsize=15)
    ax.legend(loc='lower center', ncol=4, bbox_to_anchor=(0.2, -0.3))


def create_figure():
    """
    创建画布和子图布局
    
    Returns:
        tuple: (Figure对象, Axes数组)
    """
    figure, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 12), dpi=100)
    figure.suptitle("TMDB-TOP300电影榜单数据统计", fontsize=23, x=0.5, y=0.98)
    figure.subplots_adjust(hspace=0.5, wspace=0.2)
    
    return figure, axes


def main():
    """主函数：执行完整的数据分析流程"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # 1. 配置Matplotlib
    configure_matplotlib()

    # 2. 加载数据
    logger.info("正在加载电影数据...")
    df = load_movie_data()
    logger.info("成功加载 %d 条电影数据", len(df))

    # 3. 预处理数据
    logger.info("正在预处理数据...")
    df_processed = preprocess_year_data(df)

    # 4. 创建画布
    figure, axes = create_figure()

    # 5. 需求1：绘制年份趋势折线图
    logger.info("正在分析年份趋势...")
    x_years, y_counts = calculate_year_statistics(df_processed)
    plot_year_trend(axes[0, 0], x_years, y_counts)

    # 6. 需求2：绘制语言分布柱状图
    logger.info("正在分析语言分布...")
    language_count = calculate_language_statistics(df)
    plot_language_distribution(axes[0, 1], language_count)

    # 7. 需求3：绘制类型分布柱状图
    logger.info("正在分析类型分布...")
    type_count = calculate_type_statistics(df)
    plot_type_distribution(axes[1, 0], type_count)

    # 8. 需求4：绘制评分比例饼图
    logger.info("正在分析评分比例...")
    score_count = calculate_score_statistics(df)
    plot_score_distribution(axes[1, 1], score_count)

    # 9. 保存图表
    output_path = _RESOURCES_DIR / "TMDB-TOP300.jpg"
    logger.info("正在保存图表到 %s...", output_path)
    plt.savefig(str(output_path))
    logger.info("图表已保存！")

    # 10. 显示图表
    logger.info("分析完成！显示图表...")
    try:
        plt.show()
    except AttributeError as e:
        logger.warning("图表显示遇到问题 - %s", e)
        logger.info("提示: 图表已成功保存，您可以在 %s 查看结果", output_path)
        logger.info("如需在PyCharm中正常显示，请尝试以下方法：")
        logger.info("  1. 更新PyCharm到最新版本")
        logger.info("  2. 或在File -> Settings -> Tools -> Python Scientific中取消勾选'Show plots in tool window'")
    logger.info("程序执行完毕！")


if __name__ == '__main__':
    main()
