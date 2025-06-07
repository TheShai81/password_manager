'''Handles all logic for encryption/decryption and generation/retrieval.'''

from hashlib import sha256

def xor(h1: bytes, h2: bytes, offset: int = 0) -> bytes:
    '''Returns the binary XOR of two bytes objects (hashlib hashes).
    
    ## Args:
    h1: bytes - the first hash
    h2: bytes - the second hash
    offset: int - the bit offset to xor
    '''

    h1 = shift_bits(h1, offset)
    h2 = shift_bits(h2, offset)

    return bytes(a ^ b for a, b in zip(h1, h2))

def hash(s: str) -> bytes:
    '''Finds SHA-256 hash of a string'''
    return sha256(s.encode("utf-8")).digest()

def shift_bits(data: bytes, offset: int) -> bytes:
    '''Shift a bytes object at the bit level'''
    as_int = int.from_bytes(data, 'big')
    shifted = as_int >> offset
    byte_len = max(1, (shifted.bit_length() + 7) // 8)
    return shifted.to_bytes(byte_len, 'big')
