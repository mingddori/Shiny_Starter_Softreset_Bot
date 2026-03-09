from .base_game import BaseGamePreset

class HGSS_Preset(BaseGamePreset):
    @property
    def game_name(self) -> str:
        return "HeartGold / SoulSilver"

    @property
    def template_dir(self) -> str:
        return "hgss"

    @property
    def roi_config(self) -> dict:
        return {}

    @property
    def template_map(self) -> dict:
        return {}

    def get_current_state(self, frame) -> str:
        return "UNKNOWN"

    def process_tick(self, frame, current_state: str, controller) -> tuple[float, bool]:
        print(f"[{self.game_name}] 모듈은 아직 구현되지 않았습니다. 템플릿과 시나리오 작성이 필요합니다.")
        return 1.0, False
