import sys
sys.stdout.reconfigure(encoding='utf-8')

# External Sort I/O Analysis
#
# როცა მონაცემი იმდენად დიდია რომ RAM-ში არ ეტევა, ვალაგებთ disk-ზე.
# ვითვლით რამდენი დრო სჭირდება I/O-ს (disk reads + writes).

# === მოცემული ===
N = 2 * 1024              # 2 TB = 2048 GB
M = 128                   # RAM = 128 GB
B = 4 / (1024 * 1024)     # block size = 4 KB = 4 / 1M GB
BANDWIDTH = 1             # 1 GB/s

print(f"მონაცემები:")
print(f"  N = {N} GB (2 TB)")
print(f"  M = {M} GB RAM")
print(f"  B = 4 KB block")
print(f"  bandwidth = {BANDWIDTH} GB/s\n")


# ═════════════════════════════════════════════════════════════
# PHASE 1: Initial sorted runs
# ═════════════════════════════════════════════════════════════
# ვკითხულობთ N-ს M ზომის ნაჭრებად, ვალაგებთ RAM-ში, ვწერთ უკან.

print("=== PHASE 1: Sorted Runs ===")

num_runs = N // M
print(f"Sorted runs: N/M = {N}/{M} = {num_runs} run")

# I/O: ერთხელ ვკითხულობთ ყველაფერს, ერთხელ ვწერთ
phase1_read = N / BANDWIDTH
phase1_write = N / BANDWIDTH
phase1_time = phase1_read + phase1_write

print(f"Read time:  {N} GB / {BANDWIDTH} GB/s = {phase1_read} s")
print(f"Write time: {N} GB / {BANDWIDTH} GB/s = {phase1_write} s")
print(f"Phase 1 total: {phase1_time} s = {phase1_time/60:.1f} min\n")


# ═════════════════════════════════════════════════════════════
# PHASE 2 (option A): 2-way merge
# ═════════════════════════════════════════════════════════════
# თითო pass-ში ვაერთიანებთ წყვილებად: 16 -> 8 -> 4 -> 2 -> 1

print("=== PHASE 2A: 2-way Merge ===")

# log2(16) = 4 pass
import math
passes_2way = math.ceil(math.log2(num_runs))
print(f"Passes: log2({num_runs}) = {passes_2way}")
print(f"  Pass 1: {num_runs} -> {num_runs // 2} run")
print(f"  Pass 2: {num_runs // 2} -> {num_runs // 4} run")
print(f"  Pass 3: {num_runs // 4} -> {num_runs // 8} run")
print(f"  Pass 4: {num_runs // 8} -> 1 run")

# თითო pass = მთელი N-ის read + write
per_pass_time = 2 * N / BANDWIDTH
phase2a_time = passes_2way * per_pass_time

print(f"Time per pass: 2 * {N} GB / {BANDWIDTH} GB/s = {per_pass_time} s")
print(f"Phase 2A total: {passes_2way} * {per_pass_time} = {phase2a_time} s\n")

total_2way = phase1_time + phase2a_time
print(f">>> 2-way TOTAL: {total_2way} s = {total_2way/3600:.2f} hours\n")


# ═════════════════════════════════════════════════════════════
# PHASE 2 (option B): 16-way merge
# ═════════════════════════════════════════════════════════════
# ერთ pass-ში ვაერთიანებთ 16-ვე run-ს ერთდროულად

print("=== PHASE 2B: 16-way Merge ===")

k = 16
passes_kway = math.ceil(math.log(num_runs, k))
print(f"Passes: log_{k}({num_runs}) = {passes_kway}")
print(f"  Pass 1: {num_runs} -> 1 run (ერთბაშად ყველაფერი!)")

phase2b_time = passes_kway * per_pass_time
print(f"Phase 2B total: {passes_kway} * {per_pass_time} = {phase2b_time} s\n")

total_kway = phase1_time + phase2b_time
print(f">>> 16-way TOTAL: {total_kway} s = {total_kway/3600:.2f} hours\n")


# ═════════════════════════════════════════════════════════════
# შედარება
# ═════════════════════════════════════════════════════════════

print("=== შედარება ===")
saved = total_2way - total_kway
saved_pct = saved / total_2way * 100

print(f"2-way:   {total_2way} s ({total_2way/3600:.2f} h)")
print(f"16-way:  {total_kway} s ({total_kway/3600:.2f} h)")
print(f"დაზოგვა: {saved} s ({saved/3600:.2f} h)")
print(f"        = {saved_pct:.0f}% უფრო სწრაფი\n")


# ═════════════════════════════════════════════════════════════
# შემოწმება: k-way merge-ისთვის საკმარისი RAM გვაქვს?
# ═════════════════════════════════════════════════════════════

print("=== Buffer შემოწმება ===")

# k-way merge-ისთვის გვჭირდება k+1 buffer (k input + 1 output)
# თითო buffer-ის ზომა მინიმუმ B (1 block)
buffers_needed = k + 1
min_ram_needed_gb = buffers_needed * B

print(f"k+1 = {buffers_needed} buffer x 4 KB = {buffers_needed * 4} KB")
print(f"RAM გვაქვს {M} GB - ბევრად მეტი ვიდრე საჭიროა ✓\n")

# რა მაქსიმალური k შეიძლება გვქონდეს ერთ pass-ში?
max_k = int(M / B)
print(f"მაქს k = M/B = {M} GB / 4 KB = {max_k:,} გზიანი merge")
print(f"შეგვიძლია ყველაფერი 1 pass-ში დავამთავროთ!")
