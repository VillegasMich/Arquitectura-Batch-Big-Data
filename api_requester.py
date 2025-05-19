import os
import requests
from typing import Optional, Dict, Any


class APIRequester:
    def __init__(
        self,
        base_url: str,
        output_dir: str = "./json_outputs",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

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

    def get_and_save_file(
        self,
        path: str,
        filename: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        response = self._request("get", path, params=params).text
        output_path = os.path.join(self.output_dir, filename)

        try:
            with open(output_path, mode="w", newline="", encoding="utf-8") as jsonfile:
                jsonfile.write(response)
            print(f"✅ JSON file created: {output_path}")
            return output_path, filename
        except Exception as e:
            print(f"❌ Failed to write JSON file: {e}")
            raise

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self._request("post", path, data=data, json=json).json()

    def download_file(self, path: str, dest_path: str) -> bool:
        url = self._build_url(path)
        try:
            with requests.get(
                url,
                stream=True,
                headers=self.headers,
                auth=None,
                timeout=self.timeout,
            ) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"✅ File downloaded to: {dest_path}")
            return True
        except requests.RequestException as e:
            print(f"❌ Failed to download file: {e}")
            return False
