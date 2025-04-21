import aiohttp
from typing import Dict, Any, Optional

from utils.Logger import logger
from utils.configs import pipeline_api_url, pipeline_enable
from .manager import pipeline_manager

# XXX: 暫時假定所有 pipeline 的 "pipelines" 欄位都是 *
# TODO: 根據 "pipelines" 進行過濾


async def process_pipeline_inlet_filter(
    payload: Dict[str, Any],
    user: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not pipeline_enable:
        return payload

    filters = [
        pipeline["id"] for pipeline in pipeline_manager.pipelines_cache.values()
    ]

    async with aiohttp.ClientSession() as session:
        for filter in filters:
            request_data = {"user": user, "body": payload}
            headers = pipeline_manager.headers

            try:
                async with session.post(
                    f"{pipeline_api_url}/{filter}/filter/inlet",
                    json=request_data,
                    headers=headers,
                    timeout=10,
                ) as response:
                    payload = await response.json()
                    response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                res = (
                    await response.json()
                    if response.content_type == "application/json"
                    else {}
                )
                if "detail" in res:
                    raise Exception(res["detail"])
            except Exception as e:
                logger.exception(f"Connection error: {e}")

    return payload


async def process_pipeline_outlet_filter(
    payload: Dict[str, Any],
    user: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not pipeline_enable:
        return payload

    filters = [
        pipeline["id"] for pipeline in pipeline_manager.pipelines_cache.values()
    ]

    async with aiohttp.ClientSession() as session:
        for filter in filters:
            request_data = {"user": user, "body": payload}
            headers = pipeline_manager.headers
            try:
                async with session.post(
                    f"{pipeline_api_url}/{filter}/filter/outlet",
                    json=request_data,
                    headers=headers,
                    timeout=10,
                ) as response:
                    payload = await response.json()
                    response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                try:
                    res = (
                        await response.json()
                        if response.content_type == "application/json"
                        else {}
                    )
                    if "detail" in res:
                        raise Exception(response.status, res["detail"])
                except Exception:
                    pass
            except Exception as e:
                logger.exception(f"Connection error: {e}")

    return payload
