"""config.py — TMDB 爬虫配置常量
将所有硬编码的 URL、XPath、请求参数集中管理，便于维护和网站改版后快速适配。
"""

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

# ── 基础路径 ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "csv_files"
OUTPUT_FILE = OUTPUT_DIR / "movies.csv"

# ── TMDB URL ──────────────────────────────────────────
TMDB_BASE_URL = "https://www.themoviedb.org"
TMDB_TOP_URL_1 = f"{TMDB_BASE_URL}/movie/top-rated"
TMDB_TOP_URL_2 = f"{TMDB_BASE_URL}/discover/movie/items"

# ── 请求头 ────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.themoviedb.org/",
}

# ── 请求参数 ──────────────────────────────────────────
REQUEST_TIMEOUT = 60          # 单次请求超时（秒）
PAGE_DELAY = 3                # 页间延时（秒）
MOVIE_DELAY = 2               # 每部电影间延时（秒）
VERIFY_SSL = True             # SSL 证书验证（网络兼容问题时临时设为 False）

# 重试策略
RETRY_TOTAL = 3
RETRY_BACKOFF_FACTOR = 2
RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]

# 爬取范围默认值
DEFAULT_START_PAGE = 1
DEFAULT_END_PAGE = 5

# ── XPath 选择器 ──────────────────────────────────────
# 榜单页 – 卡片列表
POSTER_CARD_XPATH = '//div[contains(@class, "poster-card")]'
POSTER_LINK_XPATH = "./div/div/a/@href"

# 详情页 – 各字段选择器（按 CSV 字段名映射）
MOVIE_XPATH = {
    "电影名": '//*[@id="original_header"]/div[2]/section/div[1]/h2/a/text()',
    "年份":   '//*[@id="original_header"]/div[2]/section/div[1]/h2/span/text()',
    "上映时间": '//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="release"]/text()',
    "类型":   '//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="genres"]/a/text()',
    "时长":   '//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="runtime"]/text()',
    "评分":   '//*[@id="consensus_pill"]/div/div[1]/div/div/@data-percent',
    "语言":   '//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()',
    "导演":   '//*[@id="original_header"]/div[2]/section/div[3]/ol/li[1]/p[1]/a/text()',
    "作者":   '//*[@id="original_header"]/div[2]/section/div[3]/ol/li[2]/p[1]/a/text()',
    "主演":   '//*[@id="cast_scroller"]/ol/li[1]/p[1]/a/text()',
    "Slogan": '//*[@id="original_header"]/div[2]/section/div[3]/h3[1]/text()',
    "简介":   '//*[@id="original_header"]/div[2]/section/div[3]/div/p/text()',
}

# CSV 字段顺序
CSV_FIELDNAMES = [
    "电影名", "年份", "上映时间", "类型", "时长",
    "评分", "语言", "导演", "作者", "主演", "Slogan", "简介",
]


def build_discover_params(page: int) -> str:
    """构建 TMDB discover/movie/items POST 查询参数。

    日期字段动态计算（release_date.lte = 一年后），不再硬编码。
    所有空字符串参数为 TMDB API 可选过滤项。
    """
    today = date.today()
    release_lte = (today + timedelta(days=365)).isoformat()

    params = {
        "air_date.gte": "",
        "air_date.lte": "",
        "certification": "",
        "certification_country": "CN",
        "debug": "",
        "first_air_date.gte": "",
        "first_air_date.lte": "",
        "include_adult": "false",
        "include_softcore": "false",
        "latest_ceremony.gte": "",
        "latest_ceremony.lte": "",
        "page": page,
        "primary_release_date.gte": "",
        "primary_release_date.lte": "",
        "region": "",
        "release_date.gte": "",
        "release_date.lte": release_lte,
        "show_me": "everything",
        "sort_by": "vote_average.desc",
        "vote_average.gte": "0",
        "vote_average.lte": "10",
        "vote_count.gte": "300",
        "watch_region": "CN",
        "with_genres": "",
        "with_keywords": "",
        "with_networks": "",
        "with_origin_country": "",
        "with_original_language": "",
        "with_watch_monetization_types": "",
        "with_watch_providers": "",
        "with_release_type": "",
        "with_runtime.gte": "0",
        "with_runtime.lte": "400",
    }
    return urlencode(params)
