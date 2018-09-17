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
from lib.etcd_client import EtcdManagement



def get_obj_instances():
	"""
	Returns:
		tuple
	"""
	return (DecisionMaker(), \
			SwarmManagment(), \
			ContainerManagement(), \
			Logger(filename = "orchastrator", logger_name="Orchastrator API"))



def processing_admin_requests(admin_socket, decision_maker, container_manager, logger):
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
	if admin_requests:
		for req in admin_requests:
			if re.search(r'stop', req, flags=re.I|re.S):
				# logger.info("====> {}".format(req))
				match = re.match(r'stop\s+(.+?)\s+(.+?$)', req, flags=re.I|re.S)
				logger.info("Container => {} on host => {} will be stopped by admin request". \
					format(match.group(1), match.group(2)))
				container_manager.stop_container(host_ip = match.group(2), name = match.group(1))
			elif re.search(r'start', req, flags=re.I|re.S):
				# logger.info("====> {}".format(req))
				match = re.match(r'start\s+(.+?)\s+(.+?$)', req, flags=re.I|re.S)
				logger.info("Container => {} on host => {} will be started by admin request". \
					format(match.group(1), match.group(2)))
				container_manager.run_container(host_ip = match.group(2), application = match.group(1))
			elif re.search(r'release', req, flags=re.I|re.S):
				match = re.match(r'release\s+(.+?$)', req, flags=re.I|re.S)
				logger.info("Node => {} will be released by admin request".format(match.group(1)))
				decision_maker.release_node(match.group(1))

	return DecisionMaker()


def processing_stats(stats_socket, logger):

	stats_clientsocket,addr = stats_socket.accept()
	stats_clientsocket.sendall("Give me stats".encode('utf-8'))
	logger.info("Asking for stats from stats_collector")
	b = b''
	containers_stats = stats_clientsocket.recv(1024)
	if containers_stats:
		b += containers_stats
		containers_stats = json.loads(b.decode('utf-8'))
		logger.info("Received stats by stats_collector => {}".format(containers_stats))
	stats_clientsocket.close()

	return containers_stats




def looking_for_minimum_quota(decision_maker, container_manager, logger):

	apps_count = decision_maker.calculating_app_on_hosts()
	logger.info("Platform => {}".format(decision_maker.update_platform_status()))
	etcd_manager = EtcdManagement()
	for app in apps_count:
		min_app = "{}_min".format(app)
###orchastrator.json way
		# while apps_count[app] < parse_config('orchastrator.json')[min_app]:
###orchastrator.json way
###etcd way
		while apps_count[app] < etcd_manager.get_etcd_config()[min_app]:
###etcd way
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

	return DecisionMaker()


def filling_queues(containers_stats, logger, increment_queue_per_app, decrement_queue_per_app):


	for host in containers_stats:
		for container in containers_stats[host]:
			if re.search(r"registry", container, re.I|re.S):
				break 
			if containers_stats[host][container]["CPU"] > 60 :
				app_for_incremnting = re.sub('\_\d+', "", container)
				if app_for_incremnting not in increment_queue_per_app:
					increment_queue_per_app.append(app_for_incremnting)
				logger.info("CPU {} > 60% => Container {} from application {} should be runned". \
					format(containers_stats[host][container]["CPU"], container, app_for_incremnting))
			elif containers_stats[host][container]["CPU"] < 20:
				app_for_decrementing = re.sub('\_\d+', "", container)
				if app_for_decrementing not in decrement_queue_per_app:
					decrement_queue_per_app.append(app_for_decrementing)
				logger.info("CPU {} < 20% => Container {} from application {} should be stopped". \
					format(containers_stats[host][container]["CPU"], container, app_for_decrementing))

	return (increment_queue_per_app, decrement_queue_per_app)


def processing_queues(increment_queue_per_app, \
					decrement_queue_per_app, \
					container_manager, \
					logger, \
					decision_maker, \
					containers_stats):


	if increment_queue_per_app:
		app_for_incremnting = increment_queue_per_app.popleft()
		host = decision_maker.making_host_decision(app_for_incremnting, decision = 'up')
		logger.info("App for increment => {} on host => {}".format(app_for_incremnting, host))
		container_manager.run_container(host_ip = host, application = app_for_incremnting)
	elif decrement_queue_per_app:
		app_for_decrementing = decrement_queue_per_app.popleft()
		host = decision_maker.making_host_decision(app_for_decrementing, decision = 'down')

		if host is not None:
			highest_cpu_stat = 0
			container_name = None
			for container in containers_stats[host].keys():
				if re.search(r'{}'.format(app_for_decrementing), container):
					if containers_stats[host][container]['CPU'] > highest_cpu_stat:
						container_name = container
						highest_cpu_stat = containers_stats[host][container]['CPU']
			if container_name is not None:
				container_manager.stop_container(name = container_name, host_ip = host)
				logger.info("Container name => {} will be stopped on host => {}".format(container_name, host))
		else:
			logger.info("Can't stop container, minimal application number is running!")
			node_for_releasing = decision_maker.check_for_releasing_node()
			if node_for_releasing:
				logger.info("Node {} will be released by the orchastrator api".format(node_for_releasing))
				decision_maker.release_node(host = node_for_releasing)	
			else:
				logger.info("There isn't any node that can be released from the orchastrator api")

	return (increment_queue_per_app, decrement_queue_per_app)



def main():

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

	######## port 11000 => listen for stats_collector tool
	stats_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	stats_port = 11000
	stats_socket.bind((host, stats_port))
	stats_socket.listen(5)
	while True:
		decision_maker, swarm_manager, container_manager, logger = get_obj_instances()
		app_for_incremnting = None
		app_for_decrementing = None
	######## processing admin requests
		logger.info("11 => {}".format(decision_maker.apps_by_hosts))
		decision_maker = processing_admin_requests(admin_socket, decision_maker, container_manager, logger)
		logger.info("22 => {}".format(decision_maker.apps_by_hosts))
	######## processing admin_requests

	###Running container if minimum quota is not applied
		decision_maker = looking_for_minimum_quota(decision_maker, container_manager, logger)
	###Running container if minimum quota is not applied

	#######processing stats from stats socket
		containers_stats = processing_stats(stats_socket, logger)
	#######processing stats from stats socket

	#######filling queues
		increment_queue_per_app, decrement_queue_per_app = filling_queues(containers_stats, \
																		logger, \
																		increment_queue_per_app, \
																		decrement_queue_per_app)
	#######filling queues

		logger.info("2 QUEUE for increment app => {}".format(increment_queue_per_app))
		logger.info("2 QUEUE for decrement app => {}".format(decrement_queue_per_app))
		increment_queue_per_app, decrement_queue_per_app = processing_queues(increment_queue_per_app, \
																			decrement_queue_per_app, \
																			container_manager, \
																			logger, \
																			decision_maker, \
																			containers_stats)
		logger.info("Waiting 30 seconds for the next cycle")
		logger.clear_handler()
		time.sleep(30)



main()