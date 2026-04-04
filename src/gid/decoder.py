#                           Structure
# -----------------------------------------------------------------
# Data                                       |   Bytes            |
# -----------------------------------------------------------------
# Header                                     |  12                |
# Entry metadata                             |  62                |
# Entry file name                            |  N                 |
# Mandatory file name terminating NUL byte   |  1                 |
# File name padding NUL bytes                |  (8 - (F % 8)) % 8 |
# Extension signature                        |  4                 |
# Extension size                             |  4                 |
# Extension data                             |  M                 |
# -----------------------------------------------------------------

from gid.utils import (
    bytes_to_ascii,
    bytes_to_int,
    format_value_line,
)


class Header:
    def parse(self, bytes: bytes) -> None:
        self.dircache = bytes_to_ascii(bytes[0:4])
        self.version = bytes_to_int(bytes[4:8])
        self.num_entries = bytes_to_int(bytes[8:12])

    def format(self) -> str:
        return (
            "[header]"
            + "\n"
            + format_value_line("dircache:", self.dircache)
            + "\n"
            + format_value_line("version:", self.version)
            + "\n"
            + format_value_line("entries:", self.num_entries)
            + "\n"
        )


class Entry:
    def parse_metadata(self, metadata: bytes) -> None:
        self.ctime_sec = bytes_to_int(metadata[0:4])
        self.ctime_ns = bytes_to_int(metadata[4:8])
        self.mtime_sec = bytes_to_int(metadata[8:12])
        self.mtime_ns = bytes_to_int(metadata[12:16])
        self.dev = bytes_to_int(metadata[16:20])
        self.ino = bytes_to_int(metadata[20:24])
        self.type_and_permissions = metadata[24:28]
        self.mode = self._parse_mode(metadata[24:28])
        self.uid = bytes_to_int(metadata[28:32])
        self.gid = bytes_to_int(metadata[32:36])
        self.file_size = bytes_to_int(metadata[36:40])
        self.sha1 = metadata[40:60].hex()
        self.flags = bytes_to_int(metadata[60:62])
        self.assume_valid = (self.flags & 0x00FF) >> 15
        self.extended = (self.flags >> 14) & 1
        self.stage = (self.flags >> 12) & 3
        self.name_len = self.flags & 4095
        self.skip_worktree = None
        self.intend_to_add = None

    def parse_field(self, field: bytes) -> None:
        field_int = bytes_to_int(field)
        self.skip_worktree = (field_int >> 14) & 1
        self.intend_to_add = (field_int >> 13) & 1

    def parse_name(self, name: bytes) -> None:
        self.name = bytes_to_ascii(name)

    def consumed_bytes(self) -> int:
        if (self.skip_worktree is not None) and (self.intend_to_add is not None):
            return 62 + len(self.name) + 2
        return 62 + len(self.name)

    def format(self) -> str:
        return (
            "[entry]"
            + "\n"
            + format_value_line("ctime_s:", self.ctime_sec)
            + "\n"
            + format_value_line("ctime_ns:", self.ctime_ns)
            + "\n"
            + format_value_line("mtime_s:", self.mtime_sec)
            + "\n"
            + format_value_line("mtime_ns:", self.mtime_ns)
            + "\n"
            + format_value_line("dev:", self.dev)
            + "\n"
            + format_value_line("ino:", self.ino)
            + "\n"
            + format_value_line("mode:", self.mode)
            + "\n"
            + format_value_line("uid:", self.uid)
            + "\n"
            + format_value_line("gid:", self.gid)
            + "\n"
            + format_value_line("sha1:", self.sha1)
            + "\n"
            + format_value_line("assume-valid:", self.assume_valid)
            + "\n"
            + format_value_line("extended:", self.extended)
            + "\n"
            + format_value_line("stage:", self.stage)
            + "\n"
            + format_value_line("skip-worktree:", self.skip_worktree)
            + "\n"
            + format_value_line("name:", self.name)
            + "\n"
        )

    def _parse_mode(self, b: bytes) -> str:
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


class Extension:
    def __init__(self, bytes: bytes) -> None:
        self.bytes = bytes
        self._parse_signature()
        self._parse_size()

    def parse_data(self, data: bytes) -> None:
        self.data = data

    def format(self) -> str:
        return (
            "[extension]"
            + "\n"
            + format_value_line("signature:", bytes_to_ascii(self.signature))
            + "\n"
            + format_value_line("size:", self.size)
            + "\n"
            + format_value_line("data:", self.data)
        )

    def _parse_signature(self) -> None:
        self.signature: bytes = self.bytes[0:4]
        self.optional: bool = self._is_optional()

    def _parse_size(self) -> None:
        self.size: int = bytes_to_int(self.bytes[4:8])

    def _is_optional(self) -> bool:
        if self.signature[0] >= 0x41 and self.signature[0] <= 0x5A:
            return True

        return False


def decode(filepath: str) -> None:
    with open(filepath, "rb") as f:
        header_bytes = f.read(12)
        header = Header()
        header.parse(header_bytes)

        print(header.format())

        # Index entries
        for i in range(header.num_entries):
            entry = _parse_entry(f, header)

            print(entry.format())

        # Extensions
        extension = Extension(f.read(8))
        extension_data = f.read(extension.size)
        extension.parse_data(extension_data)

        print(extension.format())


def _parse_entry(f, header: Header) -> Entry:
    metadata: bytes = f.read(62)
    entry = Entry()
    entry.parse_metadata(metadata)

    if (header.version >= 3) and (entry.extended == 1):
        entry.parse_field(f.read(2))

    if entry.name_len != 0x0FFF:
        entry.parse_name(f.read(entry.name_len))
    else:
        # Read until a NUL byte (0x00)
        entry_name: bytes = ""
        b = f.peek(1)[:1]  # peek can return more than 1 byte
        while b != b"\x00":
            entry_name += f.read(1)
            b = f.peek(1)[:1]

        entry.parse_name(entry_name)

    # Consume mandatory 1 NUL byte
    _ = f.read(1)

    # Consume padding bytes
    consumed_bytes = entry.consumed_bytes() + 1
    padding_bytes = (8 - (consumed_bytes % 8)) % 8
    _ = f.read(padding_bytes)

    return entry
