import sys
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 필요한 폴더 보장
(Path(PROJECT_ROOT / "captures" / "raw")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "captures" / "roi")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "captures" / "shiny_candidates")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "refs" / "starters")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "templates")).mkdir(parents=True, exist_ok=True)


def print_header():
    print("=" * 50)
    print(" 포켓몬 이로치 체크 봇 - Capture CLI ")
    print("=" * 50)


def print_menu():
    print("\n메뉴를 선택하세요.")
    print("1. 캡처 실행")
    print("2. 사용 가능한 카메라 찾기")
    print("3. 종료")
    print("-" * 50)


def run_find_cameras():
    try:
        from capture_module.capture_find import find_available_cameras
    except Exception as e:
        print(f"[ERROR] capture_find 모듈 import 실패: {e}")
        return

    print("\n[INFO] 사용 가능한 카메라를 찾는 중입니다...\n")

    try:
        cameras = find_available_cameras(max_index=10)
    except Exception as e:
        print(f"[ERROR] 카메라 검색 중 예외 발생: {e}")
        return

    if not cameras:
        print("[WARN] 사용 가능한 카메라를 찾지 못했습니다.")
        return

    print("[INFO] 사용 가능한 카메라 목록")
    for cam in cameras:
        idx = cam.get("index")
        backend = cam.get("backend")
        width = cam.get("width")
        height = cam.get("height")
        print(f"  - index={idx}, backend={backend}, resolution={width}x{height}")


def run_capture():
    try:
        from capture_module.capture_run import run_capture_session
    except Exception as e:
        print(f"[ERROR] capture_run 모듈 import 실패: {e}")
        return

    cam_input = input("카메라 번호를 입력하세요 (예: 0): ").strip()

    if not cam_input.isdigit():
        print("[ERROR] 숫자만 입력해주세요.")
        return

    camera_index = int(cam_input)

    print("\n[INFO] 캡처 세션을 시작합니다.")
    print("[INFO] 조작 방법:")
    print("  - ESC : 영상 종료")
    print("  - s   : 현재 프레임 저장")
    print("  - q   : 터미널에서 q 입력 후 Enter 로 종료")
    print("-" * 50)

    try:
        run_capture_session(
            camera_index=camera_index,
            save_dir=str(PROJECT_ROOT / "captures" / "raw"),
        )
    except Exception as e:
        print(f"[ERROR] 캡처 실행 중 예외 발생: {e}")


def main():
    print_header()

    while True:
        print_menu()
        choice = input("입력 > ").strip()

        if choice == "1":
            run_capture()
        elif choice == "2":
            run_find_cameras()
        elif choice == "3":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("[WARN] 올바른 메뉴 번호를 입력해주세요.")


if __name__ == "__main__":
    main()