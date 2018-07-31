import time
from lib.orchastration import PlatformOrchastration


###old way 
# orchastrator = PlatformOrchastration(available_servers = ['10.102.7.124'], \
# 									swarm_servers = ['10.102.7.123', '10.102.7.122'], \
# 									user = 'root', \
# 									password = '0penc0de', \
# 									master_nodes = ['10.102.7.122'], \
# 									token = 'SWMTKN-1-3sbwti51l06awsw6bsqer4s6wz5yvkb8l90g2vgmbo1wlhqvoe-d0dilgpmh7wliu4pjx7mo158x', \
# 									master = '10.102.7.122')



orchastrator = PlatformOrchastration()



print("Servers 1=> {}\n\n\n".format(orchastrator.available_servers))
while True:
	orchastrator.add_server('10.10.01.111')
	print("LL AA {}".format(orchastrator.list_available_servers()))
	print("Servers 1=> {}\n\n\n".format(orchastrator.available_servers))
	print("CONT => {}".format(orchastrator.take_containers_stats()))
	print("\n\n\n\nIPS in swarm => {}\n\n\n\n".format(orchastrator.list_nodes_ips()))
	time.sleep(33)