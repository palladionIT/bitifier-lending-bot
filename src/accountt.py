class Account:

    def __init__(self, id, mail, name, key, secret, type, exchange, status):
        self.UserID = id
        self.UserMail = mail
        self.UserName = name
        self.APIKey = key
        self.APISecret = secret
        self.Type = type
        self.Exchange = exchange
        self.Status = status

    @property
    def UserID(self):
        return self.__UserID

    @UserID.setter
    def UserID(self, value):
        self.__UserID = value

    @property
    def UserMail(self):
        return self.__UserMail

    @UserMail.setter
    def UserMail(self, value):
        self.__UserMail =  value

    @property
    def UserName(self):
        return self.__UserName

    @UserName.setter
    def UserName(self, value):
        self.__UserName = value

    @property
    def APIKey(self):
        return self.__APIKey

    @APIKey.setter
    def APIKey(self, value):
        self.__APIKey = value

    @property
    def APISecret(self):
        return self.__APISecret

    @APISecret.setter
    def APISecret(self, value):
        self.__APISecret = value

    @property
    def Type(self):
        return self.__Type

    @Type.setter
    def Type(self, value):
        self.__Type = value

    @property
    def Exchange(self):
        return self.__Exchange

    @Exchange.setter
    def Exchange(self, value):
        self.__Exchange = value

    @property
    def Status(self):
        return self.__Status

    @Status.setter
    def Status(self, value):
        self.__Status = value