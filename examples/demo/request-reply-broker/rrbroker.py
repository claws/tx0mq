"""
Example tx0mq requester.

    rrbroker.py --frontend_endpoint=ipc:///tmp/broker_frontend.ipc --backend_endpoint=ipc:///tmp/broker_backend.ipc
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
from tx0mq import constants, ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqRepConnection, ZmqReqConnection, ZmqQueue


parser = OptionParser("")
parser.add_option("-f", "--frontend_endpoint", dest="frontend_endpoint", default="ipc:///tmp/broker_frontend.ipc", help="Frontend 0MQ Endpoint")
parser.add_option("-b", "--backend_endpoint", dest="backend_endpoint", default="ipc:///tmp/broker_backend.ipc", help="Backend 0MQ Endpoint")


if __name__ == '__main__':
    
    (options, args) = parser.parse_args()

    @defer.inlineCallbacks 
    def start_queue_device():

        factory = ZmqFactory()

        frontend_endpoint = ZmqEndpoint(ZmqEndpointType.bind, options.frontend_endpoint)
        frontend = ZmqRepConnection(frontend_endpoint)
        frontend = yield frontend.listen(factory)
        print "broker's frontend router connection is ready"
        print frontend

        backend_endpoint = ZmqEndpoint(ZmqEndpointType.bind, options.backend_endpoint)
        backend = ZmqReqConnection(backend_endpoint)
        backend = yield backend.listen(factory)
        print "broker's backend dealer connection is ready"
        print backend

        broker = ZmqQueue(frontend, backend)
        print "broker is ready"
        print broker
        
        defer.returnValue(None)

    reactor.callWhenRunning(start_queue_device)
    reactor.run()

