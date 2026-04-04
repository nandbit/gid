def bytes_to_ascii(b: bytes) -> str:
    return b.decode("ascii")


def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(bytes=b, byteorder="big")


def format_value_line(
    label: str,
    value: str,
    spacing: int = 30,
) -> None:
    return f"{label:<{spacing}} {value}"
