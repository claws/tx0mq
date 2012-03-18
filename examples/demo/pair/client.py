#!/usr/bin/env python

"""
Example tx0mq client.

    client.py --endpoint=ipc:///tmp/sock
"""

import os
import sys
rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..'))
sys.path.append(rootdir)

import time
from optparse import OptionParser
from twisted.internet import reactor
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPairConnection


parser = OptionParser("")
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/sock", help="0MQ Endpoint")    


class MyPairClient(ZmqPairConnection):

    def messageReceived(self, message):
        # in this example only single-part messages are used
        message = message[0]
        # don't reply to the reply or a cascade of pain ensues
        print "received response: %s" % (message)

if __name__ == '__main__':


    (options, args) = parser.parse_args()
    
    endpoint = ZmqEndpoint(ZmqEndpointType.connect, options.endpoint)
    client = MyPairClient(endpoint)
    
    def onConnect(client):
        print "Client connected"
        send(client)
    
    def send(client):
        data = str(time.time())
        print "sending %s" % data
        client.send(data)
        reactor.callLater(1, send, client)

    deferred = client.connect(ZmqFactory())
    deferred.addCallback(onConnect)
    reactor.run()


            
    
    
