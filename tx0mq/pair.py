"""
ZeroMQ PAIR wrapper
"""
from tx0mq import constants
from tx0mq.connection import ZmqConnection


class ZmqPairConnection(ZmqConnection):
    """
    Bidirectional, stateless connection.
    """
    socketType = constants.PAIR

