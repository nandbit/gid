def decode(filepath: str) -> None:
    with open(filepath, "rb") as f:
        # Header
        header = f.read(12)

        dircache: str = _bytes_to_ascii(header[0:4])
        version: int = _bytes_to_int(header[4:8])
        num_index_entries: int = _bytes_to_int(header[8:12])

        print("[header]")
        print(_format_value_line("dircache:", dircache))
        print(f"{'version:':<30} {version}")
        print(f"{'entries:':<30} {num_index_entries}")

        print("")

        # Index entries
        for i in range(num_index_entries):
            print("[entry]")

            metadata: bytes = f.read(40)

            ctime_sec: int = _bytes_to_int(metadata[0:4])
            ctime_ns: int = _bytes_to_int(metadata[4:8])
            mtime_sec: int = _bytes_to_int(metadata[8:12])
            mtime_ns: int = _bytes_to_int(metadata[12:16])
            dev: int = _bytes_to_int(metadata[16:20])
            ino: int = _bytes_to_int(metadata[20:24])
            type_and_permissions: bytes = metadata[24:28]
            mode: str = _parse_mode(type_and_permissions)
            uid: int = _bytes_to_int(metadata[28:32])
            gid: int = _bytes_to_int(metadata[32:36])
            file_size: int = _bytes_to_int(metadata[36:40])

            sha1: bytes = f.read(20)

            flags_bytes: bytes = f.read(2)
            assume_valid, extended, stage, name_len = _parse_flags(flags_bytes)

            skip_worktree = None
            intend_to_add = None

            if (version >= 3) and (extended == 1):
                field = f.read(2)
                skip_worktree = (field >> 14) & 1
                intend_to_add = (field >> 13) & 1

            entry_path_name = None
            c = 1
            if name_len != 0xFFF:
                entry_path_name = f.read(name_len + 1)
                print(f"Name length: {name_len}")
                print(f"Name: {entry_path_name}")
                print("Starting to seek NUL bytes")
                padding_bytes = 8 - (name_len % 8)
                print(f"Reading {padding_bytes} padding bytes")
                _ = f.read(padding_bytes)

                # b = f.peek(1)[:1]
                # _ = f.read(0)
                # while b == b"\x00":
                #     c += 1
                #     print("after name NUL byte")
                #     _ = f.read(1)
                #     b = f.peek(1)[:1]
                #     print(f"next byte: {b}")
                #     if c >= 7:
                #         break
            # else:
            #     print(f"Name length: {entry_path_name}")
            #     print("Starting to seek NUL bytes")
            #     b = f.peek(1)[:1]
            #     while b != b"\x00":
            #         print("NUL byte")
            #         b = f.read(1)
            #         entry_path_name += b
            #         b = f.peek(1)[:1]
            #
            #     b = f.peek(1)
            #     while b == b"\x00" and b is not None:
            #         print("NUL byte")
            #         f.read(1)
            #         b = f.peek(1)[:1]

            print(f"Done reading {c} NUL bytes")

            # if version < 4:
            #     print("Starting to seek NUL bytes after entry end")
            #     b = f.peek(1)[:1]
            #     while b == b"\x00":
            #         print("after entry NUL byte")
            #         f.read(1)
            #         b = f.peek(1)[:1]

            print(_format_value_line("ctime_sec:", ctime_sec))
            print(_format_value_line("ctime_ns:", ctime_ns))
            print(_format_value_line("mtime_sec:", mtime_sec))
            print(_format_value_line("mtime_ns:", mtime_ns))
            print(_format_value_line("dev:", dev))
            print(_format_value_line("ino:", ino))
            print(_format_value_line("mode:", mode))
            print(_format_value_line("uid:", uid))
            print(_format_value_line("gid:", gid))
            print(_format_value_line("size:", file_size))
            print(_format_value_line("sha1:", sha1.hex()))
            print(_format_value_line("assume-valid:", assume_valid))
            print(_format_value_line("extended:", extended))
            print(_format_value_line("stage:", stage))
            print(_format_value_line("length:", name_len))
            print(_format_value_line("skip-worktree:", skip_worktree))
            print(_format_value_line("intend-to-add:", intend_to_add))
            print(_format_value_line("name:", _bytes_to_ascii(entry_path_name)))
            print("")

        # Extensions
        extension_signature: bytes = f.read(4)
        extension_optional: bool = _is_extension_optional(extension_signature)
        extension_size: int = _bytes_to_int(f.read(4))
        extension_data: bytes = f.read(extension_size)

        print("[extension]")
        print(_format_value_line("signature:", extension_signature))
        print(_format_value_line("optional:", str(extension_optional)))
        print(_format_value_line("size:", extension_size))
        print(_format_value_line("data:", str(extension_data)))


def _parse_mode(b: bytes) -> str:
    # Type|---|Perm bits
    # 1000 000 111101101
    # 1 0   0   7  5  5

    # For type:
    # 1000 (regular file), 1010 (symbolic link) and 1110 (gitlink)

    b_int = int.from_bytes(bytes=b, byteorder="big")
    type_h = str(b_int >> 15)
    type_l = str((b_int >> 12) & 0x0007)
    perm_h = str((b_int >> 6) & 0x0007)
    perm_m = str((b_int >> 3) & 0x0007)
    perm_l = str(b_int & 0x0007)

    return type_h + type_l + "0" + perm_h + perm_m + perm_l


def _parse_flags(b: bytes) -> list[str]:
    flags_int = int.from_bytes(bytes=b, byteorder="big")
    assume_valid_flag = str((flags_int & 0x00FF) >> 15)
    extended_flag = str((flags_int >> 14) & 1)
    stage_flag = str((flags_int >> 12) & 3)
    file_name_length = flags_int & 4095

    return [
        assume_valid_flag,
        extended_flag,
        stage_flag,
        file_name_length,
    ]


def _is_extension_optional(signature: bytes) -> bool:
    first_byte = signature[0]
    if first_byte >= 0x41 and first_byte <= 0x5A:
        return True

    return False


def _bits_from_byte(b: bytes, n_bits: int) -> int:
    for i in b:
        for j in range(8):
            yield (i >> j) & 1


def _bytes_to_ascii(b: bytes) -> str:
    return b.decode("ascii")


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
