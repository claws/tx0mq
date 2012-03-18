"""
Tests for L{tx0mq.connection}.
"""
from tx0mq import constants

from zope.interface import verify as ziv

from twisted.internet import reactor, defer
from twisted.internet.interfaces import IFileDescriptor, IReadDescriptor
from twisted.trial import unittest

from tx0mq import ZmqConnection, ZmqFactory, ZmqEndpoint, ZmqEndpointType


class ZmqTestSender(ZmqConnection):
    socketType = constants.PUSH


class ZmqTestReceiver(ZmqConnection):
    socketType = constants.PULL

    def messageReceived(self, message):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append(message)


class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """

    def setUp(self):
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()

    def test_interfaces(self):
        ziv.verifyClass(IReadDescriptor, ZmqConnection)
        ziv.verifyClass(IFileDescriptor, ZmqConnection)

    def test_init(self):
        ZmqTestReceiver(ZmqEndpoint(ZmqEndpointType.bind, "ipc://#1"))
        ZmqTestSender(ZmqEndpoint(ZmqEndpointType.connect, "ipc://#1"))

    def test_repr(self):
        expected = ("ZmqTestReceiver(None, (ZmqEndpoint(type='bind', address='ipc://#1'),))")
        result = ZmqTestReceiver(ZmqEndpoint(ZmqEndpointType.bind, "ipc://#1"))
        self.failUnlessEqual(expected, repr(result))

    def test_send_recv(self):

        def onListen(r, s, d):
            ds = s.connect(self.factory)
            ds.addCallback(onConnect, r, d)

        def onConnect(s, r, d):
            s.send('abcd')
            reactor.callLater(0.2, check, r, d)

        def check(r, d):
            result = getattr(r, 'messages', [])
            expected = [['abcd']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")
            d.callback(True)

        r = ZmqTestReceiver(ZmqEndpoint(ZmqEndpointType.bind, "ipc://#1"))
        s = ZmqTestSender(ZmqEndpoint(ZmqEndpointType.connect, "ipc://#1"))

        d = defer.Deferred()
        
        dr = r.listen(self.factory)
        dr.addCallback(onListen, s, d)

        return d

    def test_send_recv_tcp(self):
        
        def onListen(r, s, d):
            ds = s.connect(self.factory)
            ds.addCallback(onConnect, r, d)

        def onConnect(s, r, d):
            for i in xrange(100):
                s.send(str(i))
            reactor.callLater(0.3, check, r, d)

        def check(r, d):
            result = getattr(r, 'messages', [])
            expected = map(lambda i: [str(i)], xrange(100))
            self.failUnlessEqual(
                result, expected, "Messages should have been received")
            d.callback(True)
        
        r = ZmqTestReceiver(ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5555"))
        s = ZmqTestSender(ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5555"))

        d = defer.Deferred()
        
        dr = r.listen(self.factory)
        dr.addCallback(onListen, s, d)

        return d



    def test_send_recv_tcp_large(self):
        
        def onListen(r, s, d):
            ds = s.connect(self.factory)
            ds.addCallback(onConnect, r, d)

        def onConnect(s, r, d):
            s.send(["0" * 10000, "1" * 10000])
            reactor.callLater(0.3, check, r, d)

        def check(r, d):
            result = getattr(r, 'messages', [])
            expected = [["0" * 10000, "1" * 10000]]
            self.failUnlessEqual(
                result, expected, "Messages should have been received")
            d.callback(True)
        
        r = ZmqTestReceiver(ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5555"))
        s = ZmqTestSender(ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5555"))

        d = defer.Deferred()
        
        dr = r.listen(self.factory)
        dr.addCallback(onListen, s, d)

        return d
