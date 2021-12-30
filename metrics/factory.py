import pandas as pd

from metrics.activity.cumulative import CumulativeActivity
from metrics.activity.sma import SmaActivity
from metrics.awards.message import MessageAwards
from metrics.awards.sender import SenderAwards
from metrics.metric import Metric
from metrics.reacts.heatmap import ReactHeatmap


def provide_metric(
    name: str,
    messages: pd.DataFrame,
    filter_top: bool = False,
    filter_bottom: bool = False,
    filter_word: str = None,
) -> Metric:
    name = name.lower()
    if name == CumulativeActivity.name:
        return CumulativeActivity(messages, filter_top, filter_bottom)
    if name == SmaActivity.name:
        return SmaActivity(messages, filter_top, filter_bottom)
    if name == MessageAwards.name:
        return MessageAwards(messages)
    if name == SenderAwards.name:
        return SenderAwards(messages, filter_word)
    if name == ReactHeatmap.name:
        return ReactHeatmap(messages)
    raise Exception(f"Unsupported metric name {name}")
