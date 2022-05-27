from random import choice, sample

from .utilities import get_data


def name(count: int | None = None,
         gender: str | None = None) -> str | list[str]:
    '''
    Returns a random first name or a list of them

    Args:
        count (int, optional): The number of names to be
            generated. Defaults to `None`
        gender (str, optional): Specifies the name of which gender
            will be generated. Defaults to `None`

    Returns:
        str | list[str]: A random first name if `count` is `None` or
            a list of random first names if `count` is not `None`
    '''
    if gender == 'm':
        names = get_data('names', 'male_names')
    elif gender == 'f':
        names = get_data('names', 'female_names')
    else:
        male_names = get_data('names', 'male_names')
        female_names = get_data('names', 'female_names')
        names = male_names + female_names

    if count:
        return sample(names, count)
    else:
        return choice(names)


def surname(count: int | None = None) -> str | list[str]:
    '''
    Returns a random surname or a list of them

    Args:
        count (int, optional): The number of surnames to be
            generated. Defaults to `None`

    Returns:
        str | list[str]: A random surname if `count` is `None` or
            a list of surnames if `count` is not `None`
    '''
    surnames = get_data('names', 'surnames')

    if count:
        return sample(surnames, count)
    else:
        return choice(surnames)


def fullname(count: int | None = None,
             gender: int | None = None) -> str | list[str]:
    '''
    Returns a random fullname or a list of them

    Args:
        count (int, optional): The number of fullnames to be
            generated. Defaults to `None`
        gender (str): Specifies the fullname of which gender
            will be generated. Defaults to `None`

    Returns:
        str | list[str]: A random fullname if `count` is `None` or
            a list of random fullnames if `count` is not `None`
    '''
    if gender == 'm':
        names = get_data('names', 'male_names')
    elif gender == 'f':
        names = get_data('names', 'female_names')
    else:
        male_names = get_data('names', 'male_names')
        female_names = get_data('names', 'female_names')
        names = male_names + female_names

    surnames = get_data('names', 'surnames')

    if count:
        fullnames = []
        random_names = sample(names, count)
        random_surnames = sample(surnames, count)

        for name, surname in zip(random_names, random_surnames):
            fullnames.append(f'{name} {surname}')

        return fullnames
    else:
        return f'{choice(names)} {choice(surnames)}'


if __name__ == '__main__':
    print(name())
    print(surname())
    print(fullname())
