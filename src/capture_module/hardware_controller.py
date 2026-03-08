import time

class MockController:
    """
    아두이노(Hardware)가 없을 때,
    시리얼 통신 대신 콘솔에 입력 명령을 출력만 해주는 가짜(Mock) 제어기입니다.
    추후 실제 Arduino 설정이 오면 이와 똑같은 메서드를 가진 ArduinoController 클래스만 갈아끼우면 됩니다.
    """
    def __init__(self):
        print("[MOCK_HARDWARE] 가상 하드웨어 제어기가 초기화되었습니다.")

    def press_button(self, button: str, delay_after: float = 0.5):
        """특정 버튼을 짧게 누르고 뗍니다 (예: A, B, X, Y, UP, DOWN)"""
        print(f"🎮 [MOCK_INPUT] 버튼 입력 전송 -> [{button}]")
        time.sleep(1/30) # 대략 1프레임 누르고 있음 가정
        print(f"🎮 [MOCK_INPUT] 버튼 뗌 -> [{button}]")
        
        if delay_after > 0:
            time.sleep(delay_after)

    def soft_reset(self):
        """소프트 리셋 명령 (A+B+X+Y 등 동시에 누르기)"""
        print(f"🚨 [MOCK_INPUT] 소프트 리셋 (A+B+X+Y) 전송!")
        time.sleep(2.0) # 리셋 후 화면 뜰 때까지 대기
