import cv2
import queue
import threading
import sys
import time
from capture_module.capture_save import save_frame
from capture_module.hardware_controller import MockController
from games.base_game import BaseGamePreset

# msvcrt는 Windows에서만 동작합니다.
if sys.platform == 'win32':
    import msvcrt

def input_listener(q: queue.Queue, stop_event: threading.Event):
    """ 터미널 입력을 비동기적으로 받는 스레드 """
    if sys.platform == 'win32':
        while not stop_event.is_set():
            if msvcrt.kbhit():
                cmd = msvcrt.getwche().lower()
                if cmd == 'q':
                    q.put("quit")
                    break
            else:
                stop_event.wait(0.1)
    else:
        while not stop_event.is_set():
            try:
                cmd = input().strip().lower()
                if cmd == "q":
                    q.put("quit")
                    break
            except EOFError:
                break
            except Exception as e:
                print(f"[입력 스레드 오류] {e}")
                break

def start_auto_reset_session(camera_index: int, game_preset: BaseGamePreset):
    """
    캡처를 돌리면서 시나리오에 맞춰 하드웨어 컨트롤러에 명령을 내리는 메인 자동화 루프.
    """
    print(f"\n[INFO] {game_preset.game_name} 이로치 자동 리셋 봇을 시작합니다 (카메라 {camera_index}번).")
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print(f"[ERROR] 카메라 {camera_index}번을 열 수 없습니다.")
        return

    controller = MockController()
    
    print("\n==============================")
    print(" 봇이 화면을 감시하며 입력을 제어합니다.")
    print(" 튜토리얼:")
    print("   - 영상 창에서 'ESC' 키: 세션 강제 종료")
    print("   - 터미널 창 활성 상태에서 'q' 키: 세션 강제 종료")
    print("==============================\n")

    cmd_queue = queue.Queue()
    stop_event = threading.Event()
    
    t = threading.Thread(target=input_listener, args=(cmd_queue, stop_event), daemon=True)
    t.start()

    # 중복 입력을 막기 위한 쿨다운 관리
    last_action_time = time.time()
    ACTION_COOLDOWN = 1.0 # 상태 감지 후 다음 버튼을 누르기까지 최소 1초 대기
    overlay_state = "UNKNOWN"
    
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            cv2.waitKey(100)
            continue

        # --- 자동화 매크로 & 렌더링 최적화 ---
        current_time = time.time()
        
        # ACTION_COOLDOWN 기간 동안은 렉 방지를 위해 불필요한 매칭(vision 검사)을 아예 스킵합니다.
        if current_time - last_action_time <= ACTION_COOLDOWN:
            current_state = "UNKNOWN" # 쿨다운 중엔 화면 판별 생략 (CPU 절약)
        else:
            # 쿨다운이 끝났을 때만 화면을 분석합니다 (30fps 매 프레임 검사 방지)
            current_state = game_preset.get_current_state(frame)
            overlay_state = current_state
            
            # 여기서 각 게임별 구체적인 상태에 따른 처리를 위임
            # process_tick은 (새로운 쿨다운 시간, 루프를 종료해야 하는지 여부)를 리턴합니다.
            new_cooldown, should_stop = game_preset.process_tick(frame, current_state, controller)
            
            last_action_time = time.time()
            ACTION_COOLDOWN = new_cooldown
            
            if should_stop:
                break

        # --- 화면 드로잉 로직 ---
        display_frame = frame.copy()
        cv2.putText(
            display_frame, 
            f"STATE: {overlay_state}", 
            (20, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.5, 
            (0, 255, 0) if overlay_state != "UNKNOWN" else (0, 0, 255), 
            3, 
            cv2.LINE_AA
        )
        # 이로치 판별 보조 텍스트
        cv2.putText(
            display_frame, 
            "TARGET(SHINY): ANY STARTER", 
            (20, 100), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.0, 
            (255, 255, 0), 
            2, 
            cv2.LINE_AA
        )

        cv2.imshow("Bot Auto Session", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            print("[INFO] ESC 입력.")
            break
            
        if not cmd_queue.empty():
            cmd = cmd_queue.get()
            if cmd == "quit":
                print("[INFO] 터미널 종료 명령(q) 감지.")
                break

    stop_event.set()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] 봇 세션이 종료되었습니다.")
