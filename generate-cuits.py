import random
import sys


def get_validation_number(number):
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    aux = 0
    for i in range(10):
        aux += int(number[i]) * base[i]

    aux = 11 - (aux - (int(aux / 11) * 11))

    if aux == 11:
        return 0
    elif aux == 10:
        return 9
    else:
        return aux


def get_amount_to_generate():
    if len(sys.argv[1:]) == 1 and sys.argv[1].isnumeric():
        return int(sys.argv[1])

    return 5


def run():
    for x in range(get_amount_to_generate()):
        prefix = str(random.choice([20, 23, 24, 27]))
        dni = str(random.randint(10000000, 40000000))
        validation_number = str(get_validation_number(prefix + dni))
        print(f"{prefix}{dni}{validation_number}", end=" | ")
        print(f"{prefix}-{dni}-{validation_number}", end=" | ")
        print(f"{prefix} {dni} {validation_number}")


if __name__ == '__main__':
    run()
