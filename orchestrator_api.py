import time
import re
from collections import deque
###custom libs
from lib.decision_maker import DecisionMaker
from lib.stats import StatsCollector
from lib.swarming import SwarmManagment
from lib.containering import ContainerManagement
from lib.containering import parse_config
from lib.containering import update_config


# stats_collector = StatsCollector()
# decision_maker = DecisionMaker()
# swarm_manager = SwarmManagment()
# container_manager = ContainerManagement()


increment_queue_per_app = deque([])
decrement_queue_per_app = deque([])

while True:

	print("QUEUE for increment app => {}".format(increment_queue_per_app))
	print("QUEUE for decrement app => {}".format(decrement_queue_per_app))

	stats_collector = StatsCollector()
	decision_maker = DecisionMaker()
	swarm_manager = SwarmManagment()
	container_manager = ContainerManagement()
	app_for_incremnting = None
	app_for_decrementing = None
	containers_stats = stats_collector.parsed_stats()
	print("Stats of containers are taken  => {}".format(containers_stats))
	for host in containers_stats:
		for container in containers_stats[host]:
			if re.search(r"registry", container, re.I|re.S):
				break 
			print("Container => {} Stats => {}".format(container, containers_stats[host][container]))
			if containers_stats[host][container]["CPU"] > 60 :
				app_for_incremnting = re.sub('\_\d+', "", container)
				if app_for_incremnting not in increment_queue_per_app:
					increment_queue_per_app.append(app_for_incremnting)
				print("Container from application {} should be runned".format(app_for_incremnting))
				# break
			elif containers_stats[host][container]["CPU"] < 20:
				app_for_decrementing = re.sub('\_\d+', "", container)
				if app_for_decrementing not in decrement_queue_per_app:
					decrement_queue_per_app.append(app_for_decrementing)
				print("Container from application {} should be stopped".format(app_for_decrementing))
				# break
		# if app_for_incremnting or app_for_decrementing:
		# 	break
	print("2 QUEUE for increment app => {}".format(increment_queue_per_app))
	print("2 QUEUE for decrement app => {}".format(decrement_queue_per_app))


	if increment_queue_per_app:
		app_for_incremnting = increment_queue_per_app.popleft()
		print("II => {}".format(app_for_incremnting))
		host = decision_maker.making_host_decision(app_for_incremnting, decision = 'up')
		container_manager.run_container(host_ip = host, application = app_for_incremnting)
	elif decrement_queue_per_app:
		app_for_decrementing = decrement_queue_per_app.popleft()
		print("DD => {}".format(app_for_decrementing))
		host = decision_maker.making_host_decision(app_for_decrementing, decision = 'down')

		if host is None:
			print("Can't stop container, minimal application number is running!")

		if host is not None:
			highest_cpu_stat = 0
			container_name = None
			for container in containers_stats[host].keys():
				if containers_stats[host][container]['CPU'] > highest_cpu_stat:
					container_name = container
					highest_cpu_stat = containers_stats[host][container]['CPU']
			print("Container name => {}".format(container_name))
			if container_name is not None:
				container_manager.stop_container(name = container_name, host_ip = host)

	print("Waiting 30 seconds for the next cycle")
	time.sleep(30)


