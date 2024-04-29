'''
定时任务
'''

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config_parser import read_config
from capturer import Capturer

def create_scheduler(capturer: Capturer, interval_seconds=2):
    # 创建调度器实例
    scheduler = BackgroundScheduler()

    # 设置定时任务
    interval_seconds = 2  # 调整为所需的间隔时间
    scheduler.add_job(
        func=Capturer.run_once,  # 任务函数
        args=[capturer],  # 任务参数
        trigger=IntervalTrigger(seconds=interval_seconds),  # 触发器类型及参数
        id='data_collection',  # 作业ID 用于唯一标识该任务
        max_instances=1,  # 最大并发实例数 设为1避免重复执行
        replace_existing=True,  # 如果同名作业已存在 则替换之
    )

    return scheduler

class Scheduler:
    def __init__(self, config_path):
        self.capture_config, db_config, modules, modules_max = read_config(config_path)
        self.capturer = Capturer(db_config, modules, modules_max)
        self.scheduler = create_scheduler(self.capturer, self.capture_config['seconds'])
        print('Scheduler created')

    def start(self):
        print('Scheduler starting')
        self.scheduler.start()

    def shutdown(self):
        print('Scheduler shutting down')
        self.scheduler.shutdown()

