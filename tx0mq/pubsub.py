"""
ZeroMQ PUB-SUB wrappers.
"""
import types
from tx0mq import constants
from tx0mq.connection import ZmqConnection


class ZmqPubConnection(ZmqConnection):
    """
    Publishing in broadcast manner.
    """
    socketType = constants.PUB

    def publish(self, message, topic=''):
        """
        Broadcast L{message} with specified L{tag}.

        @param message: message data
        @type message: C{str}
        @param tag: message tag
        @type tag: C{str}
        """
        if type(message) != types.ListType:
            message = [message]
        if topic:
            message = [topic] + message
        self.send(message)


class ZmqSubConnection(ZmqConnection):
    """
    Subscribing to messages.
    """
    socketType = constants.SUB

    def subscribe(self, tag):
        """
        Subscribe to messages with specified tag (prefix).

        @param tag: message tag
        @type tag: C{str}
        """
        self.socket.setsockopt(constants.SUBSCRIBE, tag)

    def unsubscribe(self, tag):
        """
        Unsubscribe from messages with specified tag (prefix).

        @param tag: message tag
        @type tag: C{str}
        """
        self.socket.setsockopt(constants.UNSUBSCRIBE, tag)

    def _messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.
        Pub/Sub messages are always multi-part messages, with 
        the first part representing the message topic.

        @param message: message data
        """
        topic = message[0]
        message = message[1:]
        self.messageReceived(message, topic)

    def messageReceived(self, message, topic):
        """
        Called on incoming message recevied by subscriber

        @param message: message data
        @param tag: message tag
        """
        raise NotImplementedError(self)
