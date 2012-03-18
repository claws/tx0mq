"""
Tests for L{tx0mq.pubsub}.
"""
from twisted.trial import unittest

from twisted.internet import reactor, defer

from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqPubConnection, ZmqSubConnection


class ZmqTestSubConnection(ZmqSubConnection):

    def messageReceived(self, message, topic):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append([topic, message])


class ZmqPubSubTestCase(unittest.TestCase):
    """
    Test case for L{tx0mq.pubsub}
    """

    def setUp(self):
        self.factory = ZmqFactory()
        ZmqPubConnection.allowLoopbackMulticast = True

    def tearDown(self):
        del ZmqPubConnection.allowLoopbackMulticast
        self.factory.shutdown()

    def test_send_recv(self):
        """ Check sending and receiving """

        def onListen(p, s, d):
            ds = s.connect(self.factory)
            ds.addCallback(onConnect, p, d)
        
        def onConnect(s, p, d):
            s.subscribe('tag')
            reactor.callLater(0.2, performTest, s, p, d)

        def performTest(s, p ,d):
            p.publish('xyz', 'different-tag')
            p.publish('abcd', 'tag1')
            p.publish('efgh', 'tag2')
            reactor.callLater(0.2, check, s, d)
            
        def check(s, d):
            result = getattr(s, 'messages', [])
            expected = [['tag1', ['abcd']], ['tag2', ['efgh']]]
            self.failUnlessEqual(
                result, expected, "Message should have been received")
            d.callback(True) 
        
        s = ZmqTestSubConnection(ZmqEndpoint(ZmqEndpointType.connect, "ipc://test-sock"))
        p = ZmqPubConnection(ZmqEndpoint(ZmqEndpointType.bind, "ipc://test-sock"))

        d = defer.Deferred()

        ds = p.listen(self.factory)
        ds.addCallback(onListen, s, d)

        return d
#
# PGM is not enabled in my 0MQ. OpenPGM is currently broken on
# OS X 10.7. It will be fixed in the OpenPGM 5.2 release.
#
#    def test_send_recv_pgm(self):
#        """ Test send and receive using multicast """
#        
#        def onListen(p, s, d):
#            print "publisher listening"
#            ds = s.connect(self.factory)
#            ds.addCallback(onConnect, p, d)
#        
#        def onConnect(s, p, d):
#            print "subscriber connected"
#            s.subscribe('tag')
#            reactor.callLater(0.2, perform_test, s, p, d)
#
#        def perform_test(s, p, d):
#            print "publishing messages"
#            p.publish('xyz', 'different-tag')
#            p.publish('abcd', 'tag1')
#            reactor.callLater(0.2, check, s, d)
#            
#        def check(s, d):
#            print "checking results"
#            result = getattr(s, 'messages', [])
#            print "result: %s" % result
#            expected = [['tag1', ['abcd']]]
#            print "expected: %s" % expected
#            self.failUnlessEqual(
#                result, expected, "Message should have been received")
#            d.callback(True) 
#
#        s = ZmqTestSubConnection(
#            ZmqEndpoint(ZmqEndpointType.connect, "epgm://127.0.0.1;239.192.1.1:5556"))
#        p = ZmqPubConnection(
#            ZmqEndpoint(ZmqEndpointType.bind, "epgm://127.0.0.1;239.192.1.1:5556"))
#
#        d = defer.Deferred()
#
#        dp = p.listen(self.factory)
#        dp.addCallback(onListen, s, d)
#
#        return d

    def test_send_recv_multiple_endpoints(self):
        """ Check send and receive using multiple endpoint """
        
        def onP1Listen(p1, p2, s, d):
            dp2 = p2.listen(self.factory)
            dp2.addCallback(onP2Listen, p1, s, d)

        def onP2Listen(p2, p1, s, d):
            ds = s.connect(self.factory)
            ds.addCallback(onConnect, p1, p2, d)
        
        def onConnect(s, p1, p2, d):
            s.subscribe('')
            reactor.callLater(0.2, perform_test, s, p1, p2, d)


        def perform_test(s, p1, p2, d):
            p1.publish('111', 'tag1')
            p2.publish('222', 'tag2')
            reactor.callLater(0.2, check, s, d)
            
        def check(s, d):
            result = getattr(s, 'messages', [])
            expected = [['tag2', ['222']], ['tag1', ['111']]]
            self.failUnlessEqual(
                result, expected, "Message should have been received")
            d.callback(True) 

        s = ZmqTestSubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"),
            ZmqEndpoint(ZmqEndpointType.connect, "inproc://endpoint"))
        p1 = ZmqPubConnection(
            ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5556"))
        p2 = ZmqPubConnection(
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://endpoint"))

        d = defer.Deferred()

        ds = p1.listen(self.factory)
        ds.addCallback(onP1Listen, p2, s, d)

        return d

