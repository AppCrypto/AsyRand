from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
groupObj = PairingGroup("MNT159")
p=groupObj.random(G1)
print(f"MNT159 point size:{len(str(p))}")

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
groupObj = PairingGroup("SS512")
p=groupObj.random(G1)
print(f"SS512 point size:{len(str(p))}")



from py_ecc.bls import G2ProofOfPossession as bls_pop
private_key = 1782633894
public_key = bls_pop.SkToPk(private_key)
print("BLS12-381 point size:",len(str(public_key)))

# hydrand on linux
from ed25519 import fe, Point, Scalar
B = Point.B
print("ED25519 point size:",len(str(B)))
