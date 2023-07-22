import pvss
from ed25519 import KeyPair
from time import time
import math


keypairs = [KeyPair.random() for node_id in range(256)]

for n in [32 * x for x in range(1, 5)]:
    t = math.ceil(n / 3)
    print(f"benchmark pvss performance for n={n}, t={t}: ", end="")
    public_keys = [k.public_key for k in keypairs][:n - 1]

    tstart = time()
    results = [pvss.share_random_secret(public_keys, t) for _ in range(10)]
    print(f"shares length:{len(str(results))/10/1024.}kB")
    tend = time()
    print((tend - tstart) / 100)
