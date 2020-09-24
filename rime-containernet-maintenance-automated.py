#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import sys
setLogLevel('info')

NUM_NODES = int(sys.argv[1])
NUM_TIERS = int(sys.argv[2])

info('num_nodes=' + str(NUM_NODES) + '\n')
info('num_tiers=' + str(NUM_TIERS) + '\n')

# max 1mio nodes
def define_nodes(NUM_NODES): # lookup range/xrange for iteration over a number 
    node_list = []
    ip_high = 0    
    ip_low = 0

    port = 0

    for number in range(0, NUM_NODES):         
        info('*** Adding node' + str(number) + '\n')
        ip_str = '192.168.' + str(ip_high) + '.' + str(ip_low)
        
        port = 50000 + ip_low + 1000*ip_high

        # define node
        node_list.append(net.addDocker('r' + str(number),
                                            ip=ip_str,
                                            ports=[3000],
                                            port_bindings={port:3000},
                                            volumes=["/home/jjestram/rime_logs:/opt/logs_rime"],
                                            dimage="jo/rime-noentry" ) )  
        ip_low+=1        
        if ip_low == 1000 :
            ip_low = 0
            ip_high+=1                                 
    
    return node_list

def start_nodes(node_list, num_tiers) :        
    ip_high = 0    
    ip_low = 0
    parent_ip_str = ''
    ip_str = ''

    parent_id = 0      
    cnt = 0
    reference_set = False

    num_nodes_after_this_tier=1
    args = ''
    tier = 0    
    node_id = 0

    cmd_string = 'cd /opt/logs_rime && /opt/rime/build/rime --config-file=/opt/rime/run/containernet/maintenance/scaling/node.ini'

    first_parent_id = 0
    num_parents = pow(4, num_tiers - 1)

    for node in node_list : 
        info('\n*** Node' + str(ip_high*1000 + ip_low) + '\n')
    
        # check if tier (which equals level in tree) needs to be incremented
        if node_id >  num_nodes_after_this_tier - 1 and tier < num_tiers: 
            tier += 1 
            num_nodes_after_this_tier+=pow(4,tier)            
        if tier <  num_tiers :
            if node_id > 0 :                                      
                if cnt <= 3 :
                    cnt+=1
                else :
                    parent_id += 1
                    cnt = 1 

                ## get parent ip from parent id 
                if parent_id < 1000 : 
                    parent_ip_str = '192.168.0.' + str(parent_id)
                else :
                    tmp = str(parent_id/1000)
                    tmp_list = tmp.split('.') 
                    parent_ip_str = '192.168.' + tmp_list[0] + '.' + tmp_list[1].lstrip('0')                 
            if node_id == 0 :                     
                ip_str = '192.168.0.0'
                parent_ip_str = 'localhost'            
       
        # last level -> give each parent a child in round-robin-style
        else : 
            info('*** Last tier\n')
            if not reference_set :
                reference_set = True
                first_parent_id = parent_id + 1
                parent_id += 1
                info('first_parent_id=' + str(first_parent_id) + '\n')
                                    
            if parent_id >= 1000 :
                tmp = str(parent_id/1000)
                tmp_list = tmp.split('.')
                parent_ip_str = '192.168.' + tmp_list[0] + '.' + tmp_list[1].lstrip('0')
            else : 
                parent_ip_str = '192.168.0.' + str(parent_id)

            # round robin here
            parent_id += 1            
            if parent_id >= first_parent_id + num_parents :
                parent_id = first_parent_id
        
        ip_str='192.168.' +  str(ip_high) + '.' + str(ip_low)
        
        args= ' --my_ip="' + ip_str + '" --node_id=' + str(node_id) + ' --tier=' + str(tier) + ' --relative_ip="' + parent_ip_str + '" --logger.file-name="' + str(node_id) + '_actor_log_[PID]_[TIMESTAMP]_[NODE].log"'
        
        #info('args=' + args + '\n')
        #info('cmd_string=' + cmd_string + '\n')
        if node_id == 0 :
            full_string = cmd_string + ' --am_first_root' + args + ' &'
        else : 
            full_string = cmd_string + args + ' &'
        info('full_string=' + full_string + '\n')
        # start rime on node with correct args
        node.cmd(full_string)

        ip_low+=1        
        if ip_low == 1000 :
            ip_low = 0
            ip_high+=1

        node_id+=1        
    return

# add link between node and switch
def add_links(node_list) : 
    for number in range(0, len(node_list) ) : 
        info('*** Linking node' + str(number) + '\n')
        net.addLink('r' + str(number), s1)
    return

net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')

node_list = define_nodes(NUM_NODES)

info('*** Adding switches\n')
s1 = net.addSwitch('s1')
info('*** Creating links\n')

add_links(node_list)

info('*** Starting network\n')
net.start()

start_nodes(node_list, NUM_TIERS)
#node_list[0].cmd('cd /opt/logs_rime && /opt/rime/build/rime --config-file=/opt/rime/run/containernet/maintenance/scaling/node.ini --am_first_root=true --my_ip="192.168.0.0" --node_id=0 --tier=0 --relative_ip="localhost" --logger.file-name="0_actor_log_[PID]_[TIMESTAMP]_[NODE].log" &')
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
