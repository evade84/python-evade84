from typing import Any, Dict, List, NoReturn, Optional, Union

import requests

from . import auth, enums, exceptions, models


class Client:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    def _parse_response_error(response: requests.Response) -> tuple[str, str, str]:
        json = response.json()
        return json["error_id"], json["error_message"], json["error_details"]

    def _build_url(self, path: str):
        return f"{self.base_url}{path}"

    def _parse_response(self, response: requests.Response):
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise exceptions.IncorrectInputException(*self._parse_response_error(response))
        elif response.status_code == 403:
            raise exceptions.AccessDeniedException(*self._parse_response_error(response))
        elif response.status_code == 404:
            raise exceptions.NotFoundException(*self._parse_response_error(response))
        elif response.status_code == 409:
            raise exceptions.ConflictException(*self._parse_response_error(response))
        elif response.status_code == 422:
            raise exceptions.UnprocessableEntityException(*self._parse_response_error(response))
        elif response.status_code == 500:
            raise exceptions.InternalServerErrorException(*self._parse_response_error(response))
        else:
            raise ValueError(
                f"Unknown response status code: {response.status_code}. Response content: {response.text}."
            )

    def _api_request(
        self,
        method: str,
        path: str,
        query_params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], NoReturn]:
        url = self._build_url(path)
        if method == "get":
            resp = requests.get(url, params=query_params)
        elif method == "post":
            resp = requests.post(url, params=query_params, json=json_data)
        elif method == "delete":
            resp = requests.delete(url, params=query_params)
        else:
            raise ValueError("Unknown request method.")
        return self._parse_response(resp)

    def create_pool(
        self,
        pool_type: enums.PoolType,
        master_key: str,
        tag: Optional[str] = None,
        description: Optional[str] = None,
        public: Optional[bool] = None,
        encrypted: Optional[bool] = None,
        creator_signature: Optional[auth.SignatureAuthorization] = None,
        writer_key: Optional[str] = None,
        reader_key: Optional[str] = None,
    ) -> models.Pool:
        resp = self._api_request(
            "post",
            "/pool/create",
            query_params={
                "pool_type": pool_type,
            },
            json_data={
                "tag": tag,
                "description": description,
                "public": public,
                "encrypted": encrypted,
                "creator_signature": creator_signature.dict() if creator_signature else None,
                "master_key": master_key,
                "writer_key": writer_key,
                "reader_key": reader_key,
            },
        )
        return models.Pool(**resp)

    def update_pool(
        self,
        identifier: str,
        master_key: str,
        new_description: Optional[str] = None,
        new_master_key: Optional[str] = None,
        new_writer_key: Optional[str] = None,
        new_reader_key: Optional[str] = None,
    ) -> models.Pool:
        resp = self._api_request(
            "post",
            f"/pool/{identifier}/update",
            query_params={"identifier": identifier, "master_key": master_key},
            json_data={
                "new_description": new_description,
                "new_master_key": new_master_key,
                "new_writer_key": new_writer_key,
                "new_reader_key": new_reader_key,
            },
        )
        return models.Pool(**resp)

    def delete_pool(self, identifier: str, master_key: str) -> models.Pool:
        resp = self._api_request(
            "delete",
            path=f"/pool/{identifier}/delete",
            query_params={"identifier": identifier, "master_key": master_key},
        )
        return models.Pool(**resp)

    def get_pool(
        self,
        identifier: str,
        master_key: Optional[str] = None,
        writer_key: Optional[str] = None,
        reader_key: Optional[str] = None,
    ) -> models.Pool:
        resp = self._api_request(
            "get",
            f"/pool/{identifier}",
            {
                "master_key": master_key,
                "writer_key": writer_key,
                "reader_key": reader_key,
            },
        )
        return models.Pool(**resp)

    def list_public_pools(self, limit: int, offset: int) -> models.Pools:
        resp = self._api_request("get", "/pool/list", query_params={"limit": limit, "offset": offset})
        return models.Pools(**resp)

    def read_pool(
        self,
        identifier: str,
        first: Optional[int] = None,
        last: Optional[int] = None,
        reader_key: Optional[str] = None,
    ):
        resp = self._api_request(
            "get",
            f"/pool/{identifier}/read",
            {"first": first, "last": last, "reader_key": reader_key},
        )
        return models.Messages(**resp)

    def write_to_pool(
        self,
        identifier: str,
        writer_key: str,
        message_type: enums.MessageType,
        signature: Optional[auth.SignatureAuthorization] = None,
        plaintext: Optional[str] = None,
        AES_ciphertext: Optional[str] = None,
        AES_nonce: Optional[str] = None,
        AES_tag: Optional[str] = None,
    ):
        resp = self._api_request(
            "post",
            f"/pool/{identifier}/write",
            query_params={"message_type": message_type, "writer_key": writer_key},
            json_data={
                "signature": signature.dict() if signature else None,
                "plaintext": plaintext,
                "AES_ciphertext": AES_ciphertext,
                "AES_nonce": AES_nonce,
                "AES_tag": AES_tag,
            },
        )
        if message_type == enums.MessageType.plaintext:
            return models.PlaintextMessage(**resp)
        elif message_type == enums.MessageType.encrypted:
            return models.EncryptedMessage(**resp)
        else:
            raise ValueError("Unknown message type.")

    def create_signature(
        self, key: str, value: str | None = None, description: str | None = None
    ) -> models.Signature:
        resp = self._api_request(
            "post",
            "/signature/create",
            json_data={"key": key, "value": value, "description": description},
        )
        return models.Signature(**resp)

    def update_signature(
        self,
        signature: auth.SignatureAuthorization,
        new_value: Optional[str] = None,
        new_description: Optional[str] = None,
        new_key: Optional[str] = None,
    ) -> models.Signature:
        resp = self._api_request(
            "post",
            f"/signature/{signature.uuid}/update",
            query_params={"key": signature.key},
            json_data={
                "new_value": new_value,
                "new_description": new_description,
                "new_key": new_key,
            },
        )
        return models.Signature(**resp)

    def get_signature(self, uuid: str) -> models.Signature:
        resp = self._api_request("get", f"/signature/{uuid}", query_params={"uuid": uuid})
        return models.Signature(**resp)

    def node(self) -> models.Node:
        resp = self._api_request("get", "/node")
        return models.Node(**resp)
