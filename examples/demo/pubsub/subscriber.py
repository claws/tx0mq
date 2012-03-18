#!/usr/bin/env python
"""
Example tx0mq subscriber.

    subscriber.py --endpoint=ipc:///tmp/sock
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
    sys.path.append(package_dir)
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqSubConnection


parser = OptionParser("")
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/sock", help="0MQ Endpoint")
parser.add_option("-t", "--topic", dest="topic", default="demo_topic", help="Data topic")
#parser.set_defaults(method="connect", endpoint="epgm://eth1;239.0.5.3:10011")


class MySubscriber(ZmqSubConnection):

    def messageReceived(self, message, topic):
        # in this example only single-part messages are used
        message = message[0]
        print "Received message: (%s) %s" % (topic, message)


if __name__ == '__main__':

    (options, args) = parser.parse_args()
    
    def onConnect(subscriber):
        print "subscriber connected, subscribing for topic: %s" % options.topic
        subscriber.subscribe(options.topic)

    endpoint = ZmqEndpoint(ZmqEndpointType.connect, options.endpoint)
    subscriber = MySubscriber(endpoint)
    deferred = subscriber.listen(ZmqFactory())
    deferred.addCallback(onConnect) 
    reactor.run()





