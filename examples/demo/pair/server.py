#!/usr/bin/env python

"""
Example txzmq server.

    server.py --endpoint=ipc:///tmp/sock
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


class MyPairServer(ZmqPairConnection):

    def messageReceived(self, message):
        # in this example only single-part messages are used
        message = message[0]
        print "received request: %s" % (message)
        data = str(time.time())
        print "sending response: %s" % data
        self.send(data)


if __name__ == '__main__':

    (options, args) = parser.parse_args()
    
    endpoint = ZmqEndpoint(ZmqEndpointType.bind, options.endpoint)
    server = MyPairServer(endpoint)
    
    def onListen(server):
        print "Server listening"
    
    deferred = server.listen(ZmqFactory())
    deferred.addCallback(onListen)
    reactor.run()


            
    
    
