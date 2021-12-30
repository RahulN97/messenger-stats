from dataclasses import dataclass


@dataclass
class Status:
    metric: str
    success: bool
    message: str = ""
