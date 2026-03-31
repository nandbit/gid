from gid import decoder


def test_bits_from_byte():
    b = b"\xffxff"

    b_1 = 1
    b_2 = 255
    b_3 = 1
    b_4 = 3
    b_1 = 61440

    decoder._bits_from_byte(
        b,
    )
