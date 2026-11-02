class ItemSelector:
    """Memilih soal berikutnya berdasarkan kemampuan peserta."""

    def __init__(self, item_bank):
        self.item_bank = item_bank

    def select_item(self, theta, administered_items=None):
        """
        Memilih soal yang paling sesuai dengan kemampuan peserta.

        theta:
            Estimasi kemampuan peserta.

        administered_items:
            Daftar indeks soal yang sudah diberikan.
        """

        if administered_items is None:
            administered_items = []

        best_item_idx = None
        best_difference = float("inf")

        for idx in range(self.item_bank.n_items):

            # Jangan pilih soal yang sudah diberikan
            if idx in administered_items:
                continue

            item = self.item_bank.get_item_data(idx)

            # Parameter tingkat kesulitan soal
            difficulty = item["b"]

            # Cari soal yang tingkat kesulitannya
            # paling dekat dengan kemampuan peserta
            difference = abs(theta - difficulty)

            if difference < best_difference:
                best_difference = difference
                best_item_idx = idx

        return best_item_idx