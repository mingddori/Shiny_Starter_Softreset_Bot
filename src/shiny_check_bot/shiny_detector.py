import cv2
import numpy as np
from pathlib import Path
from shiny_check_bot.state_check import check_template_match

TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

def is_shiny(frame: np.ndarray, target_name: str) -> bool:
    """
    현재 주어진 프레임(포켓몬 스테이터스 창이어야 함)에서
    지정된 이로치 템플릿 마커(별표 등)가 감지되는지 확인합니다.
    """
    marker_path = TEMPLATE_DIR / f"shiny_{target_name}.png"
    
    # 캡처 퀄리티나 배경 투명도 등에 따라 임계값을 조절해야 할 수 있습니다 (기본 0.85)
    return check_template_match(frame, marker_path, threshold=0.85)