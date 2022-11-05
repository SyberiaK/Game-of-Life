def starts_and_endswith(main_str, check_str):
    return main_str.startswith(check_str) and main_str.endswith(check_str)


def is_float(elem: str) -> bool:
    try:
        float(elem)
        return True
    except ValueError:
        return False


def is_int(elem: str) -> bool:
    try:
        int(elem)
        return int(elem) % 1 == 0
    except ValueError:
        return False


def is_bytes(elem: str) -> bool:
    return elem[0] == 'b' and (starts_and_endswith(elem[1:], "'") or starts_and_endswith(elem[1:], '"'))


def is_bool(elem: str) -> bool:
    return elem in ('True', 'False')


def str_to_bool(elem: str) -> bool:
    if elem.lower() in ['y', 'yes', 't', 'true', 'on', '1']:
        return True
    elif elem.lower() in ['n', 'no', 'f', 'false', 'off', '0']:
        return False
    else:
        raise ValueError(f'invalid string for boolean conversion: {elem}')