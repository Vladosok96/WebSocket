# Установить бит в 1
def set_bit(number: int, bit_position: int, value: int):
    if value:
        return number | (1 << bit_position)
    else:
        return number & ~(1 << bit_position)


# Прочитать значение бита (0 или 1)
def read_bit(number: int, bit_position: int):
    return (number >> bit_position) & 1


# Циклический сдвиг
def shift(number: int, steps: int, size: int):
    if steps > 0:
        for i in range(steps):
            last_bit = (number & (2 ** (size - 1))) >> (size - 1)
            number = number << 1
            number += last_bit
            number = number & (2 ** size - 1)
    elif steps < 0:
        pass

    return number
