class Ability:
    """Mengelola estimasi kemampuan peserta."""

    def __init__(self, initial_theta=0.0):
        self.theta = initial_theta

    def get_theta(self):
        return self.theta

    def set_theta(self, theta):
        self.theta = theta

    def update(self, theta):
        self.theta = theta