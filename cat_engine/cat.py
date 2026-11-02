from .ability import Ability
from .item_selection import ItemSelector
from .estimator import AbilityEstimator


class CAT:
    """Mesin utama Computerized Adaptive Testing."""

    def __init__(self, item_bank, max_items=20):
        self.item_bank = item_bank
        self.max_items = max_items

        # Kemampuan awal peserta
        self.ability = Ability(initial_theta=0.0)

        # Pemilih soal
        self.selector = ItemSelector(item_bank)

        # Estimator kemampuan
        self.estimator = AbilityEstimator(initial_theta=0.0)

        # Daftar soal yang sudah diberikan
        self.administered_items = []

        # Riwayat jawaban peserta
        self.responses = []

        # Status CAT
        self.finished = False

    def get_next_item(self):
        """Mengambil soal berikutnya."""

        # Jika jumlah soal sudah mencapai batas
        if len(self.administered_items) >= self.max_items:
            self.finished = True
            return None

        theta = self.ability.get_theta()

        item_idx = self.selector.select_item(
            theta,
            self.administered_items
        )

        if item_idx is None:
            self.finished = True
            return None

        # Tandai soal sebagai sudah diberikan
        self.administered_items.append(item_idx)

        # Ambil data soal
        item = self.item_bank.get_item_data(item_idx)

        return item

    def submit_answer(self, item_idx, correct):
        """Memproses jawaban peserta."""

        item = self.item_bank.get_item_data(item_idx)

        difficulty = item["b"]

        # Ambil kemampuan saat ini
        theta = self.ability.get_theta()

        # Update kemampuan
        new_theta = self.estimator.update(
            theta,
            difficulty,
            correct
        )

        # Simpan kemampuan terbaru
        self.ability.set_theta(new_theta)

        # Simpan riwayat jawaban
        self.responses.append({
            "item_idx": item_idx,
            "correct": correct,
            "theta": new_theta
        })

        # Cek apakah CAT sudah selesai
        if len(self.administered_items) >= self.max_items:
            self.finished = True

        return new_theta

    def get_theta(self):
        """Mengambil kemampuan peserta saat ini."""

        return self.ability.get_theta()

    def get_progress(self):
        """Mengambil progress pengerjaan."""

        return {
            "answered": len(self.responses),
            "total": self.max_items,
            "finished": self.finished
        }

    def is_finished(self):
        """Mengecek apakah CAT sudah selesai."""

        return self.finished

    def get_result(self):
        """Mengambil hasil akhir CAT."""

        return {
            "theta": self.get_theta(),
            "answered": len(self.responses),
            "total": self.max_items,
            "responses": self.responses
        }