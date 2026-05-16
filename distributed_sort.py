# Distributed Sort - 4 სერვერი ერთად ალაგებს მონაცემს
#
# პრობლემა: მონაცემი skewed-ია (80% არის [0, 0.1)-ში).
# თუ თანაბრად დავყოფთ - ერთი სერვერი იღებს უმეტესობას.
# გადაწყვეტა: ვიღებთ ნიმუშს და ვირჩევთ boundary-ებს მისგან.

import random
import sys
sys.stdout.reconfigure(encoding='utf-8')   # Windows-ისთვის ქართული print

# ვქმნით 4 სერვერის მონაცემს
# თითოში 10000 ელემენტი, 80% პატარა რიცხვი
server0 = []
server1 = []
server2 = []
server3 = []

for i in range(10000):
    r = random.random()
    if r < 0.8:
        x = random.random() * 0.1
    else:
        x = 0.1 + random.random() * 0.9
    server0.append(x)

for i in range(10000):
    r = random.random()
    if r < 0.8:
        x = random.random() * 0.1
    else:
        x = 0.1 + random.random() * 0.9
    server1.append(x)

for i in range(10000):
    r = random.random()
    if r < 0.8:
        x = random.random() * 0.1
    else:
        x = 0.1 + random.random() * 0.9
    server2.append(x)

for i in range(10000):
    r = random.random()
    if r < 0.8:
        x = random.random() * 0.1
    else:
        x = 0.1 + random.random() * 0.9
    server3.append(x)


# === ვერსია 1: NAIVE ===
# თანაბრად ვყოფთ [0, 1) ოთხ ნაწილად

print("ვერსია 1: NAIVE (თანაბრად დაყოფა)")

c0 = 0
c1 = 0
c2 = 0
c3 = 0

# სერვერ 0-ის მონაცემი
for i in range(10000):
    x = server0[i]
    if x < 0.25:
        c0 = c0 + 1
    elif x < 0.5:
        c1 = c1 + 1
    elif x < 0.75:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

# სერვერ 1-ის მონაცემი
for i in range(10000):
    x = server1[i]
    if x < 0.25:
        c0 = c0 + 1
    elif x < 0.5:
        c1 = c1 + 1
    elif x < 0.75:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

# სერვერ 2-ის მონაცემი
for i in range(10000):
    x = server2[i]
    if x < 0.25:
        c0 = c0 + 1
    elif x < 0.5:
        c1 = c1 + 1
    elif x < 0.75:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

# სერვერ 3-ის მონაცემი
for i in range(10000):
    x = server3[i]
    if x < 0.25:
        c0 = c0 + 1
    elif x < 0.5:
        c1 = c1 + 1
    elif x < 0.75:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

print("სერვერი 0:", c0)
print("სერვერი 1:", c1)
print("სერვერი 2:", c2)
print("სერვერი 3:", c3)


# === ვერსია 2: SAMPLING ===
# ვიღებთ ნიმუშს, ვირჩევთ boundary-ებს ნიმუშიდან

print("")
print("ვერსია 2: SAMPLING (ნიმუშის მიხედვით)")

# ვაგროვებთ 100-100 ელემენტს თითო სერვერიდან
sample = []
for i in range(100):
    idx = random.randint(0, 9999)
    sample.append(server0[idx])
for i in range(100):
    idx = random.randint(0, 9999)
    sample.append(server1[idx])
for i in range(100):
    idx = random.randint(0, 9999)
    sample.append(server2[idx])
for i in range(100):
    idx = random.randint(0, 9999)
    sample.append(server3[idx])

sample.sort()

# boundary-ები - 1/4, 2/4, 3/4 ადგილებიდან
b1 = sample[100]
b2 = sample[200]
b3 = sample[300]

print("b1 =", b1)
print("b2 =", b2)
print("b3 =", b3)

# ისევ ვითვლით, ოღონდ ახალი boundary-ებით
c0 = 0
c1 = 0
c2 = 0
c3 = 0

for i in range(10000):
    x = server0[i]
    if x < b1:
        c0 = c0 + 1
    elif x < b2:
        c1 = c1 + 1
    elif x < b3:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

for i in range(10000):
    x = server1[i]
    if x < b1:
        c0 = c0 + 1
    elif x < b2:
        c1 = c1 + 1
    elif x < b3:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

for i in range(10000):
    x = server2[i]
    if x < b1:
        c0 = c0 + 1
    elif x < b2:
        c1 = c1 + 1
    elif x < b3:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

for i in range(10000):
    x = server3[i]
    if x < b1:
        c0 = c0 + 1
    elif x < b2:
        c1 = c1 + 1
    elif x < b3:
        c2 = c2 + 1
    else:
        c3 = c3 + 1

print("სერვერი 0:", c0)
print("სერვერი 1:", c1)
print("სერვერი 2:", c2)
print("სერვერი 3:", c3)
