# Parallel Radix Sort - 4 thread-ით

import threading

NUM_THREADS = 4


def count_chunk(arr, exp, start, end, result, tid):
    # თითო thread ითვლის თავის ნაწილში ციფრებს
    # თავის count მასივში (არ ეხება სხვა thread-ის მონაცემებს!)
    my_count = [0] * 10
    for i in range(start, end):
        digit = (arr[i] // exp) % 10
        my_count[digit] += 1
    result[tid] = my_count


def write_chunk(arr, exp, start, end, output, positions, tid):
    # თითო thread წერს output-ში თავის გამოყოფილ ადგილებში
    pos = list(positions[tid])  # ვაკოპირებთ რომ არ შევცვალოთ original
    for i in range(start, end):
        digit = (arr[i] // exp) % 10
        output[pos[digit]] = arr[i]
        pos[digit] += 1


def parallel_counting_sort(arr, exp):
    n = len(arr)
    if n == 0:
        return arr

    # ვყოფთ მასივს 4 ნაწილად
    chunk_size = n // NUM_THREADS

    # === ნაბიჯი 1: ყველა thread ითვლის თავის ნაწილს ===
    counts = [None] * NUM_THREADS
    threads = []

    for tid in range(NUM_THREADS):
        start = tid * chunk_size
        if tid == NUM_THREADS - 1:
            end = n   # ბოლო thread-ი იღებს ნაშთსაც
        else:
            end = start + chunk_size

        t = threading.Thread(target=count_chunk, args=(arr, exp, start, end, counts, tid))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # === ნაბიჯი 2: ვითვლით სად დაიწყოს თითო thread წერა (prefix sum) ===
    positions = [[0] * 10 for _ in range(NUM_THREADS)]
    total = 0
    for digit in range(10):
        for tid in range(NUM_THREADS):
            positions[tid][digit] = total
            total += counts[tid][digit]

    # === ნაბიჯი 3: ყველა thread წერს output-ში ===
    output = [0] * n
    threads = []

    for tid in range(NUM_THREADS):
        start = tid * chunk_size
        if tid == NUM_THREADS - 1:
            end = n
        else:
            end = start + chunk_size

        t = threading.Thread(target=write_chunk, args=(arr, exp, start, end, output, positions, tid))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return output


def lsd_radix(arr):
    if len(arr) == 0:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = parallel_counting_sort(arr, exp)
        exp = exp * 10
    return arr


def parallel_radix_sort(arr):
    # უარყოფითები ცალკე, დადებითები ცალკე
    negatives = []
    positives = []
    for x in arr:
        if x < 0:
            negatives.append(-x)
        else:
            positives.append(x)

    negatives = lsd_radix(negatives)
    positives = lsd_radix(positives)

    result = []
    for x in reversed(negatives):
        result.append(-x)
    for x in positives:
        result.append(x)
    return result


# ტესტი
data = [-34, 5, -12, 0, 88, -1, 42]
print("Input: ", data)
print("Output:", parallel_radix_sort(data))
