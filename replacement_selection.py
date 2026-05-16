# Replacement Selection - External Sort-ის Phase 1-ის გაუმჯობესება
#
# ჩვეულებრივი Phase 1: ვკითხულობთ M ელემენტს, ვალაგებთ, ვწერთ.
# შედეგი: თითო run = M ელემენტი.
#
# Replacement Selection: ვიყენებთ მუდმივად მუშა min-heap-ს.
# შედეგი: საშუალო run = 2M ელემენტი (ორჯერ მეტი!)
#
# იდეა:
#   1. ვავსებთ heap-ს M ელემენტით
#   2. ვაგდებთ მინიმუმს (output), ვიღებთ ახალ ელემენტს
#   3. თუ ახალი >= ბოლო output → heap-ში ჩვეულებრივად
#   4. თუ ახალი <  ბოლო output → "frozen" (შემდეგი run-ისთვის)
#   5. როცა heap დაცარიელდება → frozen-ისგან ვაშენებთ ახალ heap-ს

import heapq
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')


def replacement_selection(data, heap_size, verbose=False):
    runs = []
    current_run = []
    heap = []
    frozen = []

    data_iter = iter(data)

    # ნაბიჯი 1: ვავსებთ heap-ს პირველი heap_size ელემენტით
    for _ in range(heap_size):
        try:
            x = next(data_iter)
            heapq.heappush(heap, x)
        except StopIteration:
            break

    if verbose:
        print(f"საწყისი heap: {sorted(heap)}\n")

    last_output = float('-inf')
    step = 1

    while heap or frozen:
        # თუ heap დაცარიელდა - დასრულდა მიმდინარე run
        if not heap:
            if verbose:
                print(f"  >>> heap დაცარიელდა - Run {len(runs)+1} დასრულდა: {current_run}")
            runs.append(current_run)
            current_run = []
            # frozen ელემენტებიდან ვაშენებთ ახალ heap-ს
            heap = list(frozen)
            heapq.heapify(heap)
            frozen = []
            last_output = float('-inf')
            if verbose:
                print(f"  >>> Run {len(runs)+1} იწყება: heap = {sorted(heap)}\n")

        # ვაგდებთ მინიმუმს
        x = heapq.heappop(heap)
        current_run.append(x)
        last_output = x

        # ვცდილობთ წავიკითხოთ შემდეგი ელემენტი
        try:
            y = next(data_iter)
            if y >= last_output:
                heapq.heappush(heap, y)
                action = "ემატება heap-ში"
            else:
                frozen.append(y)
                action = f"FROZEN ({y} < {last_output})"
            if verbose:
                print(f"  ნაბიჯი {step:2}: output={x:2}, read={y:2}, {action}")
                print(f"             heap={sorted(heap)}, frozen={frozen}")
        except StopIteration:
            if verbose:
                print(f"  ნაბიჯი {step:2}: output={x:2} (input ამოწურა)")
                print(f"             heap={sorted(heap)}, frozen={frozen}")

        step += 1

    if current_run:
        if verbose:
            print(f"  >>> Run {len(runs)+1} დასრულდა: {current_run}")
        runs.append(current_run)

    return runs


# ═════════════════════════════════════════════════════════════
# ნაწილი 1: სიმულაცია მოცემული input-ით
# ═════════════════════════════════════════════════════════════

print("=" * 60)
print("REPLACEMENT SELECTION SIMULATION")
print("=" * 60)

data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 7, 2, 6, 4]
M = 4

print(f"Input: {data}")
print(f"Heap size M = {M}\n")

runs = replacement_selection(data, M, verbose=True)

print(f"\n{'=' * 60}")
print("შედეგი - RUNS:")
print('=' * 60)
for i, r in enumerate(runs, 1):
    sorted_check = "✓" if r == sorted(r) else "X"
    print(f"  Run {i}  (სიგრძე {len(r)}) {sorted_check}: {r}")

avg_length = len(data) / len(runs)
print(f"\nსაშუალო run სიგრძე: {len(data)}/{len(runs)} = {avg_length:.2f}")
print(f"თეორიული 2M = {2 * M} (asymptotic, ცოტა input-ზე ჯერ ვერ ჩანს)")


# ═════════════════════════════════════════════════════════════
# ნაწილი 2: ემპირიული მტკიცებულება რომ avg = 2M
# ═════════════════════════════════════════════════════════════

print(f"\n{'=' * 60}")
print("EMPIRIC PROOF: საშუალო run სიგრძე → 2M")
print('=' * 60)

print(f"{'M':>4} {'N':>8} {'რუნი':>6} {'საშ.სიგრძე':>12} {'2M':>6} {'შეფარდება':>10}")
print("-" * 55)

random.seed(123)

for M in [4, 16, 64, 256]:
    N = M * 1000   # ბევრი input რომ asymptotic იყოს ცხადი
    data = [random.randint(0, 1000000) for _ in range(N)]

    runs = replacement_selection(data, M, verbose=False)
    avg = N / len(runs)
    ratio = avg / (2 * M)

    print(f"{M:>4} {N:>8} {len(runs):>6} {avg:>12.2f} {2*M:>6} {ratio:>10.3f}")

print("\n→ შეფარდება ~1.0 ნიშნავს რომ საშუალო ≈ 2M ✓")


# ═════════════════════════════════════════════════════════════
# ნაწილი 3: მტკიცებულების ინტუიცია
# ═════════════════════════════════════════════════════════════

print(f"""
{'=' * 60}
რატომ 2M? - SNOWPLOW ანალოგია (Knuth)
{'=' * 60}

წარმოვიდგინოთ თოვლის გასაწმენდი მანქანა მრგვალ გზაზე სიგრძით 2M.
- გზაზე თანაბრად ცვივა თოვლი (input ელემენტები)
- მანქანა მუდმივი სიჩქარით იწევს წინ და ასუფთავებს თოვლს
- მანქანის წინ თოვლი გროვდება სამკუთხედის ფორმით

steady-state-ში:
- მანქანის წინ თოვლის რაოდენობა = M (heap-ის ზომა)
- ერთ წრეზე მანქანა აგროვებს 2M თოვლს

თარგმანი ალგორითმზე:
- მანქანა = ბოლო output-ი (კურსორი)
- მის "წინ" თოვლი = ელემენტები რომლებიც last_output-ზე მეტი ან ტოლი
- მის "უკან" თოვლი = frozen ელემენტები (შემდეგი run)
- ერთი run = მანქანის ერთი წრე = 2M ელემენტი

ფორმალურად:
- random input-ისთვის ალბათობა რომ ახალი ელემენტი y >= last_output-ი = 1/2
- მაგრამ heap-ში წინ მიდის - last_output თანდათან იზრდება
- შედეგი: ჯამში თითო run = 2M ელემენტი საშუალოდ

გავლენა External Sort-ზე:
- ჩვეულებრივად: N/M run → log_k(N/M) merge pass
- Replacement Selection-ით: N/(2M) run → log_k(N/(2M)) merge pass
- გაცილებით ნაკლები I/O!
""")
