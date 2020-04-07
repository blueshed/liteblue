""" simple broadcaster """
from liteblue.handlers.broadcaster import Broadcaster


class SimpleBroadcaster(Broadcaster):
    """ test broadcaster """

    documents = []

    def broadcast(self, document):
        """ append document to our list """
        self.documents.append(document)
