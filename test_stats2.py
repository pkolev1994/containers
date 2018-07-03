from lib.stats2 import StatsCollector
import time


statistic = StatsCollector(username = 'root', password = '0penc0de')


while True:
	curr = time.time()
	statistic.collect_stats()
	print("Time is {}".format(time.time() - curr))