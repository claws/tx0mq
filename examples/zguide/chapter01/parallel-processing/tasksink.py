# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket
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
from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPullConnection


class SinkPullConnection(ZmqPullConnection):

    def messageReceived(self, message):
        # in this example only single-part messages are used
        message = message[0]
        if message.startswith('start'):
            # start flags the start of a new job batch and an indicator
            # of how many results to expect.
            start, task_count = message.split(":")
            self.task_count = int(task_count)
            self.completed_jobs = 0
            self.start = time.time()

        else:
            self.completed_jobs += 1
            if self.completed_jobs == self.task_count:
                # Calculate and report duration of batch
                print "Total elapsed time: %s sec" % ((time.time()-self.start))


if __name__ == "__main__":

    def onConnected(receiver):
        print "sink connected to worker channel"

    # Socket to receive messages on
    endpoint = ZmqEndpoint(ZmqEndpointType.bind, "tcp://*:5558")
    receiver = SinkPullConnection(endpoint)
    deferred = receiver.connect(ZmqFactory())
    deferred.addCallback(onConnected)

    reactor.run()
