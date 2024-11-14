import psutil
from model import SystemMetrics

def get_metrics():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return SystemMetrics(psutil.cpu_percent(interval=1), memory.percent, disk.percent)

