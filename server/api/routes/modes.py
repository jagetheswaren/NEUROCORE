from fastapi import APIRouter, Depends
from core.modes import MODES

router = APIRouter(prefix="/modes", tags=["Modes"])

@router.get("")
def list_modes():
    modes_info = []
    for mode_name, mode_obj in MODES.items():
        modes_info.append({
            "name": mode_name,
            "description": mode_obj.prompt.split("\n")[0] if mode_obj.prompt else "",
            "color": mode_obj.color
        })
    return {"modes": modes_info}
