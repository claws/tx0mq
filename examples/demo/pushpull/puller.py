#!/usr/bin/env python

"""
Example txzmq puller.

    puller.py --endpoint=ipc:///tmp/sock
"""

import os
import sys
rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..'))
sys.path.append(rootdir)

import socket
import time
from optparse import OptionParser
from twisted.internet import reactor
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPullConnection


parser = OptionParser("")
parser.add_option("-m", "--method", dest="method", help="0MQ socket connection: bind|connect")
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/sock", help="0MQ Endpoint")
#parser.set_defaults(method="connect", endpoint="ipc:///tmp/txzmq-pc-demo")


class MyPuller(ZmqPullConnection):

    def messageReceived(self, message):
        print "Puller received: %s" % message


if __name__ == '__main__':
    
    (options, args) = parser.parse_args()
   

    def onListen(puller):
        print "Puller connected"

    endpoint = ZmqEndpoint(ZmqEndpointType.bind, options.endpoint)
    puller = MyPuller(endpoint)
    deferred = puller.listen(ZmqFactory())
    deferred.addCallback(onListen)
    reactor.run()



