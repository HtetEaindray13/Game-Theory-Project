import settings


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1

    def world_to_screen(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        return (
            settings.TILE_SIZE * tile_x + self.x,
            settings.HUD_HEIGHT + settings.TILE_SIZE * tile_y + self.y,
        )

    def screen_to_tile(self, sx: int, sy: int) -> tuple[int, int] | None:
        map_right = settings.SCREEN_WIDTH - settings.PANEL_WIDTH
        map_bottom = settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT
        if sx < 0 or sx >= map_right or sy < settings.HUD_HEIGHT or sy >= map_bottom:
            return None
        x = int((sx - self.x) // settings.TILE_SIZE)
        y = int((sy - settings.HUD_HEIGHT - self.y) // settings.TILE_SIZE)
        if 0 <= x < settings.GRID_COLS and 0 <= y < settings.GRID_ROWS:
            return x, y
        return None

    def clamp(self) -> None:
        map_w = settings.SCREEN_WIDTH - settings.PANEL_WIDTH
        map_h = settings.SCREEN_HEIGHT - settings.HUD_HEIGHT - settings.BOTTOM_BAR_HEIGHT
        self.x = min(0, max(map_w - settings.MAP_WIDTH, self.x))
        self.y = min(0, max(map_h - settings.MAP_HEIGHT, self.y))

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
        self.clamp()

    def follow(self, animal) -> None:
        if not animal:
            return
        map_w = settings.SCREEN_WIDTH - settings.PANEL_WIDTH
        map_h = settings.SCREEN_HEIGHT - settings.HUD_HEIGHT - settings.BOTTOM_BAR_HEIGHT
        self.x = map_w // 2 - animal.x * settings.TILE_SIZE - settings.TILE_SIZE // 2
        self.y = map_h // 2 - animal.y * settings.TILE_SIZE - settings.TILE_SIZE // 2
        self.clamp()
