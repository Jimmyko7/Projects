# Project 2 — TMDB 电影榜单爬虫

从 TMDB（The Movie Database）抓取 Top 300 电影数据。

## 功能

- 爬取 TMDB Top 300 电影榜单
- 解析：片名、年份、类型、时长、评分、语言、导演、简介
- XPath 精确定位 + CSV 导出

## 技术栈

- **HTTP**: requests · **解析**: lxml + XPath · **输出**: CSV

## 运行

```bash
python project_02_web_scraper/scraper.py
```
