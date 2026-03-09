from abc import ABC, abstractmethod
import numpy as np
import cv2
import time

class BaseGamePreset(ABC):
    """
    모든 포켓몬 게임 버전이 상속받아야 하는 공통 프리셋 인터페이스.
    각 버전마다 UI 해상도가 다르므로 ROI 좌표와 템플릿 마커 매핑,
    그리고 매크로 동작 시나리오가 다릅니다.
    """
    
    @property
    @abstractmethod
    def game_name(self) -> str:
        """이 프리셋의 게임 이름 반환"""
        pass
    
    @property
    @abstractmethod
    def template_dir(self) -> str:
        """이 프리셋이 사용하는 템플릿 파일들의 루트 경로 이름 반환 (예: frlg, hgss)"""
        pass

    @property
    @abstractmethod
    def roi_config(self) -> dict:
        """해당 게임의 화면별 ROI 좌표 반환"""
        pass

    @property
    @abstractmethod
    def template_map(self) -> dict:
        """템플릿 이미지 파일명과 내부 GameState 열거형을 매핑"""
        pass

    @abstractmethod
    def get_current_state(self, frame: np.ndarray) -> str:
        """현재 프레임을 분석하여 게임의 주요 상태를 판단합니다."""
        pass

    @abstractmethod
    def process_tick(self, frame: np.ndarray, current_state: str, controller) -> tuple[float, bool]:
        """
        현재 프레임과 인식된 상태를 기반으로 이 게임에 맞는 자동 리셋 매크로를 실행합니다.
        반환값: (action_cooldown: float, should_stop: bool)
        - action_cooldown: 다음 연산을 스킵할 시간 (초)
        - should_stop: 이로치를 발견했거나 종료 조건이 달성되어 루프를 탈출해야 할 경우 True
        """
        pass

    # 공통 헬퍼 메서드: ROI 자르기
    def get_roi_slice(self, frame: np.ndarray, roi_name: str) -> np.ndarray:
        if roi_name not in self.roi_config:
            raise ValueError(f"알 수 없는 ROI 이름입니다: {roi_name}")
            
        x, y, w, h = self.roi_config[roi_name]
        
        max_h, max_w = frame.shape[:2]
        end_y = min(max_h, y + h)
        end_x = min(max_w, x + w)
        
        return frame[y:end_y, x:end_x]

    # 공통 헬퍼 메서드: 템플릿 매칭
    def check_template_match(self, frame: np.ndarray, template_path, threshold: float = 0.8) -> bool:
        """
        주어진 프레임 안에서 특정 템플릿과 매칭되는지 확인합니다. (cv2.matchTemplate 기반)
        """
        import os
        from pathlib import Path
        if not Path(template_path).exists():
            return False
            
        try:
            template_array = np.fromfile(str(template_path), np.uint8)
            template = cv2.imdecode(template_array, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"[ERROR] 템플릿 로드 실패 ({Path(template_path).name}): {e}")
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
