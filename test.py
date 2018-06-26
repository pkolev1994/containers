from lib.nodeconnection import Node

import paramiko
import time
import scp

user = 'root'
password = '0penc0de'

ll = ['10.102.7.122', '10.102.7.124']


start_time = time.time()
nodes = []
for nn in ll:
	i = Node(address=nn, user=user, password=password)
	print("Connected  ==> {} <==".format(i))
	# i.join()
	# nodes.append(i)
for j in nodes:
	print("Outt CONN => {}".format(j.output))
	j.join()
	# print("Outt => {}".format(j.output))

print("Time 1 => {}".format(time.time() - start_time))

print("ASDASDAS")
# start_time = time.time()
# for aa in ll:
# 	ssh = paramiko.SSHClient()
# 	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
# 	ssh.connect(
# 		aa,
# 		username = user,
# 		password = password,
# 	)
# 	print("Connected 2")

# 	ssh.load_system_host_keys()
# 	ssh.connect(aa, username='root', password='0penc0de')
# 	ssh.connect(aa)
# 	scp_client = scp.SCPClient(ssh.get_transport())
# 	scp_client.put('exec_script/take_stats.py', '/root/python/')
# 	_, stdout, _ = ssh.exec_command('python /root/python/take_stats.py')
# 	stdout = '\n'.join(map(lambda x: x.rstrip(), stdout.readlines()))
# 	a = 7
# 	output = eval(stdout)
# 	# print("A => {}\n\n\n".format(a))
# 	# print("FINISH WITH OUTPUT\n\n\n")
# 	with open('aa.txt', 'a') as f:
# 		f.write("SSSSSSSS => {}\n".format(output))

# print("Time 2 => {}".format(time.time() - start_time))
