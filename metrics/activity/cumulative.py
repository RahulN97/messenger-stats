from typing import List

import pandas as pd

from metrics.figure import Chart, Figure
from metrics.metric import Metric


class CumulativeActivity(Metric):
    name = "cumulative_activity"

    def __init__(self, messages: pd.DataFrame, filter_top: bool, filter_bottom: bool):
        super().__init__(messages)
        self.filter_top = filter_top
        self.filter_bottom = filter_bottom

    def compute_metric(self) -> List[Figure]:
        participants = self.get_participants()
        counter = {p: 0 for p in participants}

        rows = []
        for row in self.messages.itertuples():
            counter[row.sender] += 1
            entry = counter.copy()
            entry["date"] = self.timestamp_to_date(row.timestamp)
            rows.append(entry)

        df = pd.DataFrame(rows)

        senders = self._get_sorted_senders(df)
        charts = [self._plot_cumulative_all(df, senders)]
        mid = int(len(participants) / 2)
        if self.filter_top:
            charts.append(self._plot_cumulative_top(df, senders, mid))
        if self.filter_bottom:
            charts.append(self._plot_cumulative_bottom(df, senders, mid))
        return charts

    def _plot_cumulative_all(
        self,
        df: pd.DataFrame,
        senders: List[str],
    ) -> Chart:
        plt = df.plot(
            x="date",
            y=senders,
            title="Cumulative sum of messages sent by all chatters",
        )
        return Chart(title="cumulative_activity_all", figure=plt.get_figure())

    def _plot_cumulative_top(
        self, df: pd.DataFrame, senders: List[str], n: int
    ) -> Chart:
        plt = df.plot(
            x="date",
            y=senders[:n],
            title=f"Cumulative sum of messages sent over time by top {n} chatters",
        )
        return Chart(title="cumulative_activity_top", figure=plt.get_figure())

    def _plot_cumulative_bottom(
        self, df: pd.DataFrame, senders: List[str], n: int
    ) -> Chart:
        plt = df.plot(
            x="date",
            y=senders[n:],
            title=f"Cumulative sum of messages sent over time by bottom {n} chatters",
        )
        return Chart(title="cumulative_activity_bottom", figure=plt.get_figure())

    def _get_sorted_senders(self, df: pd.DataFrame) -> List[str]:
        sender_counts = [(df[c].iloc[-1], c) for c in df.columns if c != "date"]
        sender_counts.sort(key=lambda x: x[0], reverse=True)
        return [sc[1] for sc in sender_counts]
