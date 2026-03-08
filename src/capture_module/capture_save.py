import cv2
import time
import numpy as np
from pathlib import Path

def save_frame(frame, save_dir: str):
    """
    현재 프레임을 지정된 디렉토리에 타임스탬프와 함께 저장합니다.
    """
    dir_path = Path(save_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.png"
    filepath = dir_path / filename
    
    # Windows 환경에서 경로에 한글이 포함된 경우 cv2.imwrite가 조용히 실패하는 문제를 해결하기 위해,
    # cv2.imencode와 python 자체 파일 쓰기를 사용하여 저장합니다.
    result, encoded_img = cv2.imencode('.png', frame)
    if result:
        filepath.write_bytes(encoded_img.tobytes())
        print(f"[INFO] 프레임 저장 완료: {filepath}")
    else:
        print(f"[ERROR] 프레임 저장 실패 (인코딩 오류): {filepath}")
        
    return str(filepath)
