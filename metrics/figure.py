from abc import ABC, abstractmethod

import pandas as pd
from matplotlib import figure


class Figure(ABC):
    SAVE_PATH = "./figures/{title}.{ext}"

    def __init__(self, title: str):
        self.title = title

    @abstractmethod
    def save(self):
        pass


class Chart(Figure):
    EXTENSION = "png"
    ZOOM = 2

    def __init__(self, title: str, figure: figure.Figure):
        super().__init__(title)
        self.figure = figure

    def save(self):
        w, h = self.figure.get_size_inches()
        self.figure.set_size_inches(w * self.ZOOM, h * self.ZOOM)
        self.figure.savefig(
            self.SAVE_PATH.format(title=self.title, ext=self.EXTENSION),
            dpi=self.figure.get_dpi() * self.ZOOM,
        )


class Table(Figure):
    EXTENSION = "csv"

    def __init__(self, title: str, table: pd.DataFrame):
        super().__init__(title)
        self.table = table

    def save(self):
        self.table.to_csv(self.SAVE_PATH.format(title=self.title, ext=self.EXTENSION))
