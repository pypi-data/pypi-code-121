def base_convert(s, from_base: int, to_base: int, alphabet="0123456789abcdefghijklmnopqrstuvwxyz") -> str:
    s = str(s)
    n = 0
    p = 1
    for digit in s[::-1]:
        if digit in alphabet:
            n += alphabet.index(digit) * p
            p *= from_base
    if n == 0:
        return '0'
    digits = []
    while n:
        digits.append(alphabet[n % to_base])
        n //= to_base
    return ''.join(digits[::-1])
