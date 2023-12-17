import binoperations


# Режимы алгоритма DES
ENCRYPTION = 1
DECRYPTION = 2


# Функция генерации 48-битного ключа из 56-битного
def generate_keys(k: int):

    # Расширение до 64 бит
    pieces = []
    for i in range(8):
        piece = k & 0b1111111
        k = k >> 7
        piece = piece << 1
        piece_str = bin(piece)[2:].rjust(7, '0')
        if piece_str.count('1') % 2 == 0:
            piece += 1
        pieces.append(piece)
    k_64 = 0
    for i in range(7, -1, -1):
        k_64 = k_64 << 8
        k_64 += pieces[i]

    # Первоначальная перестановка ключа
    table = [
        57, 49, 41, 33, 25, 17, 9,
        1,  58, 50, 42, 34, 26, 18,
        10, 2,  59, 51, 43, 35, 27,
        19, 11, 3,  60, 52, 44, 36,
        63, 55, 47, 39, 31, 23, 15,
        7,  62, 54, 46, 38, 30, 22,
        14, 6,  61, 53, 45, 37, 29,
        21, 13, 5,  28, 20, 12, 4
    ]
    g = 0
    i = 0
    for place in table:
        place -= 1
        g = binoperations.set_bit(g, i, binoperations.read_bit(k_64, place))
        i += 1

    # Сдвиги ключей
    keys = []
    shifts = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    c = g >> 28
    d = g & 0xFFFFFFF
    for step in shifts:
        c = binoperations.shift(c, step, 28)
        d = binoperations.shift(d, step, 28)
        key = (c << 28) + d
        keys.append(key)

    # Завершающая перестановка ключей
    for i in range(16):
        table = [
            14,  17,  11,  24,  1,   5,
            3,   28,  15,  6,   21,  10,
            23,  19,  12,  4,   26,  8,
            16,  7,   27,  20,  13,  2,
            41,  52,  31,  37,  47,  55,
            30,  40,  51,  45,  33,  48,
            44,  49,  39,  56,  34,  53,
            46,  42,  50,  36,  29,  32
        ]
        key = 0
        j = 0
        for place in table:
            place -= 1
            key = binoperations.set_bit(key, j, binoperations.read_bit(keys[i], place))
            j += 1
        keys[i] = key

    return keys


# Функция Фейстеля
def f(half: int, key: int):

    # Расширение до 48 бит
    table = [
        32, 1,  2,  3,  4,  5,
        4,  5,  6,  7,  8,  9,
        8,  9,  10, 11, 12, 13,
        12, 13, 14, 15, 16, 17,
        16, 17, 18, 19, 20, 21,
        20, 21, 22, 23, 24, 25,
        24, 25, 26, 27, 28, 29,
        28, 29, 30, 31, 32, 1
    ]
    half_48 = 0
    i = 0
    for place in table:
        place -= 1
        half_48 = binoperations.set_bit(half_48, i, binoperations.read_bit(half, place))
        i += 1

    # Сложение по модулю 2 с ключем
    half_48 ^= key

    # Разделение на 8 asS-блоков
    s_blocks = []
    for i in range(8):
        s_blocks.append(half_48 & 0b111111)
        half_48 = half_48 >> 6

    # Таблица преобразований
    table = [
        [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
         [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
         [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
         [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
        [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
         [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
         [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
         [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
        [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
         [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
         [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
         [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
        [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
         [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
         [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
         [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
        [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
         [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
         [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
         [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
        [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
         [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
         [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
         [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
        [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
         [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
         [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
         [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
        [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
         [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
         [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
         [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
    ]

    # Преобразование S-блоков
    for i in range(8):
        a = ((s_blocks[i] >> 5) & 0b10) + (s_blocks[i] & 0b1)
        b = (s_blocks[i] >> 1) & 0b1111
        s_blocks[i] = table[i][a][b]

    # Соединение S-блоков в одно число
    result = 0
    for i in range(8):
        result = result << 4
        result += s_blocks[i]

    # Перестановка P
    permutations_table = [
        16, 7,  20, 21, 29, 12, 28, 17,
        1,  15, 23, 26, 5,  18, 31, 10,
        2,  8,  24, 14, 32, 27, 3,  9,
        19, 13, 30, 6,  22, 11, 4,  25
    ]
    tmp_result = result
    i = 0
    for place in permutations_table:
        place -= 1
        tmp_result = binoperations.set_bit(tmp_result, i, binoperations.read_bit(result, place))
        i += 1
    result = tmp_result

    return result


# Алгоритм шифрования DES для одного блока (ECB)
def DES(block: int, key: int, mode: int):

    # Генерация 48-битного ключа
    keys = generate_keys(key)

    # Начальная перестановка
    permutations_table = [
        58, 50, 42, 34, 26, 18, 10, 2,
        60, 52, 44, 36, 28, 20, 12, 4,
        62, 54, 46, 38, 30, 22, 14, 6,
        64, 56, 48, 40, 32, 24, 16, 8,
        57, 49, 41, 33, 25, 17, 9,  1,
        59, 51, 43, 35, 27, 19, 11, 3,
        61, 53, 45, 37, 29, 21, 13, 5,
        63, 55, 47, 39, 31, 23, 15, 7
    ]
    tmp_block = block
    i = 0
    for place in permutations_table:
        place -= 1
        tmp_block = binoperations.set_bit(tmp_block, i, binoperations.read_bit(block, place))
        i += 1
    block = tmp_block

    # Циклы сетей Фейстеля
    if mode == ENCRYPTION:
        left_half = block >> 32
        right_half = block & 0xFFFFFFFF
        for i in range(16):
            left_half_tmp = left_half
            left_half = right_half
            right_half = left_half_tmp ^ f(right_half, keys[i])
        block = (left_half << 32) + right_half
    elif mode == DECRYPTION:
        left_half = block >> 32
        right_half = block & 0xFFFFFFFF
        for i in range(15, -1, -1):
            right_half_tmp = right_half
            right_half = left_half
            left_half = right_half_tmp ^ f(left_half, keys[i])
        block = (left_half << 32) + right_half

    # Конечная перестановка
    permutations_table = [
        40, 8, 48, 16, 56, 24, 64, 32,
        39, 7, 47, 15, 55, 23, 63, 31,
        38, 6, 46, 14, 54, 22, 62, 30,
        37, 5, 45, 13, 53, 21, 61, 29,
        36, 4, 44, 12, 52, 20, 60, 28,
        35, 3, 43, 11, 51, 19, 59, 27,
        34, 2, 42, 10, 50, 18, 58, 26,
        33, 1, 41, 9,  49, 17, 57, 25
    ]
    tmp_block = block
    i = 0
    for place in permutations_table:
        place -= 1
        tmp_block = binoperations.set_bit(tmp_block, i, binoperations.read_bit(block, place))
        i += 1
    block = tmp_block

    return block
