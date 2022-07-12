from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from .enums import MessageType, PoolType


class Signature(BaseModel):
    uuid: str
    value: str
    description: Optional[str]
    created_at: datetime


class Pool(BaseModel):
    type: PoolType

    tag: Optional[str]
    address: str
    encrypted: bool

    public: bool
    description: Optional[str]

    created_at: datetime
    creator_signature: Optional[Signature]


class Pools(BaseModel):
    total: int
    count: int
    pools: List[Pool]


class _Message(BaseModel):
    type: MessageType
    id: int
    date: datetime
    signature: Optional[Signature]


class PlaintextMessage(_Message):
    plaintext: str


class EncryptedMessage(_Message):
    AES_ciphertext: bytes
    AES_nonce: bytes
    AES_tag: bytes


class Messages(BaseModel):
    total: int
    count: int
    encrypted: bool
    messages: List[PlaintextMessage | EncryptedMessage]


class Node(BaseModel):
    name: str
    description: str
    version: str
    uptime: int
    pools_count: int
    signatures_count: int
