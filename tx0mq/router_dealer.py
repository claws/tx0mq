"""
ZeroMQ ROUTER and DEALER connection types
"""

from tx0mq import constants
from tx0mq.connection import ZmqConnection

class ZmqDealerConnection(ZmqConnection):
   """
   A DEALER connection
   """
   socketType = constants.DEALER


class ZmqRouterConnection(ZmqConnection):
   """
   A ROUTER connections
   """
   socketType = constants.ROUTER


