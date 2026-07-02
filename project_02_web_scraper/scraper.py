"""scraper.py — TMDB 电影榜单爬虫（改进版）

改进点：
1. 移除 verify=False，启用 SSL 证书验证（TMDB 有合法证书）
2. POST 参数日期动态计算，不再硬编码过期时间戳
3. 配置分离到 config.py，XPath/URL 集中管理
4. 用 logging 替代 print，支持命令行控制日志级别
5. 支持 argparse 命令行参数（页码范围 / 输出路径 / 延时等）

用法:
    python scraper.py                          # 默认爬 1-5 页
    python scraper.py --start-page 1 --end-page 10  # 爬 1-10 页
    python scraper.py -o my_movies.csv               # 指定输出文件
    python scraper.py --delay 1.5                    # 调快延时
    python scraper.py -v                              # verbose 模式
"""

import argparse
import csv
import logging
import time
from pathlib import Path

import requests
from lxml import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

# ── 日志 ──────────────────────────────────────────────
logger = logging.getLogger("scraper")

# ── HTTP 会话 ──────────────────────────────────────────
def create_session() -> requests.Session:
    """创建带重试策略的 requests 会话。"""
    session = requests.Session()
    session.headers.update(config.HEADERS)
    session.verify = config.VERIFY_SSL
    retry_strategy = Retry(
        total=config.RETRY_TOTAL,
        backoff_factor=config.RETRY_BACKOFF_FACTOR,
        status_forcelist=config.RETRY_STATUS_FORCELIST,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# ── 电影详情解析 ──────────────────────────────────────
def parse_movie_detail(html_tree) -> dict[str, str]:
    """从电影详情页 HTML 树中提取所有字段。

    使用 config.MOVIE_XPATH 字典进行批量解析，
    对多值字段（类型、主演）用逗号拼接，
    对单值字段取首个结果。
    """
    info: dict[str, str] = {}

    for field, xpath in config.MOVIE_XPATH.items():
        results = html_tree.xpath(xpath)
        if not results:
            info[field] = ""
            continue

        # 多值字段：逗号拼接
        if field in ("类型", "主演"):
            info[field] = ",".join(r.strip() for r in results if r.strip())
        else:
            info[field] = str(results[0]).strip()

    return info


def fetch_movie_info(movie_url: str, session: requests.Session) -> dict[str, str] | None:
    """请求单部电影详情页并解析。

    Returns:
        电影信息字典；失败时返回 None。
    """
    try:
        logger.debug("请求详情: %s", movie_url)
        resp = session.get(movie_url, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()

        tree = html.fromstring(resp.text)
        info = parse_movie_detail(tree)
        logger.debug("解析成功: %s", info.get("电影名", "?"))
        return info

    except requests.RequestException as e:
        logger.warning("请求失败 %s: %s", movie_url, e)
    except Exception as e:
        logger.warning("解析失败 %s: %s", movie_url, e)

    return None


# ── CSV 保存 ───────────────────────────────────────────
def save_movies(movies: list[dict], output_path: Path) -> None:
    """将电影数据保存为 UTF-8-BOM CSV。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=config.CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(movies)
    logger.info("已保存 %d 部电影 → %s", len(movies), output_path)


# ── 主流程 ─────────────────────────────────────────────
def run(
    start_page: int = config.DEFAULT_START_PAGE,
    end_page: int = config.DEFAULT_END_PAGE,
    output_path: Path | None = None,
    movie_delay: float = config.MOVIE_DELAY,
    page_delay: float = config.PAGE_DELAY,
) -> list[dict]:
    """执行爬取主逻辑。

    Args:
        start_page: 起始页码（1-based）
        end_page: 结束页码（含）
        output_path: CSV 输出路径；None 时使用默认值
        movie_delay: 每部电影间延时（秒）
        page_delay: 每页间延时（秒）

    Returns:
        爬取到的所有电影数据列表。
    """
    if output_path is None:
        output_path = config.OUTPUT_FILE

    all_movies: list[dict] = []
    session = create_session()

    total_pages = end_page - start_page + 1
    logger.info("开始爬取 TMDB Top Rated: 第 %d → %d 页（共 %d 页）", start_page, end_page, total_pages)

    try:
        for page_num in range(start_page, end_page + 1):
            logger.info("━ 第 %d/%d 页 ━", page_num, end_page)

            try:
                # 第 1 页用 GET，其余页用 POST
                if page_num == 1:
                    resp = session.get(
                        config.TMDB_TOP_URL_1,
                        timeout=config.REQUEST_TIMEOUT,
                    )
                else:
                    body = config.build_discover_params(page_num)
                    resp = session.post(
                        config.TMDB_TOP_URL_2,
                        data=body,
                        timeout=config.REQUEST_TIMEOUT,
                    )

                resp.raise_for_status()
                tree = html.fromstring(resp.text)

                # 提取卡片列表
                cards = tree.xpath(config.POSTER_CARD_XPATH)
                logger.info("本页发现 %d 个卡片", len(cards))

                for card in cards:
                    links = card.xpath(config.POSTER_LINK_XPATH)
                    if not links:
                        continue

                    movie_path = links[0].strip("/")
                    movie_url = f"{config.TMDB_BASE_URL.rstrip('/')}/{movie_path}"

                    info = fetch_movie_info(movie_url, session)
                    if info:
                        all_movies.append(info)

                    time.sleep(movie_delay)

                logger.info("第 %d 页完成，已累计 %d 部", page_num, len(all_movies))
                time.sleep(page_delay)

            except requests.RequestException as e:
                logger.error("第 %d 页请求失败: %s", page_num, e)
                continue
            except Exception as e:
                logger.error("第 %d 页处理异常: %s", page_num, e)
                continue

    except KeyboardInterrupt:
        logger.warning("用户中断，正在保存已爬取的数据...")
    finally:
        session.close()
        if all_movies:
            save_movies(all_movies, output_path)
        else:
            logger.warning("未获取到任何电影数据！")

    return all_movies


# ── CLI 入口 ───────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="TMDB 电影榜单爬虫 — 抓取 Top Rated 电影数据并导出 CSV",
    )
    parser.add_argument(
        "--start-page", type=int, default=config.DEFAULT_START_PAGE,
        help=f"起始页码（默认: {config.DEFAULT_START_PAGE}）",
    )
    parser.add_argument(
        "--end-page", type=int, default=config.DEFAULT_END_PAGE,
        help=f"结束页码（默认: {config.DEFAULT_END_PAGE}）",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=config.OUTPUT_FILE,
        help=f"CSV 输出路径（默认: {config.OUTPUT_FILE}）",
    )
    parser.add_argument(
        "--delay", type=float, default=config.MOVIE_DELAY,
        help=f"每部电影间延时/秒（默认: {config.MOVIE_DELAY}）",
    )
    parser.add_argument(
        "--page-delay", type=float, default=config.PAGE_DELAY,
        help=f"每页间延时/秒（默认: {config.PAGE_DELAY}）",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="详细日志（DEBUG 级别）",
    )

    args = parser.parse_args()

    # 日志配置
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # 参数校验
    if args.start_page < 1:
        logger.error("起始页码必须 ≥ 1")
        return
    if args.end_page < args.start_page:
        logger.error("结束页码不能小于起始页码")
        return

    run(
        start_page=args.start_page,
        end_page=args.end_page,
        output_path=args.output,
        movie_delay=args.delay,
        page_delay=args.page_delay,
    )


if __name__ == "__main__":
    main()
