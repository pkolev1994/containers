from lib.stats import StatsCollector
import time


statistic = StatsCollector()


while True:
	curr = time.time()
	statistic.collect_stats()
	print("Time is {}".format(time.time() - curr))