import cv2
import threading
import queue
import sys
from pathlib import Path
from capture_module.capture_save import save_frame
from games.base_game import BaseGamePreset

# msvcrt는 Windows에서만 동작합니다.
if sys.platform == 'win32':
    import msvcrt

def input_listener(q: queue.Queue, stop_event: threading.Event):
    """ 터미널 입력을 비동기적으로 받는 스레드 """
    # Windows 환경에 특화된 non-blocking 입력 감지
    if sys.platform == 'win32':
        while not stop_event.is_set():
            if msvcrt.kbhit():
                cmd = msvcrt.getwche().lower()
                if cmd == 'q':
                    # 엔터키 없이 q만 눌러도 즉시 종료 큐 삽입
                    q.put("quit")
                    break
            else:
                stop_event.wait(0.1)  # CPU 점유율 제어
    else:
        # 비 윈도우 환경 (혹시 모를 호환성)
        while not stop_event.is_set():
            try:
                # 이 방식은 사용자가 인터럽트를 걸기 전까지 블로킹됩니다.
                cmd = input().strip().lower()
                if cmd == "q":
                    q.put("quit")
                    break
            except EOFError:
                break
            except Exception as e:
                print(f"[입력 스레드 오류] {e}")
                break

def run_capture_session(camera_index: int, save_dir: str, game_preset: BaseGamePreset):
    """
    지정된 카메라 인덱스와 게임 프리셋으로 캡처 세션을 시작합니다.
    """
    print(f"\n[INFO] 카메라 {camera_index}번을 엽니다 (CAP_DSHOW)...")
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    # 캡처 퀄리티 기본 설정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print(f"[ERROR] 카메라 {camera_index}번을 열 수 없습니다.")
        return

    print("[INFO] 카메라 연결에 성공했습니다.")
    try:
        backend_name = cap.getBackendName()
    except Exception:
        backend_name = "알 수 없음"
    print(f"[INFO] 현재 캡처 백엔드: {backend_name}")

    print("\n==============================")
    print(" 캡처 세션이 실행 중입니다.")
    print(" 튜토리얼:")
    print("   - 영상 창에서 's' 키: 원본 프레임 캡처 (captures/raw)")
    print("   - 영상 창에서 'r' 키: ROI 프레임 캡처 (captures/roi) - 임시 좌표")
    print("   - 영상 창에서 'ESC' 키: 세션 종료")
    print("   - 터미널 창 활성 상태에서 'q' 키: 세션 종료 (엔터 불필요)")
    print("==============================\n")

    cmd_queue = queue.Queue()
    stop_event = threading.Event()
    
    t = threading.Thread(target=input_listener, args=(cmd_queue, stop_event), daemon=True)
    t.start()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[WARN] 프레임을 읽지 못했습니다. 잠시 대기합니다.")
            cv2.waitKey(100)
            continue

        # 현재 화면 상태 분석
        current_state = game_preset.get_current_state(frame)
        
        # 화면에 텍스트를 그리기 위한 복사본 (원본 프레임 보존)
        display_frame = frame.copy()
        
        # 좌측 상단에 상태 텍스트 출력
        cv2.putText(
            display_frame, 
            f"STATE({game_preset.game_name}): {current_state}", 
            (20, 50), # 텍스트 위치 (x, y)
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.0, # 폰트 크기
            (0, 255, 0) if current_state != "UNKNOWN" else (0, 0, 255), # 식별되면 초록색, 안되면 빨간색
            3, # 선 두께
            cv2.LINE_AA
        )

        cv2.imshow("Capture Session", display_frame)

        # OpenCV 창 키 입력 받기 (1ms 대기)
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            print("[INFO] ESC 입력이 감지되어 캡처를 종료합니다.")
            break
        elif key == ord('s'):
            save_frame(frame, save_dir)
        elif key == ord('r'):
            # 테스트용으로 "pokemon_summary" ROI 만 잘라서 저장
            try:
                roi_frame = game_preset.get_roi_slice(frame, "pokemon_summary")
                roi_dir = str(Path(save_dir).parent / "roi")
                save_frame(roi_frame, roi_dir)
            except Exception as e:
                print(f"[ERROR] ROI 저장 중 예외 발생: {e}")
            
        # 터미널 창 입력 체크
        if not cmd_queue.empty():
            cmd = cmd_queue.get()
            if cmd == "quit":
                print("[INFO] 터미널 종료 명령(q)이 감지되어 캡처를 종료합니다.")
                break

    # 스레드 종류 신호 전송
    stop_event.set()
    
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] 캡처 세션이 안전하게 종료되었습니다.")