import csv
import requests
from lxml import html
import time
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 常量
MOVIE_LIST_FILE = "csv_files/movie_list.csv"
TMDB_BASE_URL = "https://www.themoviedb.org/"
TMDB_TOP_URL_1 = "https://www.themoviedb.org/movie/top-rated"
TMDB_TOP_URL_2 = "https://www.themoviedb.org/discover/movie/items"

# 设置请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.themoviedb.org/",
}


# 创建会话，配置重试策略
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # 最大重试次数
        backoff_factor=2,  # 重试间隔: 2s, 4s, 8s
        status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# 获取电影详情数据
def get_movie_info(movie_info_url, session):
    try:
        # 1.发送请求，获取影详情数据
        movie_response = session.get(
            movie_info_url,
            headers=HEADERS,
            timeout=60,
            verify=False
        )
        movie_response.raise_for_status()
        print(f"发送请求{movie_info_url},获取电影详情数据....")

        # 2.解析数据，获取电影详情
        movie_document = html.fromstring(movie_response.text)
        # 电影名
        movie_names = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()")
        # 电影年份
        movie_years = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/span/text()")
        # 上映时间
        movie_dates = movie_document.xpath(
            "//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='release']/text()")
        # 类型
        movie_types = movie_document.xpath(
            "//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='genres']/a/text()")
        # 时长
        movie_times = movie_document.xpath(
            "//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='runtime']/text()")
        # 评分
        movie_scores = movie_document.xpath("//*[@id='consensus_pill']/div/div[1]/div/div/@data-percent")
        # 语言
        movie_languages = movie_document.xpath(
            "//*[@id='media_v4']/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()")
        # 导演
        movie_directors = movie_document.xpath(
            "//*[@id='original_header']/div[2]/section/div[3]/ol/li[1]/p[1]/a/text()")
        # 作者
        movie_authors = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[2]/p[1]/a/text()")
        # 主演
        movie_actors = movie_document.xpath("//*[@id='cast_scroller']/ol/li[1]/p[1]/a/text()")
        # Slogan
        movie_slogans = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[3]/h3[1]/text()")
        # 简介
        movie_details = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[3]/div/p/text()")
        # 3.返回电影详情数据 - 字典
        movie_info = {
            "电影名": movie_names[0].strip() if movie_names else "",
            "年份": movie_years[0].strip() if movie_years else "",
            "上映时间": movie_dates[0].strip() if movie_dates else "",
            "类型": ",".join(movie_types) if movie_types else "",
            "时长": movie_times[0].strip() if movie_times else "",
            "评分": movie_scores[0].strip() if movie_scores else "",
            "语言": movie_languages[0].strip() if movie_languages else "",
            "导演": movie_directors[0].strip() if movie_directors else "",
            "作者": movie_authors[0].strip() if movie_authors else "",
            "主演": ",".join(movie_actors) if movie_actors else "",
            "Slogan": movie_slogans[0].strip() if movie_slogans else "",
            "简介": movie_details[0].strip() if movie_details else "",
        }
        return movie_info
    except Exception as e:
        print(f"获取电影详情失败: {movie_info_url}, 错误: {e}")
        return None


# 保存电影数据
def save_all_movies(all_movies):
    with open(MOVIE_LIST_FILE, "w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=["电影名", "年份", "上映时间", "类型", "时长", "评分", "语言", "导演",
                                            "作者", "主演", "Slogan", "简介"])
        writer.writeheader()  # 写入表头
        writer.writerows(all_movies)  # 写入数据
        print("保存电影数据成功！")


# 主函数
def main():
    all_movies = []  # 保存所有电影数据

    # 创建会话
    session = create_session()

    # 循环获取从第1页到第5页的电影数据
    for page_num in range(1, 6):
        try:
            # 1.发送请求。获取高分电影榜单数据
            if page_num == 1:
                response = session.get(
                    TMDB_TOP_URL_1,
                    headers=HEADERS,
                    timeout=60,
                    verify=False
                )
            else:
                response = session.post(
                    TMDB_TOP_URL_2,
                    f"air_date.gte=&air_date.lte=&certification=&certification_country=CN&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&include_softcore=false&latest_ceremony.gte=&latest_ceremony.lte=&page={page_num}&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2026-10-21&show_me=everything&sort_by=vote_average.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=300&watch_region=CN&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400",
                    headers=HEADERS,
                    timeout=60,
                    verify=False
                )

            response.raise_for_status()
            print("发送请求,获取TMDB电影榜单数据")

            # 2.解析数据，获取电影列表
            document = html.fromstring(response.text)
            movie_list = document.xpath("//div[contains(@class, 'poster-card')]")

            # 3.遍历电影列表，获取电影详情
            for mv in movie_list:
                # 获取a里的超链接href
                movie_urls = mv.xpath("./div/div/a/@href")
                if movie_urls:
                    # 电影详情的url - 修复URL拼接问题，避免双斜杠
                    movie_path = movie_urls[0].strip("/")
                    movie_info_url = f"{TMDB_BASE_URL.rstrip('/')}/{movie_path}"
                    # 发送请求，获取电影详情数据
                    movie_info = get_movie_info(movie_info_url, session)
                    if movie_info:
                        all_movies.append(movie_info)

                    # 增加延时，避免请求过快
                    time.sleep(2)

            print(f"第{page_num}页处理完成,共获取{len(all_movies)}部电影")
            time.sleep(3)

        except Exception as e:
            print(f"第{page_num}页获取失败,错误: {e}")
            continue

    # 4.保存数据，保存为csv文件
    print("获取到所有电影详情,保存到csv文件")
    save_all_movies(all_movies)

    # 关闭会话
    session.close()


if __name__ == '__main__':
    main()
