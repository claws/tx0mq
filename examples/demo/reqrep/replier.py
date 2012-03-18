"""
Example tx0mq replier.

    replier.py --endpoint=ipc:///tmp/sock
"""
import sys
import time
from optparse import OptionParser
from twisted.internet import reactor
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))))
    print package_dir
    sys.path.append(package_dir)
from tx0mq import constants, ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqRepConnection


parser = OptionParser("")
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/sock", help="0MQ Endpoint")


class MyReplier(ZmqRepConnection):

    def messageReceived(self, message, identifier):
        # this example only uses single-part messages
        message = message[0]
        print "received request %s : %s" % (identifier, message)
        # return response message
        data = str(time.time())
        print "response contains %s : %s" % (identifier, data)
        self.reply(identifier, data)


if __name__ == '__main__':
    
    (options, args) = parser.parse_args()
  
    def onListen(replier):
        print "Replier listening"

    endpoint = ZmqEndpoint(ZmqEndpointType.bind, options.endpoint)
    replier = MyReplier(endpoint)
    deferred = replier.listen(ZmqFactory())
    deferred.addCallback(onListen)
    reactor.run()

