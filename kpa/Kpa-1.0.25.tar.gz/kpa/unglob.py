#!/usr/bin/env python3

from string import printable as ascii_printable

def _collapse_runs(nums):
    nums = sorted(nums)
    ret = []
    while nums:
        start = n = nums[0]
        nums = nums[1:]
        while nums and n+1 == nums[0]:
            n = nums[0]
            nums = nums[1:]
        if start == n: ret.append(n)
        else: ret.append((start,n))
    return ret
assert _collapse_runs([3,4,5,9,10,11,14]) == [(3,5),(9,11),14]

def _fmt_group(chars):
    if len(chars) == 0: raise
    if len(chars) == 1: return chars[0]
    if any(char not in ascii_printable for char in chars): raise
    digits, uppers, lowers, etcs = [], [], [], []
    for char in chars:
        if   char.isdigit(): digits.append(char)
        elif char.isupper(): uppers.append(char)
        elif char.islower(): lowers.append(char)
        else: etcs.append(char)
    ret = ''.join('{x[0]}-{x[1]}'.format(x=x) if isinstance(x,tuple) else str(x) for x in _collapse_runs(map(int,digits)))
    ret += ''.join('{}-{}'.format(chr(x[0]), chr(x[1])) if isinstance(x,tuple) else chr(x) for x in _collapse_runs(map(ord,lowers)))
    ret += ''.join('{}-{}'.format(chr(x[0]), chr(x[1])) if isinstance(x,tuple) else chr(x) for x in _collapse_runs(map(ord,uppers)))
    ret += ''.join(sorted(etcs))
    return '[' + ret +']'

def get_globs(data):
    data = list(set(data))
    lens = {}
    for s in data: lens.setdefault(len(s), []).append(s)
    for length,strings in sorted(lens.items()):

        things = [list(s) for s in strings]
        for i in reversed(range(length)):
            things = [(tuple(thing[:i]), thing[i], tuple(thing[i+1:])) for thing in things]
            groups = {}
            for prefix, char, suffix in things:
                groups.setdefault((prefix,suffix), []).append(char)
            things = [list(prefix) + [tuple(sorted(chars))] + list(suffix) for (prefix,suffix),chars in groups.items()]

        for thing in sorted(things):
            yield ''.join(_fmt_group(g) for g in thing)


if __name__ == '__main__':

    # TODO: make expandglob(), and test that for arbitrary lists of strings, expandglob(unglob(strings)) == strings
    # TODO: run tests with pytest

    datasets = [
            ['{code:03}'.format(code=code) for code in range(0,100+1)],

            ['{code}'.format(code=code) for code in range(0,100+1)],

            (
                '310 311 312 313 314 315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 333 334 335 336 337 338 339 340 341 342 343 344 345 346 347 348 349 350 351 352 353 354 355 356 357 358 359 360 361 362 363 364 365 366 367 368 369 370 371 372 373 374 375 376 377 378 379 380 381 382 383 384 385 386'.split() +
                '308/200 309/200 310/200 311/200 312/200 313/200 314/200 315/200 316/200 317/200 318/200 319/200 320/200 321/200 322/200 323/200 324/200 325/200 326/200 327/200 328/200 329/200 330/200 331/200 332/200 333/200 334/200 335/200 336/200 337/200 338/200 339/200 340/200 341/200 342/200 343/200 344/200 345/200 346/200 347/200 348/200 349/200 350/200 351/200 352/200 353/200 354/200 355/200 356/200 357/200 358/200 359/200 360/200 361/200 362/200 363/200 364/200 365/200 366/200 367/200 368/200 369/200 370/200 371/200 372/200 373/200 374/200 375/200 376/200 377/200 378/200 379/200 380/200 381/200 382/200 383/200 384/200 385/200 386/200 387/200 388/200 389/200'.split()
            )
    ]
    for data in datasets:
        for glob in get_globs(data):
            print(glob)
        print()
