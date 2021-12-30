from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd

from metrics.figure import Figure, Table
from metrics.metric import Metric


@dataclass
class SenderCount:
    date: np.dtype("datetime64[ns]")
    sender: str
    count: int


class SenderAwards(Metric):
    TOP = 10

    name = "sender_awards"

    def __init__(self, messages: pd.DataFrame, filter_word: Optional[str]):
        super().__init__(messages)
        self.filter_word = filter_word

    def compute_metric(self) -> List[Figure]:
        figures = [self._most_chats_per_day(), self._most_mentioned()]
        if self.filter_word:
            figures.append(self._most_filter_word())
        return figures

    def _most_chats_per_day(self) -> Table:
        participants = self.get_participants()
        dfs = []
        for p in participants:
            p_df = self.messages[self.messages.sender == p]
            p_df["date"] = self.messages["timestamp"].apply(self.timestamp_to_date)
            date_df = pd.to_datetime(p_df["date"])
            count_df = date_df.groupby(date_df.dt.floor("d")).size().reset_index(name=p)
            count_df.set_index("date", inplace=True)
            dfs.append(count_df)

        counts = []
        for df in dfs:
            for index, row in df.iterrows():
                name = [c for c in df.columns][0]
                counts.append(SenderCount(date=index, sender=name, count=row[name]))
        counts.sort(key=lambda c: c.count, reverse=True)

        rows = [
            {"Sender": c.sender, "Messages": c.count, "Date": c.date}
            for c in counts[: self.TOP]
        ]
        row_labels = [str(i + 1) for i in range(self.TOP)]
        df = pd.DataFrame(rows, index=row_labels)

        return Table("most_messages_sent_on_a_single_day", table=df)

    def _most_mentioned(self) -> Table:
        participants = self.get_participants()
        counts = {p: 0 for p in participants}
        for row in self.messages.itertuples():
            for p in participants:
                if isinstance(row.content, str) and p in row.content:
                    counts[p] += 1

        mentions = [(k, v) for k, v in counts.items()]
        mentions.sort(key=lambda x: x[1], reverse=True)
        rows = [{"Mentioned": m[0], "Count": m[1]} for m in mentions]
        row_labels = [str(i + 1) for i in range(len(mentions))]
        df = pd.DataFrame(rows, index=row_labels)

        return Table("most_mentioned", table=df)

    def _most_filter_word(self) -> Table:
        counts = {p: 0 for p in self.get_participants()}
        for row in self.messages.itertuples():
            if (
                isinstance(row.content, str)
                and self.filter_word.lower() in row.content.lower()
            ):
                counts[row.sender] += 1

        mentions = [(k, v) for k, v in counts.items() if v]
        mentions.sort(key=lambda x: x[1], reverse=True)
        rows = [{"Chatter": m[0], "Times Messaged": m[1]} for m in mentions]
        row_labels = [str(i + 1) for i in range(len(mentions))]
        df = pd.DataFrame(rows, index=row_labels)

        return Table(f"most_times_{self.filter_word}_messaged", table=df)
