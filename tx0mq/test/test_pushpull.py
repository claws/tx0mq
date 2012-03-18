"""
Tests for L{tx0mq.pushpull}.
"""
from twisted.trial import unittest

from twisted.internet import reactor, defer

from tx0mq import constants, ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPushConnection, ZmqPullConnection



class ZmqTestPullConnection(ZmqPullConnection):

    def messageReceived(self, message):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append(message)


class ZmqPushPullTestCase(unittest.TestCase):
    """
    Test case for L{tx0mq.pushpull}
    """

    def setUp(self):
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()


    def test_send_recv(self):
        """ Check  hsending and receiving """

        def onListen(pusher, puller, d):
            # now connect the puller
            dpuller = puller.connect(self.factory)
            dpuller.addCallback(onConnect, pusher, d)

        def onConnect(puller, pusher, d):
            reactor.callLater(0.2, perform_test, pusher, puller, d)

        def perform_test(pusher, puller, d):
            for i in range(0,5):
                pusher.push(str(i)) 
            reactor.callLater(0.2, check, pusher, puller, d)

        def check(pusher, puller, d):
            result = getattr(puller, 'messages', [])
            expected = [ ['0'], ['1'], ['2'], ['3'], ['4'] ]
            self.failUnlessEqual(
                result, expected, "Message should have been received")
            d.callback(True)

        pusher = ZmqPushConnection(ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5858"))
        puller = ZmqTestPullConnection(ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5858"))

        d = defer.Deferred()

        dpush = pusher.listen(self.factory)
        dpush.addCallback(onListen, puller, d)

        return d
