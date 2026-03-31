def main():
    index_filepath = "./tests/index"

    with open(index_filepath, "rb") as f:
        # Header
        header = f.read(12)
        dircache = header[0:4]
        version = header[4:8]
        num_index_entries = header[8:12]

        # Extensions
        extension_signature = f.read(4)
        extension_optional = _is_extension_optional(extension_signature)
        extension_size = f.read(4)
        extension_data = f.read(_bytes_to_int(extension_size))

        print("[header]")
        print(_format_value_line("dircache", dircache))
        print(f"{'version:':<30} {_bytes_to_int(version)}")
        print(f"{'entries:':<30} {_bytes_to_int(num_index_entries)}")

        print("")

        print("[extension]")
        print(_format_value_line("signature:", str(extension_signature)))
        print(_format_value_line("optional:", str(extension_optional)))
        print(f"size: {_bytes_to_int(extension_size)}")
        print(f"data: {str(extension_data)}")


def _is_extension_optional(signature: bytes) -> bool:
    first_byte = signature[0]
    if first_byte >= 0x41 and first_byte <= 0x5A:
        return True

    return False


def _bytes_to_int(b: bytes) -> int:
    return int.from_bytes(bytes=b, byteorder="big")


def _bytes_to_string(b: bytes) -> str:
    return str(b)


def _format_header_line(header: str, spacing: int = 20):
    return f"{header:^{spacing}}"


def _format_value_line(
    label: str,
    value: str,
    spacing: int = 30,
) -> None:
    return f"{label:<{spacing}} {value}"


if __name__ == "__main__":
    main()
