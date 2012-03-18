"""
Tests for L{tx0mq.reqrep}.
"""
from twisted.internet import reactor, defer

from twisted.trial import unittest

from tx0mq import ZmqEndpoint, ZmqEndpointType, ZmqFactory, ZmqReqConnection, ZmqRepConnection


class ZmqTestRepConnection(ZmqRepConnection):
    identity = 'service'

    def messageReceived(self, message, identifier):
        if not hasattr(self, 'messages'):
            self.messages = []
        self.messages.append([identifier, message])
        self.reply(identifier, message)


class ZmqReqRepConnectionTestCase(unittest.TestCase):
    """
    Test case for L{tx0mq.reqrep}.
    """

    def setUp(self):
        self.factory = ZmqFactory()
        ZmqReqConnection.identity = 'client'
        self.r = ZmqTestRepConnection(ZmqEndpoint(ZmqEndpointType.bind, "ipc://#3"))
        self.s = ZmqReqConnection(ZmqEndpoint(ZmqEndpointType.connect, "ipc://#3"))
        self.count = 0


    def tearDown(self):
        ZmqReqConnection.identity = None
        self.factory.shutdown()


    def test_getNextId(self):
        self.failUnlessEqual([], self.s._uuids)
        id1 = self.s._getNextId()
        self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE - 1, len(self.s._uuids))
        self.failUnlessIsInstance(id1, str)

        id2 = self.s._getNextId()
        self.failUnlessIsInstance(id2, str)

        self.failIfEqual(id1, id2)

        ids = [self.s._getNextId() for _ in range(1000)]
        self.failUnlessEqual(len(ids), len(set(ids)))

    def test_releaseId(self):
        self.s._releaseId(self.s._getNextId())
        self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE, len(self.s._uuids))



    def test_send_recv(self):

        def get_next_id():
            self.count += 1
            return 'msg_id_%d' % (self.count,)
        self.s._getNextId = get_next_id

        def onListen(r, d):
            ds = self.s.connect(self.factory)
            ds.addCallback(onConnect, d)

        def onConnect(s, d):
            d1 = self.s.request(['aaa', 'aab'])
            d2 = self.s.request('bbb')
            reactor.callLater(0.2, check, d)
        
        def check(d):
            result = getattr(self.r, 'messages', [])
            expected = [['msg_id_1', ['aaa', 'aab']], ['msg_id_2', ['bbb']]]
            self.failUnlessEqual(
                result, expected, "Message should have been received")
            d.callback(True)

        d = defer.Deferred()
        dr = self.r.listen(self.factory)
        dr.addCallback(onListen, d)
        return d

    def test_send_recv_reply(self):
        
        def onListen(r, d):
            ds = self.s.connect(self.factory)
            ds.addCallback(onConnect, d)

        def onConnect(s, d):
            d1 = self.s.request('aaa')
            d1.addCallback(check_response, d)

        def check_response(response, d):
            self.assertEqual(response, ['aaa'])
            d.callback(True)

        d = defer.Deferred()
        dr = self.r.listen(self.factory)
        dr.addCallback(onListen, d)
        return d

    def test_lot_send_recv_reply(self):

        def onListen(r, d):
            ds = self.s.connect(self.factory)
            ds.addCallback(onConnect, d)

        def onConnect(s, d):
            reactor.callLater(0.2, perform_test, d)

        def perform_test(d):
            
            def check_response(response, identifier):
                expected = ['aaa']
                self.assertEqual(response, expected)
                return response == expected
       
            deferreds = []
            for i in range(1, 11):
                identifier = "msg_id_%d" % (i,)
                ds = self.s.request(['aaa'])
                deferreds.append(ds)
                ds.addCallback(check_response, identifier)
            dl = defer.DeferredList(deferreds)
            dl.addCallback(d.callback)
        
        d = defer.Deferred()
        dr = self.r.listen(self.factory)
        dr.addCallback(onListen, d)
        return d

    def test_cleanup_requests(self):
        """The request dict is cleanedup properly."""
        
        def onListen(r, d):
            ds = self.s.connect(self.factory)
            ds.addCallback(onConnect, d)

        def onConnect(s, d):
            d1 = self.s.request('aaa')
            d1.addCallback(check, d)

        def check(ignore, d):
            self.assertEqual(self.s._requests, {})
            self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE, len(self.s._uuids))
            d.callback(True)

        d = defer.Deferred()
        dr = self.r.listen(self.factory)
        dr.addCallback(onListen, d)
        return d
        
