import math


class AbilityEstimator:
    """Mengestimasi kemampuan peserta berdasarkan respons soal."""

    def __init__(self, initial_theta=0.0):
        self.theta = initial_theta

    def probability_correct(self, theta, difficulty):
        """
        Menghitung probabilitas peserta menjawab benar.

        Menggunakan model logistik sederhana (Rasch/1PL).
        """

        try:
            probability = 1 / (1 + math.exp(-(theta - difficulty)))
        except OverflowError:
            probability = 0.0 if theta < difficulty else 1.0

        return probability

    def update(self, theta, difficulty, correct):
        """
        Memperbarui estimasi kemampuan setelah satu jawaban.

        correct:
            True  = jawaban benar
            False = jawaban salah
        """

        probability = self.probability_correct(theta, difficulty)

        # Learning rate
        learning_rate = 0.5

        if correct:
            theta = theta + learning_rate * (1 - probability)
        else:
            theta = theta - learning_rate * probability

        # Batasi theta agar tetap stabil
        theta = max(-4.0, min(4.0, theta))

        self.theta = theta

        return theta

    def get_theta(self):
        """Mengambil estimasi kemampuan terakhir."""
        return self.theta