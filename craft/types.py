from dataclasses import dataclass


@dataclass
class ProcessedFile:
    path: str
    content: str
