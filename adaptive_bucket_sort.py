import random
import time
import bisect


def naive_bucket_sort(arr, num_buckets):
    # თანაბრად დაყოფილი bucket-ები [0, 1)-ში
    buckets = [[] for _ in range(num_buckets)]

    for x in arr:
        idx = int(x * num_buckets)
        if idx >= num_buckets:
            idx = num_buckets - 1
        buckets[idx].append(x)

    result = []
    for b in buckets:
        b.sort()
        result.extend(b)
    return result


def adaptive_bucket_sort(arr, num_buckets):
    n = len(arr)
    if n == 0:
        return arr

    min_val = min(arr)
    max_val = max(arr)
    range_size = max_val - min_val
    if range_size == 0:
        return list(arr)

    # ნაბიჯი 1: HISTOGRAM - წვრილი bin-ებით ვითვლით density-ს
    NUM_BINS = 1000
    histogram = [0] * NUM_BINS

    for x in arr:
        bin_idx = int((x - min_val) / range_size * NUM_BINS)
        if bin_idx >= NUM_BINS:
            bin_idx = NUM_BINS - 1
        histogram[bin_idx] += 1

    # ნაბიჯი 2: BOUNDARIES - ვირჩევთ მიჯნებს ისე რომ თითო bucket-ში
    # დაახლოებით n/num_buckets ელემენტი მოხვდეს (quantile-based)
    target = n / num_buckets
    boundaries = []
    cumulative = 0
    next_target = target

    for bin_idx in range(NUM_BINS):
        cumulative += histogram[bin_idx]
        while cumulative >= next_target and len(boundaries) < num_buckets - 1:
            boundary = min_val + (bin_idx + 1) / NUM_BINS * range_size
            boundaries.append(boundary)
            next_target += target

    # ნაბიჯი 3: DISTRIBUTE - ვანაწილებთ ელემენტებს ადაპტურ bucket-ებში
    # binary search-ით (bisect) ვპოულობთ bucket-ს O(log k)-ში
    buckets = [[] for _ in range(num_buckets)]
    for x in arr:
        idx = bisect.bisect_right(boundaries, x)
        buckets[idx].append(x)

    # ნაბიჯი 4: SORT - თითო bucket-ი ცალკე
    result = []
    for b in buckets:
        b.sort()
        result.extend(b)
    return result


def show_distribution(name, data, num_buckets, use_adaptive):
    # ვაჩვენებთ რამდენი ელემენტი მოხვდა თითო bucket-ში
    if use_adaptive:
        n = len(data)
        min_val = min(data)
        max_val = max(data)
        range_size = max_val - min_val

        NUM_BINS = 1000
        histogram = [0] * NUM_BINS
        for x in data:
            bin_idx = int((x - min_val) / range_size * NUM_BINS)
            if bin_idx >= NUM_BINS:
                bin_idx = NUM_BINS - 1
            histogram[bin_idx] += 1

        target = n / num_buckets
        boundaries = []
        cumulative = 0
        next_target = target
        for bin_idx in range(NUM_BINS):
            cumulative += histogram[bin_idx]
            while cumulative >= next_target and len(boundaries) < num_buckets - 1:
                boundary = min_val + (bin_idx + 1) / NUM_BINS * range_size
                boundaries.append(boundary)
                next_target += target

        sizes = [0] * num_buckets
        for x in data:
            idx = bisect.bisect_right(boundaries, x)
            sizes[idx] += 1
    else:
        sizes = [0] * num_buckets
        for x in data:
            idx = int(x * num_buckets)
            if idx >= num_buckets:
                idx = num_buckets - 1
            sizes[idx] += 1

    print(f"  {name}: max bucket = {max(sizes)}, min bucket = {min(sizes)}")


def benchmark():
    n = 100_000
    num_buckets = 100

    # uniform data: თანაბრად განაწილებული [0, 1)
    uniform = [random.random() for _ in range(n)]

    # skewed data: 80% [0, 0.1)-ში, 20% [0.1, 1.0)-ში
    skewed = []
    for _ in range(n):
        if random.random() < 0.8:
            skewed.append(random.random() * 0.1)
        else:
            skewed.append(0.1 + random.random() * 0.9)

    print(f"Benchmark: n = {n}, buckets = {num_buckets}\n")

    for name, data in [("UNIFORM", uniform), ("SKEWED ", skewed)]:
        print(f"=== {name} ===")

        show_distribution("naive   ", data, num_buckets, use_adaptive=False)
        show_distribution("adaptive", data, num_buckets, use_adaptive=True)

        t = time.perf_counter()
        naive_bucket_sort(data, num_buckets)
        naive_time = time.perf_counter() - t

        t = time.perf_counter()
        adaptive_bucket_sort(data, num_buckets)
        adaptive_time = time.perf_counter() - t

        speedup = naive_time / adaptive_time if adaptive_time > 0 else 0
        print(f"  naive    time: {naive_time:.3f}s")
        print(f"  adaptive time: {adaptive_time:.3f}s")
        print(f"  speedup:       {speedup:.2f}x\n")


if __name__ == "__main__":
    # კორექტულობის შემოწმება
    test_data = [0.42, 0.05, 0.99, 0.01, 0.5, 0.03, 0.8]
    assert adaptive_bucket_sort(test_data, 4) == sorted(test_data)
    print("Correctness test: PASSED\n")

    benchmark()
