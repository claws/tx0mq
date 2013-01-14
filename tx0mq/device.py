"""
ZeroMQ device
"""

from tx0mq import constants


class ZmqDevice(object):
    """
    A ZMQ device 
    """

    def __init__(self, device_type):
        self.device_type = device_type


class ZmqQueue(ZmqDevice):
    """
    A ZMQ queue device 

    frontend: The connection for incoming messages
    backend: The connection for outgoing messages

    This device assumes that the frontend and backend connections
    are already established (ie. connect ior listen has already 
    been called)
    """
    def __init__(self, frontend, backend):
        """
        """
        super(ZmqQueue, self).__init__(constants.QUEUE)
        self.frontend = frontend
        self.backend = backend

        self.frontend.messageReceived = self._frontendMessageReceived
#        self.backend.messageReceived = self._backendMessageReceived


    def __repr__(self):
        return "%s (frontend: %s, backkend: %s)" % (self.__class__.__name__,
                                                    self.frontend,
                                                    self.backend)

    def _frontendMessageReceived(self, message, identifier):
        """
        Route request messages from frontend to backend connection
        """
        print "frontend received: %s" % message
        def returnResponse(msg, identifier):
            print "Returning response to through frontend: %s, %s" % (identifier, msg)
            self.frontend.reply(identifier, msg)
        d = self.backend.request(message)
        d.addCallback(returnResponse, identifier)
   
#    def _backendMessageReceived(self, message, identifier):
#        """
#        Route messages from backend to frontend connection
#        """
#        self.frontend.reply(identifier, message)

class ZmqForwarder(ZmqDevice):
    """
    A ZMQ forwarder device 

    incoming: The connection for incoming messages
    outgoing: The connection for outgoing messages
    """
    def __init__(self, incoming, outgoing):
        """
        """
        super(ZmqQueue, self).__init__(constants.FORWARDER)
        self.incoming = incoming
        self.outgoing = outgoing


class ZmqStreamer(ZmqDevice): 
    pass


