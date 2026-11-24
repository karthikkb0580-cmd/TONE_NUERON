class EmailDeliveryError(Exception):
    def __init__(self, message: str = "Email delivery failed."):
        super().__init__(message)
