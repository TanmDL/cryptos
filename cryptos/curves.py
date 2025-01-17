"""
Store of curves and generators
"""

from dataclasses import dataclass

# -----------------------------------------------------------------------------
# Related math utilities

def extended_euclidean_algorithm(a, b):
    """
    Returns (gcd, x, y) s.t. a * x + b * y == gcd
    This function implements the extended Euclidean
    algorithm and runs in O(log b) in the worst case,
    taken from Wikipedia.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t

def inv(n, p):
    """ returns modular multiplicate inverse m s.t. (n * m) % p == 1 """
    gcd, x, y = extended_euclidean_algorithm(n, p)
    return x % p

# -----------------------------------------------------------------------------
# Core data structures to represent curves and generators

@dataclass
class Curve:
    """
    Elliptic Curve over the field of integers modulo a prime.
    Points on the curve satisfy y^2 = x^3 + a*x + b (mod p).
    """
    p: int
    a: int
    b: int

@dataclass
class Point:
    """ An integer point (x,y) on a Curve """
    curve: Curve
    x: int
    y: int

    def __add__(self, other):
        # handle special case of P + 0 = 0 + P = 0
        if self == INF:
            return other
        if other == INF:
            return self
        # handle special case of P + (-P) = 0
        if self.x == other.x and self.y != other.y:
            return INF
        # compute the "slope"
        if self.x == other.x: # (self.y = other.y is guaranteed too per above check)
            m = (3 * self.x**2 + self.curve.a) * inv(2 * self.y, self.curve.p)
        else:
            m = (self.y - other.y) * inv(self.x - other.x, self.curve.p)
        # compute the new point
        rx = (m**2 - self.x - other.x) % self.curve.p
        ry = (-(m*(rx - self.x) + self.y)) % self.curve.p
        return Point(self.curve, rx, ry)

    def __rmul__(self, k):
        assert isinstance(k, int) and k >= 0
        result = INF
        append = self
        while k:
            if k&1 == 1:
                result = result + append
            append = append + append
            k >>= 1
        return result

@dataclass
class Generator:
    """
    A generator over a curve: an initial point and the (pre-computed) order
    """
    G: Point     # a generator point on the curve
    n: int       # the order of the generating point, so 0*G = n*G = INF

INF = Point(None, None, None)

# -----------------------------------------------------------------------------
# A library of curves (currently just Bitcoin's secp256k1)

def bitcoin_gen():
    # Return the elliptic curve used in Bitcoin and the generator point
    # secp256k1, http://www.oid-info.com/get/1.3.132.0.10
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    a = 0x0000000000000000000000000000000000000000000000000000000000000000
    b = 0x0000000000000000000000000000000000000000000000000000000000000007
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    curve = Curve(p, a, b)
    G = Point(curve, Gx, Gy)
    gen = Generator(G, n)
    return gen
