from lib.stats import StatsCollector
import time


statistic = StatsCollector()


while True:
	curr = time.time()
	# print(statistic.collect_stats())
	# print("\n\n\n\n")
	# print("Processes => {}".format(statistic.show_processes()))
	print("STATS => {}".format(statistic.parsed_stats()))
	print("Prety => {}".format(statistic.show_stats()))
	print("Prety processes => {}".format(statistic.show_processes()))
	print("Time is {}".format(time.time() - curr))
