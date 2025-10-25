import hashlib
import math

class Sketch:
    def __init__(self, m=64):
        # m = nombre de registres, plus grand → plus précis
        self.m = m
        self.registers = [0] * m

    def _hash(self, value):
        """Retourne un hash 128 bits sous forme d'entier."""
        h = hashlib.md5(str(value).encode()).hexdigest()
        return int(h, 16)
    
    def _rho(self, x):
        """Nombre de zéros consécutifs à droite (avant le premier 1)."""
        r = 1
        while x & 1 == 0 and r < 128:
            x >>= 1
            r += 1
        return r
    def add(self, value):
        h = self._hash(value)
        # index du registre : selon les log2(m) premiers bits
        i = h % self.m
        # on décale pour “oublier” les bits utilisés pour le registre
        w = h >> int(math.log2(self.m))
        # on compte les zéros à droite
        r = self._rho(w)
        # mise à jour du registre (max des zéros vus)
        self.registers[i] = max(self.registers[i], r)
    def merge(self, other):
        assert self.m == other.m
        for i in range(self.m):
            self.registers[i] = max(self.registers[i], other.registers[i])
    def count(self):
     Z = sum(2.0 ** (-r) for r in self.registers)
     alpha = 0.7213 / (1 + 1.079 / self.m)
     E = alpha * self.m * self.m / Z
     return E
