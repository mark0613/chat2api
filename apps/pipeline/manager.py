import aiohttp
from typing import Dict, List, Any

from utils.Logger import logger
from utils.configs import pipeline_api_url, pipeline_api_key, pipeline_enable


class PipelineManager:
    def __init__(self):
        self.pipelines_cache = {}
        self.api_url = pipeline_api_url
        self.api_key = pipeline_api_key
        self.headers = (
            {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )

    async def init(self):
        if pipeline_enable:
            try:
                await self.get_pipeline_list()
            except Exception:
                pass

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        if not self.api_url:
            raise ValueError("Pipeline API URL not configured")

        url = f"{self.api_url}{endpoint}"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.request(method, url, **kwargs) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(
                            f"Error {method} {endpoint}: {response.status} - {error_text}"
                        )

                    # Handle potential empty response for DELETE
                    if method.upper() == "DELETE" and response.content_length == 0:
                        # Or return a standard success message if preferred
                        return {
                            "status": "success",
                            "message": "Pipeline deleted successfully",
                        }

                    return await response.json()
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error to {url}: {str(e)}")
            raise ValueError(f"Could not connect to Pipeline API at {url}") from e
        except Exception as e:
            logger.error(
                f"Error during pipeline API request ({method} {url}): {str(e)}"
            )
            raise

    async def get_pipeline_list(self) -> List[Dict[str, Any]]:
        data = await self._make_request("GET", "/pipelines")
        pipelines = data.get("data", [])

        new_cache = {}
        for pipeline in pipelines:
            pipeline["url"] = self.api_url
            cache_key = pipeline["id"]
            new_cache[cache_key] = pipeline
        self.pipelines_cache = new_cache

        return pipelines

    async def get_pipeline_valves(self, pipeline_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"/{pipeline_id}/valves")

    async def update_pipeline_valves(
        self,
        pipeline_id: str,
        valves: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self._make_request(
            "POST", f"/{pipeline_id}/valves/update", json=valves
        )

    async def get_pipeline_valves_specs(self, pipeline_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"/{pipeline_id}/valves/spec")

    async def upload_pipeline(
        self,
        file_content: bytes,
        file_name: str,
    ) -> Dict[str, Any]:
        form_data = aiohttp.FormData()
        form_data.add_field("file", file_content, filename=file_name)

        # Need to handle FormData separately from _make_request json helper
        if not self.api_url:
            raise ValueError("Pipeline API URL not configured")

        url = f"{self.api_url}/pipelines/upload"
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(url, data=form_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(
                            f"Error uploading pipeline: {response.status} - {error_text}"
                        )
                    return await response.json()
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error during upload to {url}: {str(e)}")
            raise ValueError(
                f"Could not connect to Pipeline API at {url} for upload"
            ) from e
        except Exception as e:
            logger.error(f"Error uploading pipeline: {str(e)}")
            raise ValueError("Failed to upload pipeline") from e

    async def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        try:
            result = await self._make_request(
                "DELETE", "/pipelines/delete", json={"id": pipeline_id}
            )

            # 從緩存中刪除 (key is now just pipeline_id)
            if pipeline_id in self.pipelines_cache:
                del self.pipelines_cache[pipeline_id]

            return result
        except Exception as e:
            logger.error(f"Unexpected error deleting pipeline {pipeline_id}: {str(e)}")
            raise ValueError(f"Failed to delete pipeline {pipeline_id}") from e


pipeline_manager = PipelineManager()
