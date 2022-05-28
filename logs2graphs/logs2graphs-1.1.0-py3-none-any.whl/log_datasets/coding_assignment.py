def inc_or_dec(arr):
    if len(arr) == 2:
        return arr[0] != arr[1]
    else:
        larger = True
        if arr[0] < arr[1]:
            larger = False
        elif arr[0] == arr[1]:
            return False

        for i in range(1, len(arr)-1):
            if larger:
                if arr[i]<arr[i+1]:
                    return False
            else:
                if arr[i]>arr[i+1]:
                    return False
        return True


def solution(arr):
    counter = 0  # [0,1,2,3,4]
    for i in range(len(arr) - 1):
        for j in range(i + 2, len(arr) + 1):
            sub_arr = arr[i:j]
            if inc_or_dec(sub_arr):
                counter += 1
            print(i, j, sub_arr)
    return counter


print(solution([9, 8, 7, 6, 5]))
