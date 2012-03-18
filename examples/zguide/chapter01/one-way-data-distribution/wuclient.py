#
#   Weather update client
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import sys
from twisted.internet import reactor
from optparse import OptionParser
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))))
    sys.path.append(package_dir)
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqSubConnection

parser = OptionParser("")
parser.add_option("-z", "--zipcode", dest="zipcode", default="10001", help="Zipcode. default is NYC, 10001")


class MySubscriber(ZmqSubConnection):

    def messageReceived(self, message, zipcode):
        # this example only ever receives single-part messages
        message = message[0]
        print "Received message: (%s) %s" % (zipcode, message)
        temperature, relhumidity = message.split()
        self.total_temp += int(temperature)
        self.update_count += 1
        if self.update_count == self.updates_to_process:
            print "Average temperature for zipcode '%s' was %dF" % (zipcode, self.total_temp / self.updates_to_process)
            reactor.callLater(1.0, reactor.stop)


if __name__ == '__main__':

    (options, args) = parser.parse_args()

    number_of_updates = 5

    def onConnect(subscriber):
        print "subscriber connected, subscribing for zipcode: %s" % options.zipcode
        # Subscribe to zipcode, default is NYC, 10001
        subscriber.subscribe(options.zipcode)
        subscriber.update_count = 0
        subscriber.total_temp = 0
        subscriber.updates_to_process = number_of_updates

    endpoint = ZmqEndpoint(ZmqEndpointType.connect, "tcp://localhost:5556")
    subscriber = MySubscriber(endpoint)
    deferred = subscriber.listen(ZmqFactory())
    deferred.addCallback(onConnect)
    reactor.run()

