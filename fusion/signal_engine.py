from typing import List


class SignalEngine:
    def __init__(self, confirm_n: int, cooldown_n: int):
        self.confirm_n = confirm_n
        self.cooldown_n = cooldown_n
        self.buffer: List[str] = []
        self.last_signal = "NEUTRAL"
        self.cooldown_counter = 0

    def generate(self, final_factor: float, threshold: float) -> str:
        direction = "NEUTRAL"
        if final_factor > threshold:
            direction = "LONG"
        elif final_factor < -threshold:
            direction = "SHORT"

        if direction == "NEUTRAL":
            self.buffer.clear()
            return "NEUTRAL"

        self.buffer.append(direction)
        if len(self.buffer) < self.confirm_n:
            return "NEUTRAL"

        if len(self.buffer) > self.confirm_n:
            self.buffer = self.buffer[-self.confirm_n :]

        if len(set(self.buffer)) == 1:
            if self.cooldown_counter > 0 and direction != self.last_signal:
                self.cooldown_counter -= 1
                return self.last_signal
            signal = direction
            if signal != self.last_signal:
                self.cooldown_counter = self.cooldown_n
            self.last_signal = signal
            return signal
        return "NEUTRAL"
