#!/usr/bin/env python

"""
Example txzmq pusher.

    pusher.py --endpoint=ipc:///tmp/sock
"""

import os
import sys
rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..'))
sys.path.append(rootdir)

import socket
import time
from optparse import OptionParser
from twisted.internet import reactor
from tx0mq import constants, ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPushConnection


parser = OptionParser("")
parser.add_option("-m", "--method", dest="method", help="0MQ socket connection: bind|connect")
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/sock", help="0MQ Endpoint")
#parser.set_defaults(method="connect", endpoint="ipc:///tmp/txzmq-pc-demo")



if __name__ == '__main__':
    
    (options, args) = parser.parse_args()
   

    def onConnect(pusher):
        print "pusher connected"
        # discard unsent messages on close
        pusher.setSocketOptions({constants.LINGER:0, constants.HWM:1})
        produce(pusher) 

    def produce(pusher):
        data = str(time.time())
        print "pushing %s ..." % (data)
        pusher.push(data)
        reactor.callLater(1, produce, pusher)
 
    endpoint = ZmqEndpoint(ZmqEndpointType.connect, options.endpoint)
    pusher = ZmqPushConnection(endpoint)
    deferred = pusher.listen(ZmqFactory())
    deferred.addCallback(onConnect)
    reactor.run()


