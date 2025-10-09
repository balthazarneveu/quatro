import time
import psutil
from collections import deque


class PerformanceTracker:
    def __init__(self):
        self.last_time = time.time()
        self.frame_count = 0
        self.process = psutil.Process()
        self.cpu_samples = deque(maxlen=10)

    def track_performance(self):
        current_time = time.time()
        self.frame_count += 1
        elapsed_time = current_time - self.last_time
        if elapsed_time >= 1.0:  # Log FPS every second
            fps = self.frame_count / elapsed_time
            cpu_usage, memory_usage = self.track_memory_cpu()
            print(
                f"FPS: {fps:.2f} CPU Usage: {cpu_usage:.2f}% Memory Usage: {memory_usage:.2f} MB",
                end="\r",
            )
            self.last_time = current_time
            self.frame_count = 0

    def track_memory_cpu(self):
        cpu = self.process.cpu_percent(interval=None)
        self.cpu_samples.append(cpu)
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
        mem = self.process.memory_info().rss / (1024 * 1024)
        return avg_cpu, mem
