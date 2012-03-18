"""
ZeroMQ REQ/REP wrappers.
"""
import types
import uuid
import warnings

from tx0mq import constants

from twisted.internet import defer

from tx0mq.connection import ZmqConnection


class ZmqReqConnection(ZmqConnection):
    """
    A REQ connection.

    This is implemented with an underlying DEALER socket, even though
    semantics are close to REQ socket.
    """
    socketType = constants.DEALER

    # the number of new UUIDs to generate when the pool runs out of them
    UUID_POOL_GEN_SIZE = 5

    def __init__(self, endpoint):
        ZmqConnection.__init__(self, endpoint)
        self._requests = {}
        self._uuids = []

    def _getNextId(self):
        """
        Returns an unique id.

        By default, generates pool of UUID in increments
        of C{UUID_POOL_GEN_SIZE}. Could be overridden to
        provide custom ID generation.

        @return: generated unique "on the wire" message ID
        @rtype: C{str}
        """
        if not self._uuids:
            self._uuids.extend(str(uuid.uuid4())
                    for _ in range(self.UUID_POOL_GEN_SIZE))
        return self._uuids.pop()

    def _releaseId(self, msgId):
        """
        Release message ID to the pool.

        @param msgId: message ID, no longer on the wire
        @type msgId: C{str}
        """
        self._uuids.append(msgId)
        if len(self._uuids) > 2 * self.UUID_POOL_GEN_SIZE:
            self._uuids[-self.UUID_POOL_GEN_SIZE:] = []

    def request(self, message):
        """
        Send L{message}.

        @param messageParts: message data
        @type messageParts: C{tuple}
        """
        d = defer.Deferred()
        messageId = self._getNextId()
        self._requests[messageId] = d
        if type(message) != types.ListType:
            message = [message]
        messageParts = [messageId, ''] + message
        self.send(messageParts)
        return d

    def _messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        msgId, _, msg = message[0], message[1], message[2:]
        d = self._requests.pop(msgId)
        self._releaseId(msgId)
        d.callback(msg)




class ZmqRepConnection(ZmqConnection):
    """
    A REP connection.

    This is implemented with an underlying ROUTER socket, but the semantics
    are close to REP socket.
    """
    socketType = constants.ROUTER

    def __init__(self, endpoint):
        ZmqConnection.__init__(self, endpoint)
        self._routingInfo = {}  # keep track of routing info

    def reply(self, identifier, message):
        """
        Send L{message} with specified L{tag}.

        @param identifier: message uuid
        @type identifier: C{str}
        @param message: message data
        @type message: C{str}
        """
        routingInfo = self._routingInfo.pop(identifier)
        if type(message) != types.ListType:
            message = [message]
        message = routingInfo + [identifier, ''] + message
        self.send(message)

    def _messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        i = message.index('')
        assert i > 0
        (routingInfo, identifier, payload) = (
            message[:i - 1], message[i - 1], message[i + 1:])
        messageParts = payload[0:]
        self._routingInfo[identifier] = routingInfo
        self.messageReceived(messageParts, identifier)

    def messageReceived(self, message, identifier):
        """
        Called on incoming message.

        @param messageParts: message data
        @type messageParts: C{list}
        @param messageId: message uuid
        @type messageId: C{str}
        """
        raise NotImplementedError(self)


