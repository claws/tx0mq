"""
ZeroMQ PUSH-PULL wrappers.
"""
from tx0mq import constants
from tx0mq.connection import ZmqConnection


class ZmqPushConnection(ZmqConnection):
    """
    Publishing in broadcast manner.
    """
    socketType = constants.PUSH

    def push(self, message):
        """
        Push a message L{message}.

        @param message: message data
        @type message: C{str}
        """
        self.send(message)


class ZmqPullConnection(ZmqConnection):
    """
    Pull messages from a socket
    """
    socketType = constants.PULL

