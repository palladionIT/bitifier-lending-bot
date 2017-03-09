import abc


class CommonLowLevel(object):
    __metaclass__ = abc.ABCMeta

    # Checks if authentication is possible
    @abc.abstractmethod
    def check_authentication(self, account):
        return

    # Basic request on unauthenticated endpoint
    @abc.abstractmethod
    def query_public(self, parameter):
        return

    # Basic request on authenticated endpoint
    @abc.abstractmethod
    def query_private(self, parameter, account):
        return