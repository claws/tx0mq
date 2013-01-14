"""
Example tx0mq requester.

    rrclient.py --endpoint=ipc:///tmp/broker_frontend.ipc
"""
import sys
import time
from optparse import OptionParser
from twisted.internet import reactor, defer
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))))
    print package_dir
    sys.path.append(package_dir)
from tx0mq import constants, ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqReqConnection


parser = OptionParser("")
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/broker_frontend.ipc", help="0MQ Endpoint")


if __name__ == '__main__':
    
    (options, args) = parser.parse_args()
 
    def handleResponse(reply):
        # this example only uses single-part messages
        reply = reply[0]
        print "received reply: %s" % reply
        reactor.callLater(1, reactor.stop)
    
    def doRequest(requester):
        data = 'hello'
        print "client sending request containing \'%s\'" % (data)
        d = requester.request(data)
        d.addCallback(handleResponse)

    def onConnect(requester):
        print "client connected to broker"
        reactor.callLater(2, doRequest, requester)
        

    endpoint = ZmqEndpoint(ZmqEndpointType.connect, options.endpoint)
    print endpoint
    client = ZmqReqConnection(endpoint)
    print client
    deferred = client.connect(ZmqFactory())
    deferred.addCallback(onConnect)
    reactor.run()

