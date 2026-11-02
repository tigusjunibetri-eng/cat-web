class ItemBank:
    """Manages the item bank data."""

    def __init__(self, df):
        self.df = df
        self.n_items = len(df)

    def get_item_data(self, item_idx):
        return self.df.iloc[item_idx]

    def get_all_items(self):
        return self.df