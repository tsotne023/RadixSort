
def american_flag_sort(arr, lo, hi, d, length):
    # ბაზური შემთხვევები
    if hi - lo <= 1:
        return                  # 0 ან 1 ელემენტი - უკვე დალაგებულია
    if d >= length:
        return                  # სიმბოლოები ამოგვეწურა

    R = 256   # ASCII alphabet (0-255)

    # ნაბიჯი 1: SCAN - ვითვლით სიმბოლოებს d პოზიციაზე
    count = [0] * R
    for i in range(lo, hi):
        c = ord(arr[i][d])
        count[c] += 1

    # ნაბიჯი 2: STARTS - სად იწყება თითო bucket
    starts = [0] * R
    starts[0] = lo
    for k in range(1, R):
        starts[k] = starts[k - 1] + count[k - 1]

    # next_pos = სად დავწეროთ შემდეგი ელემენტი თითო bucket-ში
    # (starts-ის ასლი, რადგან swap-ის დროს იცვლება)
    next_pos = list(starts)

    # ნაბიჯი 3: SWAP - ელემენტების ადგილებზე გადატანა
    for k in range(R):
        bucket_end = starts[k] + count[k]

        while next_pos[k] < bucket_end:
            elem = arr[next_pos[k]]
            target_bucket = ord(elem[d])

            if target_bucket == k:
                # უკვე სწორ ადგილზეა - გადავდივართ შემდეგზე
                next_pos[k] += 1
            else:
                # ვცვლით ადგილებს სწორი bucket-ის ცარიელ პოზიციასთან
                i = next_pos[k]
                j = next_pos[target_bucket]
                arr[i], arr[j] = arr[j], arr[i]
                next_pos[target_bucket] += 1

    # ნაბიჯი 4: RECURSE - თითო bucket-ისთვის გავაგრძელოთ შემდეგი სიმბოლოთი
    for k in range(R):
        if count[k] > 1:
            bucket_start = starts[k]
            bucket_end = bucket_start + count[k]
            american_flag_sort(arr, bucket_start, bucket_end, d + 1, length)


# ტესტი
words = ["BAT", "CAT", "ANT", "BEE", "ACE", "BAR", "CAB", "BAD"]
print("Input: ", words)

american_flag_sort(words, 0, len(words), 0, 3)

print("Output:", words)
