def check_predicates (value, predicates):
    for predicate in predicates:
        try:
            if not predicate(value):
                return False
        except:
            return False

    return True

def parse_input (value, name="", type=str, predicates=[]):
    if not check_predicates(value, predicates):
        is_value_ok = False

        while not is_value_ok:
            try:
                value = type(input(f'Enter {name}: '))
            except ValueError:
                value = None
            if check_predicates(value, predicates):
                is_value_ok = True

    return value
