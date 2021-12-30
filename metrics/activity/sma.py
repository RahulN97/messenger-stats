from typing import List

import pandas as pd

from metrics.figure import Chart, Figure
from metrics.metric import Metric


class SmaActivity(Metric):
    WINDOW = 40

    name = "sma_activity"

    def __init__(self, messages: pd.DataFrame, filter_top: bool, filter_bottom: bool):
        super().__init__(messages)
        self.filter_top = filter_top
        self.filter_bottom = filter_bottom

    def compute_metric(self) -> List[Figure]:
        participants = self.get_participants()

        dfs = []
        for p in participants:
            p_df = self.messages[self.messages.sender == p]
            p_df["date"] = self.messages["timestamp"].apply(self.timestamp_to_date)
            date_df = pd.to_datetime(p_df["date"])
            count_df = date_df.groupby(date_df.dt.floor("d")).size().reset_index(name=p)
            count_df[p] = count_df[p].rolling(window=self.WINDOW).mean()
            count_df.set_index("date", inplace=True)
            dfs.append(count_df)

        dfs = self._sort_dfs(dfs)

        charts = [self._plot_sma_all(dfs)]
        mid = int(len(participants) / 2)
        if self.filter_top:
            charts.append(self._plot_sma_top(dfs, mid))
        if self.filter_bottom:
            charts.append(self._plot_sma_bottom(dfs, mid))
        return charts

    def _plot_sma_all(self, dfs: List[pd.DataFrame]) -> Chart:
        ax = dfs[0].plot(
            title=f"Moving Avg of messages sent per day on a {self.WINDOW} day window for all chatters"
        )
        for i in range(1, len(dfs)):
            dfs[i].plot(ax=ax)

        return Chart(title="sma_activity_all", figure=ax.get_figure())

    def _plot_sma_top(self, dfs: List[pd.DataFrame], n: int) -> Chart:
        dfs = self._copy_dfs(dfs[:n])
        ax = dfs[0].plot(
            title=f"Moving Avg of messages sent per day on a {self.WINDOW} day window for top chatters"
        )
        for i in range(1, len(dfs)):
            dfs[i].plot(ax=ax)

        return Chart(title="sma_activity_top", figure=ax.get_figure())

    def _plot_sma_bottom(self, dfs: List[pd.DataFrame], n: int) -> Chart:
        dfs = self._copy_dfs(dfs[n:])
        ax = dfs[0].plot(
            title=f"Moving Avg of messages sent per day on a {self.WINDOW} day window for bottom chatters"
        )
        for i in range(1, len(dfs)):
            dfs[i].plot(ax=ax)

        return Chart(title="sma_activity_bottom", figure=ax.get_figure())

    def _copy_dfs(self, dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
        return [df.copy(deep=True) for df in dfs]

    def _sort_dfs(self, dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
        sender_counts = []
        for df in dfs:
            name = [c for c in df.columns][0]
            sender_counts.append((df[name].sum(), df))
        sender_counts.sort(key=lambda x: x[0], reverse=True)
        return [sc[1] for sc in sender_counts]
