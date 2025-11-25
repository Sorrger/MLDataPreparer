from PySide6.QtCore import QAbstractTableModel, Qt
import pandas as pd


class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self.df = df.reset_index() if not df.index.name is None else df.copy()


    def rowCount(self, parent=None):
        return len(self.df.index)


    def columnCount(self, parent=None):
        return len(self.df.columns)


    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self.df.iat[index.row(), index.column()])
        return None


    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])
            else:
                return str(self.df.index[section])