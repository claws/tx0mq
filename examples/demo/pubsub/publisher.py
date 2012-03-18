#!/usr/bin/env python
"""
Example tx0mq publisher.

    publisher.py --endpoint=ipc:///tmp/sock
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
from tx0mq import constants, ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPubConnection


parser = OptionParser("")
parser.add_option("-e", "--endpoint", dest="endpoint", default="ipc:///tmp/sock", help="0MQ Endpoint")
parser.add_option("-t", "--topic", dest="topic", default="demo_topic", help="Data topic")
#parser.set_defaults(method="connect", endpoint="epgm://eth1;239.0.5.3:10011")



if __name__ == '__main__':

    (options, args) = parser.parse_args()
    
    def publish(publisher):
        data = str(time.time())
        print "publishing (%s) %s ..." % (options.topic, data)
        publisher.publish(data, topic=options.topic)
        reactor.callLater(1, publish, publisher)

    def onListen(publisher):
        print "Publisher connected"
        publisher.setSocketOptions({constants.LINGER:0})
        publish(publisher)

    endpoint = ZmqEndpoint(ZmqEndpointType.bind, options.endpoint)
    publisher = ZmqPubConnection(endpoint)
    deferred = publisher.listen(ZmqFactory())
    deferred.addCallback(onListen)
    reactor.run()





