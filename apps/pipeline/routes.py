from typing import Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from apps.user.utils import get_current_user_from_cookie
from .manager import pipeline_manager

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("/list")
async def list_pipelines(user=Depends(get_current_user_from_cookie)):
    try:
        pipelines = await pipeline_manager.get_pipeline_list()
        return {"data": pipelines}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing pipelines: {str(e)}"
        )


@router.post("/upload")
async def upload_pipeline(
    file: UploadFile = File(...), user=Depends(get_current_user_from_cookie)
):
    try:
        content = await file.read()
        result = await pipeline_manager.upload_pipeline(content, file.filename)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading pipeline: {str(e)}"
        )


@router.delete("/delete")
async def delete_pipeline(id: str, user=Depends(get_current_user_from_cookie)):
    try:
        result = await pipeline_manager.delete_pipeline(id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting pipeline: {str(e)}"
        )


@router.get("/{pipeline_id}/valves")
async def get_pipeline_valves(
    pipeline_id: str, user=Depends(get_current_user_from_cookie)
):
    try:
        return await pipeline_manager.get_pipeline_valves(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting valves: {str(e)}")


@router.get("/{pipeline_id}/valves/spec")
async def get_pipeline_valves_specs(
    pipeline_id: str, user=Depends(get_current_user_from_cookie)
):
    try:
        return await pipeline_manager.get_pipeline_valves_specs(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting valve specs: {str(e)}"
        )


@router.post("/{pipeline_id}/valves/update")
async def update_pipeline_valves(
    pipeline_id: str, valves: Dict[str, Any], user=Depends(get_current_user_from_cookie)
):
    try:
        return await pipeline_manager.update_pipeline_valves(pipeline_id, valves)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating valves: {str(e)}")
