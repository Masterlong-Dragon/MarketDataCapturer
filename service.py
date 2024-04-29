'''
数据采集程序
'''

from datetime import datetime
from time import sleep
from scheduler import Scheduler

if __name__ == '__main__':
    scheduler = Scheduler('config.ini')
    scheduler.start()
    try:
        while True:
            # 降低cpu占用率
            print('Main thread is running at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sleep(1)
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
        print('Scheduler shutdowned')