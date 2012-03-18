# Task worker
# Connects PULL socket to tcp://localhost:5557
# Collects workloads from ventilator via that socket
# Connects PUSH socket to tcp://localhost:5558
# Sends results to sink via that socket
#

import sys
import time
from twisted.internet import reactor
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))))
    sys.path.append(package_dir)
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPushConnection, ZmqPullConnection



class Worker(object):

    def __init__(self):
        self.factory = None
        self.receiver = None
        self.sink = None

    def start(self):
        self.factory = ZmqFactory()

        endpoint = ZmqEndpoint(ZmqEndpointType.connect, "tcp://localhost:5557")
        self.receiver = ZmqPullConnection(endpoint)
        self.receiver.messageReceived = self.performWork
        deferred = self.receiver.connect(self.factory)
        deferred.addCallback(self.onReceiverConnected)

        endpoint = ZmqEndpoint(ZmqEndpointType.connect, "tcp://localhost:5558")
        self.sink = ZmqPushConnection(endpoint)
        deferred = self.sink.listen(self.factory)
        deferred.addCallback(self.onSinkConnected)


    def stop(self):
        self.factory.shutdown()
    
    def onReceiverConnected(self, receiver):
        print "worker connected to task ventilator"

    def onSinkConnected(self, sink):
        print "worker connected to task sink"

    def performWork(self, message):
        # send results to sink after waiting specified job time
        
        # in this example only single-part messages are used
        time_interval = message[0]
        
        time_wait = int(time_interval) * 0.001
        reactor.callLater(time_wait, self.sendWorkResult, "")

    def sendWorkResult(self, result):
        self.sink.send(result)


if __name__ == "__main__":

    worker = Worker()
    reactor.callWhenRunning(worker.start)
    reactor.run()    

