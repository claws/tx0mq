# Task ventilator
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket
#

import random
import sys
import time
from twisted.internet import reactor
try:
    import tx0mq
except ImportError, ex:
    import os
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))))
    sys.path.append(package_dir)
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPushConnection


if __name__ == "__main__":

    # Initialize random number generator
    random.seed()
    
    # Define how many tasks to run
    task_count = 100

    print "Press Enter when the workers are ready: "
    _ = raw_input()
    print "Connecting to to workers and sink..."

    def onWorkerChannelConnected(ventilator, factory):
        print "ventilator connected to worker push channel"

        # Socket with direct access to the sink: used to syncronize start of batch
        endpoint = ZmqEndpoint(ZmqEndpointType.connect, "tcp://localhost:5558")
        sink = ZmqPushConnection(endpoint)
        deferred = sink.connect(factory)
        deferred.addCallback(onSinkChannelConnected, ventilator)
        
    def onSinkChannelConnected(sink, ventilator):
        print "ventilator connected to sink push channel"
        # The first message is "0" and signals start of batch
        print "sending batch start message"
        sink.send("start:%s" % task_count)
        reactor.callLater(1.0, vent, ventilator)
   
    def vent(ventilator):
        # Send tasks
        total_msec = 0
        for task_number in range(task_count):
        
            # Random workload msecs
            workload = random.randint(1, 100)
            total_msec += workload
            ventilator.send(str(workload))

        print "Total expected cost: %s msec" % total_msec
        print "ventilator done"
        
    factory = ZmqFactory()

    # Socket to send messages to workers on
    endpoint = ZmqEndpoint(ZmqEndpointType.bind, "tcp://*:5557")
    ventilator = ZmqPushConnection(endpoint)
    deferred = ventilator.listen(factory)
    deferred.addCallback(onWorkerChannelConnected, factory)

    reactor.run()







