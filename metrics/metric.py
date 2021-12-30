import traceback
from abc import ABC, abstractmethod, abstractproperty
from typing import List, Set

import pandas as pd
from datetime import datetime

from metrics.figure import Figure
from status import Status


class Metric(ABC):
    def __init__(self, messages: pd.DataFrame):
        self.messages = messages

    @abstractproperty
    def name(self):
        pass

    @abstractmethod
    def compute_metric(self) -> List[Figure]:
        pass

    def compute(self) -> Status:
        try:
            print(f"computing {self.name}")
            for figure in self.compute_metric():
                if not figure.saved:
                    figure.save()
            return Status(metric=self.name, success=True)
        except Exception as e:
            return Status(
                metric=self.name,
                success=False,
                message=f"{traceback.format_exc()}\n{str(e)}",
            )

    def get_participants(self) -> Set[str]:
        return set(self.messages["sender"].unique())

    def timestamp_to_date(self, ts: int) -> int:
        return datetime.fromtimestamp(ts / 1000)
