class SignatureCredentials:
    uuid: str
    key: str

    def __init__(self, uuid: str, key: str):
        self.uuid = uuid
        self.key = key
        assert self.uuid and self.key, "Both uuid and key must be provided."

    def dict(self) -> dict:
        return {"uuid": self.uuid, "key": self.key}
