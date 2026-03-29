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
        extension_size = f.read(4)
        extension_data = f.read(_bytes_to_int(extension_size))

        print("<--- Header --->")
        print(f"Dircache label: {str(dircache)}")
        print(f"Version: {_bytes_to_int(version)}")
        print(f"Number of entries: {_bytes_to_int(num_index_entries)}")

        print("<--- Extensions --->")
        print(f"Extension signature: {_bytes_to_int(extension_signature)}")
        print(f"Extension size: {_bytes_to_int(extension_size)}")
        print(f"Extension data: {str(extension_data)}")


def _bytes_to_int(b) -> int:
    return int.from_bytes(bytes=b, byteorder="big")


if __name__ == "__main__":
    main()
