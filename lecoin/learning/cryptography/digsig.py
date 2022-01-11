import nacl.signing as signing
import nacl.encoding as encoding


bobs_private_key = signing.SigningKey.generate()
bobs_public_key = bobs_private_key.verify_key

bobs_public_key_hex = bobs_public_key.encode(encoder=encoding.HexEncoder)
print(bobs_public_key_hex)

signed = bobs_private_key.sign(b"Send $5 to Alice")
print(signed)

verify_key = signing.VerifyKey(bobs_public_key_hex, encoder=encoding.HexEncoder)

verify_key.verify(signed)
print(verify_key.verify(signed))
