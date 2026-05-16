# Streaming Bucket Sort - მუდმივი მეხსიერებით
#
# პრობლემა: მონაცემი მოდის უსასრულოდ. ვერ შევინახავთ ყველაფერს.
# გვინდა: top-k (ყველაზე ხშირი) + median (შუა მნიშვნელობა)
#
# 2 ხელსაწყო:
#   1. Count-Min Sketch - სიხშირის დასათვლელად
#   2. Reservoir Sampling - შემთხვევითი sample-ისთვის

import random
import sys

sys.stdout.reconfigure(encoding='utf-8')


# ═════════════════════════════════════════════════════════════
# 1. COUNT-MIN SKETCH - სიხშირის approximate counter
# ═════════════════════════════════════════════════════════════
# იდეა: ერთი მასივის ნაცვლად გვაქვს რამდენიმე მასივი (3-5).
# თითო ელემენტი ემატება ყველაში სხვადასხვა hash-ით.
# Estimate = ყველაზე პატარა მნიშვნელობა.

WIDTH = 5000     # თითო მასივის სიგრძე (დიდი = ნაკლები collision)
DEPTH = 3        # რამდენი მასივი გვაქვს

# ვქმნით DEPTH ცალ ცარიელ მასივს, თითო WIDTH ზომის
sketch = []
for i in range(DEPTH):
    sketch.append([0] * WIDTH)


def get_bucket(x, row):
    # თითო row-სთვის ვცვლით hash-ის სიდიდეს
    return (hash(x) + row * 31) % WIDTH


def sketch_add(x):
    # ვამატებთ ყველა მასივში
    for row in range(DEPTH):
        sketch[row][get_bucket(x, row)] += 1


def sketch_count(x):
    # ვიღებთ ყველაზე პატარა მნიშვნელობას ყველა მასივიდან
    smallest = sketch[0][get_bucket(x, 0)]
    for row in range(1, DEPTH):
        value = sketch[row][get_bucket(x, row)]
        if value < smallest:
            smallest = value
    return smallest


# ═════════════════════════════════════════════════════════════
# 2. RESERVOIR SAMPLING - შემთხვევითი sample
# ═════════════════════════════════════════════════════════════
# იდეა: ვინახავთ მხოლოდ SIZE ცალ ელემენტს.
# როცა მოდის ახალი, ვცვლით ძველს ალბათობით size/n.

SIZE = 500
reservoir = []
seen = 0    # სულ რამდენი ელემენტი მოვიდა


def reservoir_add(x):
    global seen
    seen += 1

    if len(reservoir) < SIZE:
        # თავიდან უბრალოდ ვამატებთ
        reservoir.append(x)
    else:
        # უკვე სავსეა - ვცვლით შემთხვევით პოზიციას
        j = random.randint(0, seen - 1)
        if j < SIZE:
            reservoir[j] = x


def get_median():
    sorted_sample = sorted(reservoir)
    middle = len(sorted_sample) // 2
    return sorted_sample[middle]


# ═════════════════════════════════════════════════════════════
# 3. TOP-K - ვინახავთ K კანდიდატს
# ═════════════════════════════════════════════════════════════

K = 5
top_k = {}     # სიტყვა -> approximate count


def update_top_k(x):
    count = sketch_count(x)

    if x in top_k:
        # უკვე გვაქვს - ვანახლებთ count-ს
        top_k[x] = count
    elif len(top_k) < K:
        # ჯერ არ შევსებულა K-მდე - ვამატებთ
        top_k[x] = count
    else:
        # სავსეა - ვამოწმებთ, თუ ეს უფრო ხშირია ვიდრე ყველაზე იშვიათი
        smallest_item = None
        smallest_count = None
        for item in top_k:
            if smallest_count is None or top_k[item] < smallest_count:
                smallest_count = top_k[item]
                smallest_item = item

        if count > smallest_count:
            del top_k[smallest_item]
            top_k[x] = count


# ═════════════════════════════════════════════════════════════
# 4. MAIN - ვამუშავებთ თითო ელემენტს stream-ში
# ═════════════════════════════════════════════════════════════

def process(x):
    sketch_add(x)
    update_top_k(x)


# ═════════════════════════════════════════════════════════════
# ტესტი
# ═════════════════════════════════════════════════════════════

random.seed(42)

# ვქმნით fake stream-ს
# ხშირი სიტყვები: apple, banana, cherry, date, elder
# იშვიათი სიტყვები: rare_1, rare_2, ... rare_50000
frequent_words = ["apple", "banana", "cherry", "date", "elder"]

N = 100_000
true_counts = {}   # ნამდვილი სიხშირე შესამოწმებლად

print(f"ვამუშავებთ {N} ელემენტს stream-იდან...\n")

for i in range(N):
    # 50% შემთხვევაში ხშირი სიტყვა
    if random.random() < 0.5:
        word = random.choice(frequent_words)
    else:
        word = "rare_" + str(random.randint(0, 50000))

    # ვამუშავებთ ისე როგორც stream-დან მოვიდა
    process(word)

    # ნამდვილ count-ს ვინახავთ მხოლოდ შესამოწმებლად
    if word in true_counts:
        true_counts[word] += 1
    else:
        true_counts[word] = 1

    # მედიანისთვის რიცხვებიც ცალკე
    reservoir_add(random.randint(1, 1000))


# შედეგი - TOP K
print("=== TOP 5 ხშირი სიტყვა ===")
print(f"{'სიტყვა':<15} {'approx':>10} {'ნამდვილი':>10}")
print("-" * 40)

# ვალაგებთ count-ის მიხედვით კლებადობით
sorted_top = sorted(top_k.items(), key=lambda pair: -pair[1])
for word, count in sorted_top:
    true = true_counts.get(word, 0)
    print(f"{word:<15} {count:>10} {true:>10}")


# შედეგი - MEDIAN
print("\n=== APPROXIMATE MEDIAN ===")
print(f"sample size: {len(reservoir)}")
print(f"median: {get_median()}")
print(f"(უნდა იყოს ~500, რადგან რიცხვები [1, 1000]-დან)")


# მეხსიერების კონტროლი
total_memory = WIDTH * DEPTH + SIZE + K
print(f"\n=== მეხსიერება ===")
print(f"sketch:    {WIDTH * DEPTH} cell")
print(f"reservoir: {SIZE} cell")
print(f"top_k:     {K} cell")
print(f"სულ:       {total_memory} cell (stream-ის ზომისგან დამოუკიდებლად!)")
