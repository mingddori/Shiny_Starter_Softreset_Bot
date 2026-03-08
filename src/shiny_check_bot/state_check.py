import cv2
import numpy as np
from pathlib import Path

# 템플릿 이미지가 저장될 기본 경로
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

class GameState:
    UNKNOWN = "UNKNOWN"
    OPENING = "OPENING"
    TITLE = "TITLE"
    CONTINUE_SCREEN = "CONTINUE_SCREEN"
    CHOOSE_STARTER = "CHOOSE_STARTER"
    BULBASAUR_YES = "BULBASAUR_YES"
    NICKNAME_PROMPT = "NICKNAME_PROMPT"
    POKEMON_SUMMARY = "POKEMON_SUMMARY"

# 템플릿 파일명과 GameState를 매핑
TEMPLATE_MAP = {
    "00_opening.png": GameState.OPENING,
    "01_title.png": GameState.TITLE,
    "02_continue.png": GameState.CONTINUE_SCREEN,
    "03_choose.png": GameState.CHOOSE_STARTER,
    "04_bulbasaur_yes.png": GameState.BULBASAUR_YES,
    "05_nickname.png": GameState.NICKNAME_PROMPT,
    "06_pokemon_summary.png": GameState.POKEMON_SUMMARY,
}

def check_template_match(frame: np.ndarray, template_path: Path, threshold: float = 0.8) -> bool:
    """
    주어진 프레임 안에서 특정 템플릿과 매칭되는지 확인합니다.
    (간단한 cv2.matchTemplate 기반)
    """
    if not template_path.exists():
        return False
        
    # Windows 한글 경로 문제 해결을 위해 numpy와 imdecode 사용
    try:
        template_array = np.fromfile(str(template_path), np.uint8)
        template = cv2.imdecode(template_array, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[ERROR] 템플릿 로드 실패 ({template_path.name}): {e}")
        return False

    if template is None:
        return False

    th, tw = template.shape[:2]
    fh, fw = frame.shape[:2]
    if fh < th or fw < tw:
        return False

    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    
    return max_val >= threshold

def get_current_state(frame: np.ndarray) -> str:
    """
    현재 프레임을 분석하여 게임의 주요 상태를 판단합니다.
    TEMPLATE_MAP에 정의된 템플릿들을 순회하며 가장 먼저 매칭되는 상태를 반환합니다.
    """
    for template_name, state in TEMPLATE_MAP.items():
        template_path = TEMPLATE_DIR / template_name
        if check_template_match(frame, template_path, threshold=0.85):
            return state
            
    return GameState.UNKNOWN
