import time
import re
import os
import fcntl
import socket
import select
import json
from collections import deque
###custom libs
from lib.decision_maker import DecisionMaker
from lib.stats import StatsCollector
from lib.swarming import SwarmManagment
from lib.containering import ContainerManagement
from lib.containering import parse_config
from lib.containering import update_config
from lib.logger import Logger




increment_queue_per_app = deque([])
decrement_queue_per_app = deque([])

host = 'localhost'

######## port 11001 => for orchastrator_adm request
admin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
admin_socket.setblocking(0)
admin_port = 11001
admin_socket.bind((host, admin_port))
admin_socket.listen(5)
######## port 11001 => for orchastrator_adm request

###port 11000 => listen for stats_collector tool
stats_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
stats_port = 11000
stats_socket.bind((host, stats_port))
stats_socket.listen(5)

while True:
	logger = Logger(filename = "orchastrator", logger_name="Orchastrator API")
######## processing admin requests
	# readable, writable, errored = select.select([admin_socket], [], [])
	# logger.info("After")
	# for s in readable:
	# 	if s is server_socket:
	# 		client_socket, address = server_socket.accept()
	# 		read_list.append(client_socket)
	# 		logger.info("Connection from {}".format(address))
	# 	else:
	# 		data = s.recv(1024)
	# 		if data:
	# 			# s.send(data)
	# 			logger.info("DAta from socket on port 11001 => {}".format(data))
	# 		else:
	# 			s.close()
	# 			read_list.remove(s)
	flag = True
	admin_requests = []
	while flag:
		admin_request = None
		try:
			admin_clientsocket, admin_adr = admin_socket.accept()
			logger.info("{} === {}".format(admin_adr[0], admin_adr[1]))
			admin_request = admin_clientsocket.recv(1024).decode()
		except BlockingIOError:
			logger.info("There aren't any request from orchastrator_adm"\
						" in the admin_socket on port 11001")
		if admin_request:
			admin_requests.append(admin_request)
			logger.info("Received command from orchastrator_adm => {}".format(admin_request))
		else:
			logger.info("No requests from orchastrator_adm")
			flag = False
######## processing admin_requests

	stats_clientsocket,addr = stats_socket.accept()
########
	stats_clientsocket.sendall("Give me stats".encode('utf-8'))
	logger.info("Asking for stats from stats_collector")
########
	b = b''
	containers_stats = stats_clientsocket.recv(1024)
	if containers_stats:
		b += containers_stats
		containers_stats = json.loads(b.decode('utf-8'))
		logger.info("Received stats by stats_collector => {}".format(containers_stats))
	stats_clientsocket.close()


	logger.info("QUEUE for increment app => {}".format(increment_queue_per_app))
	logger.info("QUEUE for decrement app => {}".format(decrement_queue_per_app))
	decision_maker = DecisionMaker()
	swarm_manager = SwarmManagment()
	container_manager = ContainerManagement()
	app_for_incremnting = None
	app_for_decrementing = None


####for admin request tool
	# print(decision_maker.release_node('10.102.7.124'))

####for admin request tool


###Running container if minimum quota is not applied
	apps_count = decision_maker.calculating_app_on_hosts()
	for app in apps_count:
		min_app = "{}_min".format(app)
		while apps_count[app] < parse_config('orchastrator.json')[min_app]:
			logger.info("Running container from app {} because of minimum quota limitation".format(app))
			host = decision_maker.making_host_decision(app, decision = 'up')
			container_manager.run_container(host_ip = host, application = app)
			###new object to take the new platform configuration
			decision_maker = DecisionMaker()
			container_manager = ContainerManagement()
			###new object to take the new platform configuration
			apps_count = decision_maker.calculating_app_on_hosts()
			logger.info("Appps count => {}".format(apps_count))
			time.sleep(10)
###Running container if minimum quota is not applied

	for host in containers_stats:
		for container in containers_stats[host]:
			if re.search(r"registry", container, re.I|re.S):
				break 
			# print("Container => {} Stats => {}".format(container, containers_stats[host][container]))
			if containers_stats[host][container]["CPU"] > 60 :
				app_for_incremnting = re.sub('\_\d+', "", container)
				if app_for_incremnting not in increment_queue_per_app:
					increment_queue_per_app.append(app_for_incremnting)
				logger.info("CPU {} > 60% => Container {} from application {} should be runned". \
					format(containers_stats[host][container]["CPU"], container, app_for_incremnting))
				# break
			elif containers_stats[host][container]["CPU"] < 20:
				app_for_decrementing = re.sub('\_\d+', "", container)
				if app_for_decrementing not in decrement_queue_per_app:
					decrement_queue_per_app.append(app_for_decrementing)
				logger.info("CPU {} < 20% => Container {} from application {} should be stopped". \
					format(containers_stats[host][container]["CPU"], container, app_for_decrementing))
				# print("Container from application {} should be stopped".format(app_for_decrementing))
				# break
		# if app_for_incremnting or app_for_decrementing:
	# 	# 	break
	# print("2 QUEUE for increment app => {}".format(increment_queue_per_app))
	# print("2 QUEUE for decrement app => {}".format(decrement_queue_per_app))
	logger.info("2 QUEUE for increment app => {}".format(increment_queue_per_app))
	logger.info("2 QUEUE for decrement app => {}".format(decrement_queue_per_app))



	if increment_queue_per_app:
		app_for_incremnting = increment_queue_per_app.popleft()
		# print("App for increment => {}".format(app_for_incremnting))
		host = decision_maker.making_host_decision(app_for_incremnting, decision = 'up')
		logger.info("App for increment => {} on host => {}".format(app_for_incremnting, host))
		container_manager.run_container(host_ip = host, application = app_for_incremnting)
	elif decrement_queue_per_app:
		app_for_decrementing = decrement_queue_per_app.popleft()
		# print("App for decrement => {}".format(app_for_decrementing))
		host = decision_maker.making_host_decision(app_for_decrementing, decision = 'down')
		# logger.info("App for decrement => {} on host {}".format(app_for_decrementing, host))
		# print("Host => {}".format(host))
		if host is None:
			# print("Can't stop container, minimal application number is running!")
			logger.info("Can't stop container, minimal application number is running!")

		if host is not None:
			highest_cpu_stat = 0
			container_name = None
			for container in containers_stats[host].keys():
				if re.search(r'{}'.format(app_for_decrementing), container):
					if containers_stats[host][container]['CPU'] > highest_cpu_stat:
						container_name = container
						highest_cpu_stat = containers_stats[host][container]['CPU']
			# print("Container name => {}".format(container_name))
			if container_name is not None:
				container_manager.stop_container(name = container_name, host_ip = host)
				logger.info("Container name => {} will be stopped on host => {}".format(container_name, host))


	# print("Waiting 30 seconds for the next cycle")
	logger.info("Waiting 30 seconds for the next cycle")
	logger.clear_handler()
	time.sleep(30)