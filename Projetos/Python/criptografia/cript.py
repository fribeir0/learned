from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

mensagem = b"Testando Criptografia"

mensagem_criptografada = public_key.encrypt(

mensagem,
padding.OAEP(

mgf=padding.MGF1(algorithm=hashes.SHA256()),
algorithm=hashes.SHA256(),
label=None

)

)
print("Mensagem criptografada:", mensagem_criptografada)

mensagem_descriptografada = private_key.decrypt(

mensagem_criptografada,
padding.OAEP(
mgf=padding.MGF1(algorithm=hashes.SHA256()),
algorithm=hashes.SHA256(),
label=None
)

)
print("Mensagem descriptografada:", mensagem_descriptografada.decode())