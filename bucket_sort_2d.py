# 2D Point Cloud Bucket Sort
# Input: N წერტილი (x, y) ∈ [0, 1)²
# დალაგება: ჯერ x-ის მიხედვით, შემდეგ y-ის

import random
import time


def hash_point(p, k):
    # წერტილს ვუბრუნებთ bucket-ის ინდექსს (k*k grid-ში)
    i = int(p[0] * k)
    j = int(p[1] * k)
    if i >= k:
        i = k - 1
    if j >= k:
        j = k - 1
    return i, j


def bucket_sort_2d(points, k):
    # ნაბიჯი 1: k*k grid-ის შექმნა
    grid = [[[] for _ in range(k)] for _ in range(k)]

    # ნაბიჯი 2: hash → თითო წერტილი თავის bucket-ში
    for p in points:
        i, j = hash_point(p, k)
        grid[i][j].append(p)

    # ნაბიჯი 3: column-ების მიხედვით ვაგროვებთ და ვალაგებთ
    # თითო column i-ში x ∈ [i/k, (i+1)/k) - ე.ი. ყველა მათგანი
    # უფრო პატარა x-ით არიან ვიდრე i+1 column-ის წერტილები
    result = []
    for i in range(k):
        column = []
        for j in range(k):
            column.extend(grid[i][j])
        column.sort()    # tuple sort = lexicographic ((x, y))
        result.extend(column)

    return result


def timsort_2d(points):
    # Python-ის built-in sort (Timsort)
    return sorted(points)


def radix_sort_2d(points, bits=24):
    # x-ით ვალაგებთ LSD radix sort-ით (კვანტიზებული 2^bits ბინად),
    # შემდეგ თითო ჯგუფს, რომელსაც ერთიდაიგივე xi აქვს,
    # ვალაგებთ (x, y) ფლოატებით (პრეციზიის შესანარჩუნებლად).
    scale = 1 << bits

    # თითო წერტილს ვუმაგრებთ xi-ს (კვანტიზებული x)
    items = [(int(x * scale), (x, y)) for x, y in points]

    NBITS = 8                    # 8-bit chunks
    BUCKETS = 1 << NBITS         # 256
    MASK = BUCKETS - 1

    # LSD radix sort xi-ის მიხედვით
    for shift in range(0, bits, NBITS):
        buckets = [[] for _ in range(BUCKETS)]
        for item in items:
            d = (item[0] >> shift) & MASK
            buckets[d].append(item)
        items = []
        for b in buckets:
            items.extend(b)

    # ერთიდაიგივე xi-ის მქონე წერტილებს ვალაგებთ (x, y) ფლოატებით
    result = []
    i = 0
    while i < len(items):
        j = i
        while j < len(items) and items[j][0] == items[i][0]:
            j += 1
        group = [p for _, p in items[i:j]]
        group.sort()
        result.extend(group)
        i = j

    return result


def benchmark(n, k):
    print(f"=== n = {n}, k = {k} (grid = {k}x{k} = {k*k} buckets) ===\n")

    points = [(random.random(), random.random()) for _ in range(n)]

    # --- Timsort ---
    t = time.perf_counter()
    sorted_tim = timsort_2d(points)
    tim_time = time.perf_counter() - t
    print(f"  Timsort:     {tim_time:.3f}s")

    # --- Bucket sort 2D ---
    t = time.perf_counter()
    sorted_bucket = bucket_sort_2d(points, k)
    bucket_time = time.perf_counter() - t
    print(f"  Bucket 2D:   {bucket_time:.3f}s")

    # --- Radix sort ---
    t = time.perf_counter()
    sorted_radix = radix_sort_2d(points)
    radix_time = time.perf_counter() - t
    print(f"  Radix:       {radix_time:.3f}s")

    # კორექტულობის შემოწმება
    assert sorted_bucket == sorted_tim, "Bucket sort error!"
    assert sorted_radix == sorted_tim, "Radix sort error!"
    print("  All sorts produce same result: OK\n")


def find_best_k(n):
    # სხვადასხვა k-ზე ვამოწმებთ bucket sort-ის სიჩქარეს
    print(f"=== Optimal k search (n = {n}) ===\n")
    points = [(random.random(), random.random()) for _ in range(n)]

    best_k = None
    best_time = float('inf')

    for k in [10, 30, 100, 300, 1000]:
        t = time.perf_counter()
        bucket_sort_2d(points, k)
        elapsed = time.perf_counter() - t
        avg_per_bucket = n / (k * k)
        marker = ""
        if elapsed < best_time:
            best_time = elapsed
            best_k = k
            marker = " <-- best"
        print(f"  k = {k:>4}  ({k*k:>7} buckets, ~{avg_per_bucket:>7.1f} pts/bucket): {elapsed:.3f}s{marker}")

    print(f"\n  Best k = {best_k} ({best_time:.3f}s)\n")
    return best_k


if __name__ == "__main__":
    random.seed(42)

    # ჯერ მცირე ტესტი კორექტულობისთვის
    test_points = [(0.5, 0.3), (0.1, 0.9), (0.5, 0.1), (0.9, 0.4)]
    assert bucket_sort_2d(test_points, 4) == sorted(test_points)
    assert radix_sort_2d(test_points) == sorted(test_points)
    print("Correctness test: PASSED\n")

    # ოპტიმალური k-ის ძებნა (პატარა n-ზე უფრო სწრაფი)
    best_k = find_best_k(100_000)

    # მთავარი benchmark - 1,000,000 წერტილი
    benchmark(1_000_000, best_k)
