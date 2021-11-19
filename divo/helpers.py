from binascii import unhexlify


def clean_unhexlify(val: str):
    val = val.strip().replace(" ", "").replace("\n", "")
    return unhexlify(val)


def chunks(s: str, n: int):
    return [s[i:i+n] for i in range(0, len(s), n)]
