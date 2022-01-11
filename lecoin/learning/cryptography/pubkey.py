from nacl.public import PrivateKey, Box


alices_private_key = PrivateKey.generate()
bobs_private_key = PrivateKey.generate()

alices_public_key = alices_private_key.public_key
bobs_public_key = bobs_private_key.public_key

bobs_box = Box(bobs_private_key, alices_public_key)

encrypted = bobs_box.encrypt(b"I am Satoshi")

alices_box = Box(alices_private_key, bobs_public_key)

plain_text = alices_box.decrypt(encrypted)

print(f"{encrypted}\n{plain_text}")
