import requests
from typing import Optional, Dict, Any


class APIRequester:
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        url = self._build_url(path)
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=self.headers,
                auth=None,
                params=params,
                data=data,
                json=json,
                files=files,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {e}")
            raise

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("get", path, params=params).json()
