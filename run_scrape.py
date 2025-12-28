#!/usr/bin/env python
"""
手动执行爬取任务的脚本
"""
from src.scheduler.tasks import ScrapeTask

if __name__ == "__main__":
    print("开始执行爬取任务...")
    task = ScrapeTask()
    task.scrape_all()
    print("爬取任务完成！")

