"""Read and write model files in the private Supabase Storage bucket (server only)."""

import httpx


class ModelStorage:
    def __init__(
        self,
        supabase_url: str,
        service_key: str,
        bucket: str,
        http: httpx.AsyncClient | None = None,
    ) -> None:
        if not supabase_url or not service_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for models")
        self._bucket = bucket
        self._http = http or httpx.AsyncClient(
            base_url=f"{supabase_url.rstrip('/')}/storage/v1",
            # The service-role key bypasses every access rule, so it lives only on the server.
            headers={"Authorization": f"Bearer {service_key}", "apikey": service_key},
            timeout=60.0,
        )

    async def upload(self, path: str, data: bytes) -> None:
        response = await self._http.post(
            f"/object/{self._bucket}/{path}",
            content=data,
            headers={"Content-Type": "application/octet-stream", "x-upsert": "true"},
        )
        response.raise_for_status()

    async def download(self, path: str) -> bytes:
        response = await self._http.get(f"/object/{self._bucket}/{path}")
        response.raise_for_status()
        return response.content

    async def aclose(self) -> None:
        await self._http.aclose()
