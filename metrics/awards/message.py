from dataclasses import dataclass, field
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from metrics.figure import Figure, Table
from metrics.metric import Metric


@dataclass
class MessageCount:
    message: str = ""
    total: int = 0
    counts: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ReactedMessage:
    message: str
    sender: str
    reacts: int


class MessageAwards(Metric):
    TOP_COMMON = 100
    TOP_REACTED = 30
    BLACKLIST = {
        "the call",
        "started a call",
        "this poll",
        "the video chat",
        "you sent an attachment",
    }

    name = "message_awards"

    def __init__(self, messages: pd.DataFrame):
        super().__init__(messages)

    def compute_metric(self) -> List[Figure]:
        return [self._most_common_messages(), self._most_reacted_messages()]

    def _most_common_messages(self) -> Table:
        message_counts = self._generate_message_counts()

        unique_senders = {
            sender for message in message_counts for sender in message.counts.keys()
        }
        senders = list(unique_senders)

        rows = []
        for message in message_counts:
            row = {"Message": message.message, "Total Count": message.total}
            for s in senders:
                row[s] = message.counts.get(s, 0)
            rows.append(row)

        row_labels = [str(i + 1) for i in range(self.TOP_COMMON)]
        df = pd.DataFrame(rows, index=row_labels)
        df = self._strip_infrequent_chatters(df)

        return Table(title="most_common_messages", table=df)

    def _most_reacted_messages(self) -> Table:
        rows = [
            {
                "Message": message.message,
                "Reacts": message.reacts,
                "Sender": message.sender,
            }
            for message in self._generate_reacted_messages()
        ]

        row_labels = [str(i + 1) for i in range(self.TOP_REACTED)]
        df = pd.DataFrame(rows, index=row_labels)

        return Table(title="most_reacted_messages", table=df)

    def _generate_message_counts(self) -> List[MessageCount]:
        counts = {}

        for row in self.messages.itertuples():
            if not isinstance(row.content, str):
                continue

            msg = row.content.lower()
            if any(phrase in msg for phrase in self.BLACKLIST):
                continue

            if msg not in counts:
                counts[msg] = MessageCount()
            mc = counts[msg]
            mc.message = row.content
            mc.total += 1
            if row.sender not in mc.counts:
                mc.counts[row.sender] = 0
            mc.counts[row.sender] += 1

        message_counts = sorted(counts.values(), key=lambda c: c.total, reverse=True)
        return message_counts[: min(len(message_counts), self.TOP_COMMON)]

    def _generate_reacted_messages(self) -> List[ReactedMessage]:
        reacted_messages = [
            ReactedMessage(row.content, row.sender, len(row.reactors))
            for row in self.messages.itertuples()
            if isinstance(row.reactors, list)
            and isinstance(row.content, str)
            and all(phrase not in row.content.lower() for phrase in self.BLACKLIST)
        ]
        reacted_messages.sort(key=lambda m: m.reacts, reverse=True)
        return reacted_messages[: min(len(reacted_messages), self.TOP_REACTED)]

    def _strip_infrequent_chatters(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if df[col].dtype == int and df[col].sum() < 10:
                df = df.drop(labels=col, axis=1)
        return df
