#
#   Weather update server
#   Binds PUB socket to tcp://*:5556
#   Publishes random weather updates
#

import random
import sys
from twisted.internet import reactor
from optparse import OptionParser
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))))
    sys.path.append(package_dir)
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPubConnection

parser = OptionParser("")
parser.add_option("-z", "--zipcode", dest="zipcode", default="10001", help="Zipcode. default is NYC, 10001")


if __name__ == '__main__':

    (options, args) = parser.parse_args()

    def publish(publisher):
        zipcode = str(random.randrange(10000,10050))
        temperature = random.randrange(1,215) - 80
        relhumidity = random.randrange(1,50) + 10
        message = "%s %s" % (temperature, relhumidity)
        print "publishing (%s) %s ..." % (zipcode, message)
        publisher.publish(message, topic=zipcode)
        reactor.callLater(0.5, publish, publisher)

    def onListen(publisher):
        print "Publisher connected"
        publish(publisher)

    endpoint = ZmqEndpoint(ZmqEndpointType.bind, "tcp://*:5556")
    publisher = ZmqPubConnection(endpoint)
    deferred = publisher.listen(ZmqFactory())
    deferred.addCallback(onListen)
    reactor.run()

