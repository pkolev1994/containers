import docker

host_ip = '10.102.7.124'
client = docker.DockerClient(base_url='tcp://{}:2375'.format(host_ip))
# print(client.swarm.leave(force=True))


print(client.swarm.join(remote_addrs=['10.102.7.122'], \
						join_token = "SWMTKN-1-5ynn8bvs5tolq1okngmcysob08fsltgozvnrjpzq95sv5q2w7v-2mybtqebhtcygs13xclo69kg9"))

# print(client.swarm.leave(force=True))