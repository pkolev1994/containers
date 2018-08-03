import time
import re
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

while True:

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
			print("Container => {} Stats => {}".format(container, containers_stats[host][container]))
			if containers_stats[host][container]["CPU"] > 60 :
				app_for_incremnting = re.sub('\_\d+', "", container)
				print("Container from application {} should be runned".format(app_for_incremnting))
				break
			elif containers_stats[host][container]["CPU"] < 2:
				app_for_decrementing = re.sub('\_\d+', "", container)
				print("Container from application {} should be stopped".format(app_for_decrementing))
				break
		if app_for_incremnting or app_for_decrementing:
			break

	if app_for_incremnting:
		host = decision_maker.making_host_decision(app_for_incremnting, decision = 'up')
		container_manager.run_container(host_ip = host, application = app_for_incremnting)
	elif app_for_decrementing:
		host = decision_maker.making_host_decision(app_for_decrementing, decision = 'down')
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


