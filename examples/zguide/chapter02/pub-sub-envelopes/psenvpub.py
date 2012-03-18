"""
Pubsub envelope publisher   
"""

import sys
import time
from twisted.internet import reactor
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))))
    print package_dir
    sys.path.append(package_dir)
from tx0mq import constants, ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPubConnection



if __name__ == '__main__':

    def publish(publisher):
        # Write two messages, each with an envelope and content
        first_message = ["A", "We don't want to see this"] 
        second_message = ["B", "We would like to see this"] 
        third_message = ["BB", "We might see this"] 
        print "publishing ..." 
        publisher.publish(first_message)
        publisher.publish(second_message)
        publisher.publish(third_message)
        reactor.callLater(1, publish, publisher)

    def onListen(publisher):
        print "Publisher connected"
        publisher.setSocketOptions({constants.LINGER:0})
        publish(publisher)

    # Prepare our context and publisher
    endpoint = ZmqEndpoint(ZmqEndpointType.bind, "tcp://*:5563")
    publisher = ZmqPubConnection(endpoint)
    deferred = publisher.listen(ZmqFactory())
    deferred.addCallback(onListen)
    reactor.run()





