"""
Tests for L{tx0mq.pair}.
"""
from twisted.trial import unittest

from twisted.internet import reactor, defer

from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPairConnection


class ZmqTestPairConnection(ZmqPairConnection):

    def messageReceived(self, message):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append(message)


class ZmqPairTestCase(unittest.TestCase):
    """
    Test case for L{tx0mq.pair}
    """

    def setUp(self):
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()


    def test_send_recv_ipc(self):
        """ Check sending and receiving using ipc """

        def onListen(p2, p1, d):
            dp1 = p1.connect(self.factory)
            dp1.addCallback(onConnect, p2, d)

        def onConnect(p1, p2, d):
            reactor.callLater(0.2, perform_test, p1, p2, d)

        def perform_test(p1, p2, d):
            p1.send('abcd')
            p2.send('xyz')
            p1.send('efgh')
            reactor.callLater(0.2, check, p1, p2, d)

        def check(p1, p2, d):
            p1_result = getattr(p1, 'messages', [])
            p1_expected = [['xyz']]
            self.failUnlessEqual(
                p1_result, p1_expected, "Message should have been received")
            p2_result = getattr(p2, 'messages', [])
            p2_expected = [['abcd'], ['efgh']]
            self.failUnlessEqual(
                p2_result, p2_expected, "Message should have been received")
            d.callback(True)

        p1 = ZmqTestPairConnection(ZmqEndpoint(ZmqEndpointType.connect, "ipc://test-sock"))
        p2 = ZmqTestPairConnection(ZmqEndpoint(ZmqEndpointType.bind, "ipc://test-sock"))

        d = defer.Deferred()

        dp2 = p2.listen(self.factory)
        dp2.addCallback(onListen, p1, d)

        return d

    def test_send_recv_tcp(self):
        """ Check sending and receiving using tcp """

        def onListen(p2, p1, d):
            dp1 = p1.connect(self.factory)
            dp1.addCallback(onConnect, p2, d)

        def onConnect(p1, p2, d):
            reactor.callLater(0.2, perform_test, p1, p2, d)

        def perform_test(p1, p2, d):
            p1.send('abcd')
            p2.send('xyz')
            p1.send('efgh')
            reactor.callLater(0.2, check, p1, p2, d)

        def check(p1, p2, d):
            p1_result = getattr(p1, 'messages', [])
            p1_expected = [['xyz']]
            self.failUnlessEqual(
                p1_result, p1_expected, "Message should have been received")
            p2_result = getattr(p2, 'messages', [])
            p2_expected = [['abcd'], ['efgh']]
            self.failUnlessEqual(
                p2_result, p2_expected, "Message should have been received")
            d.callback(True)

        p1 = ZmqTestPairConnection(ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5555"))
        p2 = ZmqTestPairConnection(ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5555"))

        d = defer.Deferred()

        dp2 = p2.listen(self.factory)
        dp2.addCallback(onListen, p1, d)

        return d


# This test is supposed to verify that another socket can not
# be connected to an established pair connection. However,
# the underlying 0MQ library raises asserts and crashes in
# this situation which makes this test un-runnable.
#
#    def test_additional_connect_is_prohibited(self):
#        """ Check additional connect is prohibited """
#
#        def onListen(p2, p1, p3, d):
#            print "p2 listening"
#            dp1 = p1.connect(self.factory)
#            dp1.addCallback(onConnect, p2, p3, d)
#
#        def onConnect(p1, p2, p3, d):
#            print "p1 connected"
#            dp3 = p3.connect(self.factory)
#            dp3.addCallback(onConnectP3, d)
#            dp3.addErrback(onConnectFailed, d)
#
#        def onConnectP3(p3, p1, p2, d):
#            # p3 is not expected to connect
#            print "p3 connected"
#            d.callback(False)
#            #reactor.callLater(0.2, perform_test, p1, p2, p3, d)
#
#        def onConnectFailed(failure, d):
#            print "p3 connect failed - as expected"
#            d.callback(True)
#
#        def perform_test(p1, p2, p3, d):
#            print "sending messages"
#            p1.send('abcd')
#            p2.send('xyz')
#            p3.send('efgh')
#            reactor.callLater(0.2, check, p1, p2, d)
#
#        def check(p1, p2, d):
#            print "checking results"
#            p1_result = getattr(p1, 'messages', [])
#            print "p1 result: %s" % p1_result
#            p1_expected = [['xyz']]
#            print "p1_expected: %s" % p1_expected
#            self.failUnlessEqual(
#                p1_result, p1_expected, "Message should have been received")
#            p2_result = getattr(p2, 'messages', [])
#            print "p2 result: %s" % p2_result
#            p2_expected = [['abcd'], ['efgh']]
#            print "p2_expected: %s" % p2_expected
#            self.failUnlessEqual(
#                p2_result, p2_expected, "Message should have been received")
#            d.callback(True)
#
#        p1 = ZmqTestPairConnection(ZmqEndpoint(ZmqEndpointType.connect, "ipc://test-sock"))
#        p2 = ZmqTestPairConnection(ZmqEndpoint(ZmqEndpointType.bind, "ipc://test-sock"))
#        p3 = ZmqTestPairConnection(ZmqEndpoint(ZmqEndpointType.connect, "ipc://test-sock"))
#
#        d = defer.Deferred()
#
#        dp2 = p2.listen(self.factory)
#        dp2.addCallback(onListen, p1, p3, d)
#
#        return d


