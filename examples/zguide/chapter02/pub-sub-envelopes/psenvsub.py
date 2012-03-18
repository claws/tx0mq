"""
Pubsub envelope subscriber   
"""

import sys
import time
from twisted.internet import reactor
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))))
    sys.path.append(package_dir)
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqSubConnection


class MySubscriber(ZmqSubConnection):

    def messageReceived(self, message, topic):
        print "[%s] %s" % (topic, message)


if __name__ == '__main__':

    def onConnect(subscriber):
        print "subscriber connected"
        subscriber.subscribe('B')

    # Prepare our context and subscriber
    endpoint = ZmqEndpoint(ZmqEndpointType.connect, "tcp://localhost:5563")
    subscriber = MySubscriber(endpoint)
    deferred = subscriber.listen(ZmqFactory())
    deferred.addCallback(onConnect) 
    reactor.run()





