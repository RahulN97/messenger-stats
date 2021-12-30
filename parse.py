import json
import os
from argparse import ArgumentParser
from typing import List

import pandas as pd
import seaborn as sns

from metrics.factory import provide_metric
from status import Status


METRICS = [
    "cumulative_activity",
    "sma_activity",
    "message_awards",
    "sender_awards",
    "react_heatmap",
]


def construct_argparser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "--chat",
        required=True,
        type=str,
        help="chat name or string that chat name starts with",
    )
    parser.add_argument(
        "--metrics",
        nargs="*",
        choices=METRICS,
        help=f"metrics to compute",
    )
    parser.add_argument(
        "--filter-top",
        action="store_true",
        help="create separate figures for top half of chatters",
    )
    parser.add_argument(
        "--filter-bottom",
        action="store_true",
        help="create separate figures for bottom half of chatters",
    )
    parser.add_argument(
        "--filter-word",
        type=str,
        help="track how many times a specific word was said in chat",
    )
    return parser


def generate_df(path: str) -> pd.DataFrame:
    print(f"parsing {path}")
    with open(path, "r") as f:
        meta = json.load(f)

    rows = []
    for msg in meta["messages"]:
        row = {"sender": msg["sender_name"], "timestamp": msg["timestamp_ms"]}
        if "content" in msg:
            row["content"] = msg["content"]
        if "photos" in msg:
            row["photos"] = msg["photos"]
        if "reactions" in msg:
            row["reactors"] = [r["actor"] for r in msg["reactions"]]
        rows.append(row)

    return pd.DataFrame(rows)


def parse_messages(chat: str) -> pd.DataFrame:
    candidates = [c for c in os.listdir("./messages/inbox/") if c.startswith(chat)]
    if not len(candidates):
        raise Exception(f"No chat starting with {chat} found in inbox")
    if len(candidates) > 1:
        raise Exception("Input amore unique chat name than")

    path = f"./messages/inbox/{candidates[0]}/"
    files = [path + f for f in os.listdir(path) if f.startswith("message")]

    dfs = [generate_df(f) for f in files]
    merged = pd.concat(dfs, ignore_index=True, sort=False)
    return merged.sort_values("timestamp")


def output_status(statuses: List[Status]):
    for s in statuses:
        if not s.success:
            print(f"Metric '{s.metric}' failed: {s.message}")
        else:
            print(f"Metric '{s.metric}' succeeded")


def setup():
    pd.options.mode.chained_assignment = None
    sns.set()
    if not os.path.exists("./figures"):
        os.makedirs("./figures")


def main():
    setup()
    parser = construct_argparser()
    args = parser.parse_args()

    df = parse_messages(args.chat.lower())
    names = args.metrics or METRICS
    metrics = [
        provide_metric(
            name=n,
            messages=df.copy(deep=True),
            filter_top=args.filter_top,
            filter_bottom=args.filter_bottom,
            filter_word=args.filter_word,
        )
        for n in names
    ]

    statuses = [m.compute() for m in metrics]
    output_status(statuses)


main()
