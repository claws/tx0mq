

import logging
import logging.config
from tx0mq ZmqEndPoint, ZmqEndpointType, ZmqPubConnection


def sub_logger(port):
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect('tcp://127.0.0.1:%i'%port)
    sub.setsockopt(zmq.SUBSCRIBE,"")
    while True:
        message = sub.recv_multipart()
        name = message[0]
        msg = message[1:]
        if name == 'log':
            msg[0] = int(msg[0])
        getattr(logging, name)(*msg)



endpoint = 'tcp://127.0.0.1:5555'

class ZLogger(object):

    def __init__(self, fname=None):
        if fname is not None:
            logging.config.fileConfig(fname)
        self.pub = None

    def start(self, endpoint):
        self.factory = ZmqFactory()
        self.pub = ZmqPubConnection(ZmqEndoint(ZmqEndpointType.bind, endpoint))
        d = self.pub.connect(self.factory)
        d.addCallback(self._onListen)
        return d

    def _onListen(self, pub):
        print "Log publisher connected"

    def log(self, level, msg):
        self.pub.publish(['log', str(level), msg])

    def warn(self, msg):
        self.pub.publish(['warn', msg])

    def error(self, msg):
        self.pub.publish(['error', msg])

if __name__ == '__main__':

    (options, args) = parser.parse_args()
    endpoint = 'tcp://127.0.0.1:5555'

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
