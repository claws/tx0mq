
"""
ZeroMQ connection.
"""

from collections import deque, namedtuple
import logging
import random

from twisted.internet import defer
from twisted.internet.interfaces import IFileDescriptor, IReadDescriptor
from twisted.python import log
from tx0mq import constants
from tx0mq import exceptions, util
import types
from zmq.core import error
from zmq.core.socket import Socket
from zmq.core.version import zmq_version_info
from zope.interface import implements


ZMQ3 = zmq_version_info()[0] == 3


class ZmqEndpointType(object):
    """
    Endpoint could be "bound" or "connected".
    """
    bind = "bind"
    connect = "connect"


ZmqEndpoint = namedtuple('ZmqEndpoint', ['type', 'address'])


class ZmqConnection(object):
    """
    Connection through ZeroMQ, wraps up ZeroMQ socket.

    @cvar socketType: socket type, from ZeroMQ
    @cvar allowLoopbackMulticast: is loopback multicast allowed?
    @type allowLoopbackMulticast: C{boolean}
    @cvar multicastRate: maximum allowed multicast rate, kbps
    @type multicastRate: C{int}
    @cvar highWaterMark: hard limit on the maximum number of outstanding
        messages 0MQ shall queue in memory for any single peer
    @type highWaterMark: C{int}

    @ivar factory: ZeroMQ Twisted factory reference
    @type factory: L{ZmqFactory}
    @ivar socket: ZeroMQ Socket
    @type socket: L{Socket}
    @ivar endpoints: ZeroMQ addresses for connect/bind
    @type endpoints: C{list} of L{ZmqEndpoint}
    @ivar fd: file descriptor of zmq mailbox
    @type fd: C{int}
    @ivar queue: output message queue
    @type queue: C{deque}
    @ivar isConnected: True if the connect() method called without error
    @type isConnected: C{lbool}
    @ivar isListening: True if the listen() method called without error
    @type isListening: C{lbool}
    @iprop isEstablished: True if isListening or isConnected are True
    @type isEstablished: C{lbool}
    """
    implements(IReadDescriptor, IFileDescriptor)

    socketType = None
    allowLoopbackMulticast = False
    multicastRate = 100
    highWaterMark = 0
    identity = None

    def __init__(self, *endpoints):
        """
        Constructor.

        @param endpoints: ZeroMQ addresses for connect/bind
        @type endpoints: C{list} of L{ZmqEndpoint}
        """
        self.factory = None
        self.endpoints = endpoints
        self.queue = deque()
        self.recv_parts = []
        self.fd = None
        self.isListening = False
        self.isConnected = False

    def __repr__(self):
        return "%s(%r, %r)" % (
            self.__class__.__name__, self.factory, self.endpoints)

    def _createSocket(self, factory):
        """
        Create a socket and assign the fd.
        """
        socket = Socket(factory.context, self.socketType)
        self.fd = socket.getsockopt(constants.FD)
        socket.setsockopt(constants.LINGER, factory.lingerPeriod)

        if not ZMQ3:
            socket.setsockopt(
                constants.MCAST_LOOP, int(self.allowLoopbackMulticast))

        socket.setsockopt(constants.RATE, self.multicastRate)

        if not ZMQ3:
            socket.setsockopt(constants.HWM, self.highWaterMark)
        else:
            socket.setsockopt(constants.SNDHWM, self.highWaterMark)
            socket.setsockopt(constants.RCVHWM, self.highWaterMark)

        if self.identity is not None:
            socket.setsockopt(constants.IDENTITY, self.identity)
        return socket

    def _connectOrBind(self, factory):
        """
        Connect and/or bind socket to endpoints.

        Any wildcard endpoints in self.endpoints get replaced by
        the actual endpoint used.
        """
        self.socket = self._createSocket(factory)
        for endpoint in self.endpoints:
            if endpoint.type == ZmqEndpointType.connect:
                self.socket.connect(endpoint.address)
                self.isConnected = True
            elif endpoint.type == ZmqEndpointType.bind:
                # handle wildcard port
                if endpoint.address.endswith("*"):
                    max_tries = 100
                    min_port = 49152
                    max_port = 65536
                    for i in range(max_tries):
                        try:
                            port = random.randrange(min_port, max_port)
                            candidate_address = "%s:%s" % (endpoint.address.split(":*")[0], port)
                            self.socket.bind(candidate_address)

                            # replace the wildcard endpoint with the actual endpoint
                            eps = list(self.endpoints)
                            index = eps.index(endpoint)
                            self.endpoints = eps
                            eps[index] = ZmqEndpoint(endpoint.type, candidate_address)
                            self.endpoints = tuple(eps)
                            break

                        except error.ZMQError, ex:
                            if not ex.errno == constants.EADDRINUSE:
                                raise
                            else:
                                logging.info("%s addr in use, trying another..." % candidate_address)

                else:
                    self.socket.bind(endpoint.address)
                self.isListening = True
            else:
                assert False, "Unknown endpoint type %r" % endpoint
        factory.connections.add(self)
        factory.reactor.addReader(self)
        self.factory = factory

    @property
    def isEstablished(self):
        """
        Return True if any of this connections endpoints are
        established. Multiple endpoints can be specified of
        differnet types (bind and connect). This property can
        returning True if either isListening or isConnected
        are True.
        """
        return self.isListening or self.isConnected

    def connect(self, factory):
        """
        What clients do.

        The use of deferreds here is somewhat of an artiface, providing API
        similarity with Twisted code more than anything else. What's async in
        txZMQ is really the reactor checking the socket's file descriptor to
        see if there's data available to read or write.
        """
        try:
            self._connectOrBind(factory)
        except Exception, err:
            msg = util.buildErrorMessage(err)
            return defer.fail(exceptions.ConnectionError(msg))
        else:
            return defer.succeed(self)

    def listen(self, factory):
        """
        What servers do. This is Twisted-speak for "bind."

        For notes about the use of deferred here, see the deffered comment in
        the docstring for ZmqConnection.connect.
        """
        try:
            self._connectOrBind(factory)
        except Exception, err:
            logging.exception(err)
            msg = util.buildErrorMessage(err)
            return defer.fail(exceptions.ListenError(msg))
        else:
            return defer.succeed(self)

    def connectionLost(self, reason):
        """
        Called when the connection was lost.

        Part of L{IFileDescriptor}.

        This is called when the connection on a selectable object has been
        lost.  It will be called whether the connection was closed explicitly,
        an exception occurred in an event handler, or the other end of the
        connection closed it first.

        @param reason: A failure instance indicating the reason why the
                       connection was lost.  L{error.ConnectionLost} and
                       L{error.ConnectionDone} are of special note, but the
                       failure may be of other classes as well.
        """
        log.err(reason, "Connection to ZeroMQ lost in %r" % (self))
        if self.factory:
            self.factory.reactor.removeReader(self)

    def shutdown(self):
        """
        Shutdown connection and socket.
        """
        self.factory.reactor.removeReader(self)
        self.factory.connections.discard(self)
        self.socket.close()
        self.isConnected = False
        self.isListening = False
        self.socket = None
        self.factory = None

    def fileno(self):
        """
        Part of L{IFileDescriptor}.

        @return: The platform-specified representation of a file descriptor
                 number.
        """
        return self.fd

    def logPrefix(self):
        """
        Part of L{ILoggingContext}.

        @return: Prefix used during log formatting to indicate context.
        @rtype: C{str}
        """
        return 'ZMQ'

    def getSocketOptions(self, options):
        """
        Return the socket option settings

        @param options: Socket options, eg. [tx0mq.constants.LINGER]
        @type options: C{list}
        """
        return [self.socket.getsockopt(opt) for opt in options]

    def setSocketOptions(self, opts):
        """
        Set options on the socket.

        @param opts: Socket options, eg. {tx0mq.constants.LINGER : 0}
        @type opts: C{dict}
        """
        for opt, value in opts.items():
            print "attempting to set socket option %s to %s" % (opt, value)
            try:
                self.socket.setsockopt(opt, value)
            except error.ZMQError:
                # ignore errors raised to options that likely
                # do not apply to the particular socket kind.
                pass

    def _readMultipart(self):
        """
        Read multipart in non-blocking manner, returns with ready message
        or raising exception (in case of no more messages available).
        """
        while True:
            self.recv_parts.append(self.socket.recv(constants.NOBLOCK))
            if not self.socket.getsockopt(constants.RCVMORE):
                result, self.recv_parts = self.recv_parts, []
                return result

    def doRead(self):
        """
        Some data is available for reading on your descriptor.

        ZeroMQ is signalling that we should process some events.

        Part of L{IReadDescriptor}.
        """
        events = self.socket.getsockopt(constants.EVENTS)
        if (events & constants.POLLIN) == constants.POLLIN:
            while True:
                if self.factory is None:  # disconnected
                    return
                try:
                    message = self._readMultipart()
                except error.ZMQError as e:
                    if e.errno == constants.EAGAIN:
                        break
                    raise e
                log.callWithLogger(self, self._messageReceived, message)
        if (events & constants.POLLOUT) == constants.POLLOUT:
            self._startWriting()

    def _startWriting(self):
        """
        Start delivering messages from the queue.
        """
        while self.queue:
            try:
                self.socket.send(
                    self.queue[0][1], constants.NOBLOCK | self.queue[0][0])
            except error.ZMQError as e:
                if e.errno == constants.EAGAIN:
                    break
                self.queue.popleft()
                raise e
            self.queue.popleft()

    def send(self, message):
        """
        Send message via ZeroMQ.

        @param message: message data
        """
        if not hasattr(message, '__iter__'):
            self.queue.append((0, message))
        else:
            self.queue.extend([(constants.SNDMORE, m) for m in message[:-1]])
            self.queue.append((0, message[-1]))

        # this is crazy hack: if we make such call, zeromq happily signals
        # available events on other connections
        self.socket.getsockopt(constants.EVENTS)

        self._startWriting()

    def _messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ. This method can be used
        to perform additonal actions on the message prior to notifying
        the user through the messageReceived method. This is used to
        extract topics from pub/sub messages, extract identifiers from
        router/dealer messages, etc.

        @param message: message data
        """
        # To cater for multi-part messages and to present a consistent
        # interface to messageReceived a list is always passed, even if
        # there is only one message part.
        if type(message) != types.ListType:
            message = [message]
        self.messageReceived(message)

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        raise NotImplementedError(self)
