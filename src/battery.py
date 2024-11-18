
class Battery:
    def __init__(self, capacity=100):
        """
        Inicializa a bateria com uma capacidade (em %), inicialmente cheia.
        """
        self.capacity = capacity  # Capacidade total da bateria (100%)
        self.current_charge = capacity  # Carga atual, começando com 100%
        self.max_autonomy_seconds = 1800  # Autonomia máxima do drone em segundos (30 minutos)

    def consume_charge(self, time, mode="normal"):
        """
        Consome a carga da bateria com base no tempo (em segundos) e no modo de voo.
        Modo 'normal' consome menos energia do que o modo 'esportivo'.
        """
        if mode == "normal":
            consumption_rate = 0.03  # Taxa de consumo para o modo normal (ajuste conforme necessário)
        else:  # modo 'esportivo'
            consumption_rate = 0.05  # Taxa de consumo mais alta

        consumed = time * consumption_rate
        self.current_charge -= consumed

        if self.current_charge < 0:
            self.current_charge = 0  # Garantir que não fique negativo

    def recharge(self):
        """
        Recarga a bateria completamente.
        """
        self.current_charge = self.capacity

    def is_empty(self):
        """
        Verifica se a bateria está vazia.
        """
        return self.current_charge <= 0

    def __str__(self):
        """
        Representação textual da carga atual da bateria.
        """
        return f"Battery(charge={self.current_charge}%)"
