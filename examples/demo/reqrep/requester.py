"""
Example tx0mq requester.

    requester.py --endpoint=ipc:///tmp/sock
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
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/sock", help="0MQ Endpoint")


if __name__ == '__main__':
    
    (options, args) = parser.parse_args()
  
    @defer.inlineCallbacks 
    def doRequest(requester):
        data = str(time.time())
        print "sending request containing %s ..." % (data)
        reply = yield requester.request(data)
        # this example only uses single-part messages
        reply = reply[0]
        print "received reply: %s" % reply
        reactor.callLater(1, reactor.stop)

    def onConnect(requester):
        print "Requester connected"
        requester.setSocketOptions({constants.LINGER:0})
        reactor.callLater(1, doRequest, requester)
        

    endpoint = ZmqEndpoint(ZmqEndpointType.connect, options.endpoint)
    requester = ZmqReqConnection(endpoint)
    deferred = requester.connect(ZmqFactory())
    deferred.addCallback(onConnect)
    reactor.run()

