from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd
import seaborn as sns

from metrics.figure import Chart, Figure, Table
from metrics.metric import Metric


class ReactHeatmap(Metric):
    name = "reacts"

    def __init__(self, messages: pd.DataFrame):
        super().__init__(messages)

    def compute_metric(self) -> List[Figure]:
        heatmap = defaultdict(lambda: defaultdict(int))
        for row in self.messages.itertuples():
            if not isinstance(row.reactors, list):
                continue
            for reactor in row.reactors:
                heatmap[reactor][row.sender] += 1

        receivers = list(heatmap.keys())
        df = pd.DataFrame(index=receivers, columns=receivers)
        for reactor, data in heatmap.items():
            for sender, count in data.items():
                if reactor not in receivers or sender not in receivers:
                    continue
                df.at[reactor, sender] = count
        df = df.fillna(0)

        return [
            self._generate_raw_heatmap(df.copy(deep=True)),
            self._generate_pct_heatmap(df.copy(deep=True)),
            self._most_reacts_sent(df.copy(deep=True)),
            self._most_reacts_received(df.copy(deep=True)),
            self._most_reacts_received_per_message(df.copy(deep=True)),
        ]

    def _generate_raw_heatmap(self, df: pd.DataFrame) -> Chart:
        s = sns.heatmap(df, annot=True, fmt="g", annot_kws={"size": 18})
        s.set(title="Raw React Heatmap", xlabel="Sender", ylabel="Reactor")
        s.set_xticklabels(labels=s.get_xticklabels(), rotation=60, ha="right")
        s.figure.tight_layout()

        chart = Chart(title="raw_reacts_heatmap", figure=s.get_figure())
        chart.save()
        return chart

    def _generate_pct_heatmap(self, df: pd.DataFrame) -> Chart:
        counts = self._count_messages_sent(df)
        for col in df.columns:
            df[col] = round(100 * (df[col] / counts[col]), 2)

        s = sns.heatmap(df, annot=True, fmt="g", annot_kws={"size": 18})
        s.set(
            title="Percent of Messages Reacted Heatmap",
            xlabel="Sender",
            ylabel="Reactor",
        )
        s.set_xticklabels(labels=s.get_xticklabels(), rotation=60, ha="right")
        s.figure.tight_layout()

        chart = Chart(title="pct_reacts_heatmap", figure=s.get_figure())
        chart.save()
        return chart

    def _most_reacts_sent(self, df: pd.DataFrame) -> Table:
        df["sent"] = df.sum(axis=1)
        rows = [
            {"Reactor": index, "Reacts Sent": row["sent"]}
            for index, row in df.iterrows()
        ]
        rows.sort(key=lambda d: d["Reacts Sent"], reverse=True)

        row_labels = [str(i + 1) for i in range(len(rows))]
        table = pd.DataFrame(rows, index=row_labels)

        return Table(title="most_reacts_sent", table=table)

    def _most_reacts_received_per_message(self, df: pd.DataFrame) -> Table:
        counts = self._count_messages_sent(df)
        received = self._sorted_reacts_received(df)
        rpm = sorted(
            [(r[0], r[1] / counts[r[0]]) for r in received],
            key=lambda r: r[1],
            reverse=True,
        )
        rows = [{"Chatter": r[0], "Reacts Received per Message": r[1]} for r in rpm]
        row_labels = [str(i + 1) for i in range(len(received))]
        table = pd.DataFrame(rows, index=row_labels)

        return Table(title="most_reacts_received_per_message", table=table)

    def _most_reacts_received(self, df: pd.DataFrame) -> Table:
        received = self._sorted_reacts_received(df)
        rows = [{"Chatter": r[0], "Reacts Received": r[1]} for r in received]
        row_labels = [str(i + 1) for i in range(len(received))]
        table = pd.DataFrame(rows, index=row_labels)

        return Table(title="most_reacts_received", table=table)

    def _count_messages_sent(self, df: pd.DataFrame) -> Dict[str, int]:
        counts = {c: 0 for c in df.columns}
        for row in self.messages.itertuples():
            if row.sender in counts:
                counts[row.sender] += 1
        return counts

    def _sorted_reacts_received(self, df: pd.DataFrame) -> List[Tuple[str, int]]:
        received = {c: df[c].sum() for c in df.columns}
        return sorted(received.items(), key=lambda x: x[1], reverse=True)
