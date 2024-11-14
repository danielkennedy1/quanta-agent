from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json

@dataclass_json
@dataclass
class SystemMetrics(object):
    cpu_percent: float
    memory_percent: float
    disk_percent: float

    def __str__(self):
        return json.dumps(json.loads(self.to_json()), indent=2)
