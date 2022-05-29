def bin_find(arr, x):
    start = 0
    end = len(arr) - 1

    while start <= end:
        mid = (start + end) // 2
        g = arr[mid]

        if g == x:
            return arr[mid]

        if g < x:
            start = mid + 1
        else:
            end = mid - 1


    return None



print(
    bin_find([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110], 60)
)