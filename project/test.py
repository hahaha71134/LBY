import datetime
import parser
import time

import timestring as timestring

now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
print(now_time)
a='2018-12-30 10:12'
b='2018-12-30 10:11'
print(time.mktime(time.strptime(a, '%Y-%m-%d %H:%M'))-time.mktime(time.strptime(b, '%Y-%m-%d %H:%M')))