# Radix Sort უარყოფითი რიცხვებისთვის

def counting_sort(arr, exp):
    # ვალაგებთ ერთი ციფრის მიხედვით (exp = 1, 10, 100, ...)
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    # ვითვლით თითო ციფრს
    for num in arr:
        digit = (num // exp) % 10
        count[digit] += 1

    # prefix sum - სად დაიწყოს თითო ციფრი output-ში
    for i in range(1, 10):
        count[i] = count[i] + count[i - 1]

    # ვწერთ output-ში (ბოლოდან რომ stable იყოს)
    for i in range(n - 1, -1, -1):
        digit = (arr[i] // exp) % 10
        count[digit] = count[digit] - 1
        output[count[digit]] = arr[i]

    return output


def lsd_radix(arr):
    # ჩვეულებრივი LSD radix sort (მხოლოდ დადებითი რიცხვებისთვის)
    if len(arr) == 0:
        return arr

    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = counting_sort(arr, exp)
        exp = exp * 10

    return arr


def radix_sort(arr):
    # ვყოფთ უარყოფითებად და დადებითებად
    negatives = []
    positives = []

    for x in arr:
        if x < 0:
            negatives.append(-x)   # ვაქცევთ დადებითად რომ დავალაგოთ
        else:
            positives.append(x)

    # ვალაგებთ ცალ-ცალკე
    negatives = lsd_radix(negatives)
    positives = lsd_radix(positives)

    # უარყოფითები უკან ვაბრუნებთ და reverse
    result = []
    for x in reversed(negatives):
        result.append(-x)
    for x in positives:
        result.append(x)

    return result


# ტესტი
data = [-34, 5, -12, 0, 88, -1, 42]
print("Input: ", data)
print("Output:", radix_sort(data))
