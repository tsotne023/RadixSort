# Distributed Sort
# 4 server-i alagebs monacems erTad
# problema: monacemi skewed-ia, naive partition ar mushaobs
# gadawyveta: sampling-based boundary-ebi

import random

# vqmnit 4 server-is monacems
# titoshi 10000 element, 80% patara ricxvi
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


# === VERSION 1: NAIVE ===
# tanabrad vyofT [0, 1) - oTx natilad

print("NAIVE:")

c0 = 0
c1 = 0
c2 = 0
c3 = 0

# server 0-is monacemi
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

# server 1-is monacemi
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

# server 2-is monacemi
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

# server 3-is monacemi
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

print("server 0:", c0)
print("server 1:", c1)
print("server 2:", c2)
print("server 3:", c3)


# === VERSION 2: SAMPLING ===
# vigebt nimushs, vrCevT boundary-ebs nimushidan

print("")
print("SAMPLING:")

# vagrovebT 100-100 element tito server-idan
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

# boundary-ebi - 1/4, 2/4, 3/4 adgilebidan
b1 = sample[100]
b2 = sample[200]
b3 = sample[300]

print("b1 =", b1)
print("b2 =", b2)
print("b3 =", b3)

# ahla iseve vTvliT
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

print("server 0:", c0)
print("server 1:", c1)
print("server 2:", c2)
print("server 3:", c3)
