# Create a quick sort algorithm:
#

def quick_sort(array):
    if len(array) < 2:
        return array
    else:
        pivot = array[0]
        less = [i for i in array[1:] if i <= pivot]
        greater = [i for i in array[1:] if i > pivot]
        return quick_sort(less) + [pivot] + quick_sort(greater)

# Use quick sort to sort example array
example = [3, 2, 5, 1, 4]
print(quick_sort(example))
