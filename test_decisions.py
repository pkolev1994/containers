import time
from lib.decision_maker import DecisionMaker

decision_maker = DecisionMaker(available_servers = ['10.102.7.122', '10.102.7.123'])
print("Names => {}".format(decision_maker.apps_by_hosts))
print(decision_maker.making_host_decision('ipgw'))