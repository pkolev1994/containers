import etcd

# # client = etcd.Client() # this will create a client against etcd server running on localhost on port 4001
client = etcd.Client(port=2379)
# # client = etcd.Client(host='127.0.0.1', port=4003)
# # client = etcd.Client(host='127.0.0.1', port=4003, allow_redirect=False) # wont let you run sensitive commands on non-leader machines, default is true
# # client = etcd.Client(
# #              host='127.0.0.1',
# #              port=4003,
# #              allow_reconnect=True,
# #              protocol='https',)

# # client.write('/asparuhhhh', 123124)
# # print(client.read('nodes').value)




###############
# client.write('/orchastrator/types_instances/br/br_1', "10.102.7.80")
# client.write('/orchastrator/types_instances/br/br_2', "10.102.7.81")
# client.write('/orchastrator/types_instances/br/br_3', "10.102.7.82")
# client.write('/orchastrator/types_instances/br/br_4', "10.102.7.83")
# client.write('/orchastrator/types_instances/br/br_5', "10.102.7.84")
# client.write('/orchastrator/types_instances/br/br_6', "10.102.7.85")
# client.write('/orchastrator/types_instances/br/br_7', "10.102.7.86")
# client.write('/orchastrator/types_instances/br/br_8', "10.102.7.87")
# client.write('/orchastrator/types_instances/br/br_9', "10.102.7.88")
# client.write('/orchastrator/types_instances/br/br_10', "10.102.7.89")


# client.write('/orchastrator/types_instances/ipgw/ipgw_1', "10.102.7.90")
# client.write('/orchastrator/types_instances/ipgw/ipgw_2', "10.102.7.91")
# client.write('/orchastrator/types_instances/ipgw/ipgw_3', "10.102.7.92")
# client.write('/orchastrator/types_instances/ipgw/ipgw_4', "10.102.7.93")
# client.write('/orchastrator/types_instances/ipgw/ipgw_5', "10.102.7.94")
# client.write('/orchastrator/types_instances/ipgw/ipgw_6', "10.102.7.95")
# client.write('/orchastrator/types_instances/ipgw/ipgw_7', "10.102.7.96")
# client.write('/orchastrator/types_instances/ipgw/ipgw_8', "10.102.7.97")
# client.write('/orchastrator/types_instances/ipgw/ipgw_9', "10.102.7.98")
# client.write('/orchastrator/types_instances/ipgw/ipgw_10', "10.102.7.99")



# # client.write('/orchastrator/available_servers/10.102.7.122', "")
# client.write('/orchastrator/available_servers/10.102.7.124', "")

# client.write('/orchastrator/swarm_servers/10.102.7.122', "")
# client.write('/orchastrator/swarm_servers/10.102.7.123', "")

# client.write('/orchastrator/logging_level', 10)
# client.write('/orchastrator/token', "SWMTKN-1-5ynn8bvs5tolq1okngmcysob08fsltgozvnrjpzq95sv5q2w7v-2mybtqebhtcygs13xclo69kg9")
# client.write('/orchastrator/master', "10.102.7.122")
# client.write('/orchastrator/network_name', "external_macvlan")
# client.write('/orchastrator/br_per_node', 3)
# client.write('/orchastrator/ipgw_per_node', 3)
# client.write('/orchastrator/br_min', 6)
# client.write('/orchastrator/ipgw_min', 6)


# client.delete('/orchastrator/available_servers/10.102.7.122')
# client.delete('/orchastrator/swarm_servers/10.102.7.124')
# client.delete('/orchastrator/swarm_servers/10.102.7.125')
################################


client.write('/orchastrator/platform_status', "")

# r = client.read('/orchastrator/types_instances/', recursive=True, sorted=True)
# print(r)
# for child in r.children:
#     print("%s: %s" % (child.key,child.value))



from lib.etcd_client import EtcdManagement

etcd = EtcdManagement()
# print(etcd.get_types_instances())
# print(etcd.get_available_servers())
# print(etcd.get_swarm_servers())
# print(etcd.get_logging_level())
# print(etcd.get_network_name())
# print(etcd.get_token())
# print(etcd.get_master())
print(etcd.get_etcd_config())
# print(etcd.get_initial_state())