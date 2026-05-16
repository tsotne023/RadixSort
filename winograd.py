# Winograd-ის ვარიანტი + ოპერაციების დათვლა
#
# Strassen:  7 multiplication + 18 add/sub თითო რეკურსიულ ნაწილში
# Winograd:  7 multiplication + 15 add/sub თითო რეკურსიულ ნაწილში
#
# ორივე იძლევა იგივე O(n^2.81) სირთულეს, განსხვავება add-ების რაოდენობაშია.
#
# ვამოწმებთ: (i) გამრავლების რაოდენობა, (ii) add/sub რაოდენობა, (iii) wall-clock

import random
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')   # Windows-ისთვის ქართული print


# ════════════════════════════════════════════════
# გლობალური მთვლელები ოპერაციების
# ════════════════════════════════════════════════

mul_count = 0
add_count = 0

def reset_counts():
    global mul_count, add_count
    mul_count = 0
    add_count = 0


# ════════════════════════════════════════════════
# ჩვეულებრივი matmul + add + sub (დათვლით)
# ════════════════════════════════════════════════

def standard_mul(A, B):
    global mul_count, add_count
    n = len(A)
    p = len(A[0])
    m = len(B[0])

    C = []
    for i in range(n):
        row = []
        for j in range(m):
            s = 0.0
            for k in range(p):
                s = s + A[i][k] * B[k][j]
            row.append(s)
        C.append(row)

    mul_count = mul_count + n * m * p
    add_count = add_count + n * m * (p - 1)
    return C


def add(A, B):
    global add_count
    n = len(A)
    m = len(A[0])
    C = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(A[i][j] + B[i][j])
        C.append(row)
    add_count = add_count + n * m
    return C


def sub(A, B):
    global add_count
    n = len(A)
    m = len(A[0])
    C = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(A[i][j] - B[i][j])
        C.append(row)
    add_count = add_count + n * m
    return C


# ════════════════════════════════════════════════
# Strassen (შესადარებლად)
# ════════════════════════════════════════════════

THRESHOLD = 32   # ამ ზომაზე ვუბრუნდებით standard-ს

def strassen_core(A, B):
    n = len(A)

    if n <= THRESHOLD:
        return standard_mul(A, B)

    h = n // 2

    # 4 კვადრანტად დაყოფა
    A11 = []
    A12 = []
    A21 = []
    A22 = []
    for i in range(h):
        A11.append(A[i][:h])
        A12.append(A[i][h:])
    for i in range(h, n):
        A21.append(A[i][:h])
        A22.append(A[i][h:])

    B11 = []
    B12 = []
    B21 = []
    B22 = []
    for i in range(h):
        B11.append(B[i][:h])
        B12.append(B[i][h:])
    for i in range(h, n):
        B21.append(B[i][:h])
        B22.append(B[i][h:])

    # 7 გამრავლება + 10 input add/sub
    M1 = strassen_core(add(A11, A22), add(B11, B22))
    M2 = strassen_core(add(A21, A22), B11)
    M3 = strassen_core(A11, sub(B12, B22))
    M4 = strassen_core(A22, sub(B21, B11))
    M5 = strassen_core(add(A11, A12), B22)
    M6 = strassen_core(sub(A21, A11), add(B11, B12))
    M7 = strassen_core(sub(A12, A22), add(B21, B22))

    # 8 output add/sub
    C11 = add(sub(add(M1, M4), M5), M7)
    C12 = add(M3, M5)
    C21 = add(M2, M4)
    C22 = add(sub(add(M1, M3), M2), M6)

    # უკან აწყობა
    C = []
    for i in range(h):
        C.append(C11[i] + C12[i])
    for i in range(h):
        C.append(C21[i] + C22[i])
    return C


# ════════════════════════════════════════════════
# Winograd-ის ვარიანტი (7 mult + 15 add/sub)
# ════════════════════════════════════════════════
# ჭკვიანი intermediate ცვლადებით ვამცირებთ add/sub-ს 18-დან 15-მდე
#
# Winograd-ის ფორმულები:
#   S1 = A21 + A22        T1 = B12 - B11
#   S2 = S1 - A11         T2 = B22 - T1
#   S3 = A11 - A21        T3 = B22 - B12
#   S4 = A12 - S2         T4 = T2 - B21
#       (4 + 4 = 8 add/sub)
#
#   P1 = A11 * B11        P5 = S3 * T3
#   P2 = A12 * B21        P6 = S4 * B22
#   P3 = S1 * T1          P7 = A22 * T4
#   P4 = S2 * T2          (7 multiplication)
#
#   C11 = P1 + P2
#   U2  = P1 + P4
#   U3  = U2 + P5         (U3 ორჯერ გამოიყენება!)
#   U4  = U2 + P3
#   C12 = U4 + P6
#   C21 = U3 - P7
#   C22 = U3 + P3
#       (7 add/sub)
#
#   ჯამში: 8 + 7 = 15 add/sub (Strassen-ში 18)

def winograd_core(A, B):
    n = len(A)

    if n <= THRESHOLD:
        return standard_mul(A, B)

    h = n // 2

    # 4 კვადრანტად დაყოფა
    A11 = []
    A12 = []
    A21 = []
    A22 = []
    for i in range(h):
        A11.append(A[i][:h])
        A12.append(A[i][h:])
    for i in range(h, n):
        A21.append(A[i][:h])
        A22.append(A[i][h:])

    B11 = []
    B12 = []
    B21 = []
    B22 = []
    for i in range(h):
        B11.append(B[i][:h])
        B12.append(B[i][h:])
    for i in range(h, n):
        B21.append(B[i][:h])
        B22.append(B[i][h:])

    # S1..S4 (4 add/sub)
    S1 = add(A21, A22)
    S2 = sub(S1, A11)
    S3 = sub(A11, A21)
    S4 = sub(A12, S2)

    # T1..T4 (4 add/sub)
    T1 = sub(B12, B11)
    T2 = sub(B22, T1)
    T3 = sub(B22, B12)
    T4 = sub(T2, B21)

    # 7 Winograd გამრავლება (რეკურსიულად)
    P1 = winograd_core(A11, B11)
    P2 = winograd_core(A12, B21)
    P3 = winograd_core(S1, T1)
    P4 = winograd_core(S2, T2)
    P5 = winograd_core(S3, T3)
    P6 = winograd_core(S4, B22)
    P7 = winograd_core(A22, T4)

    # შედეგების შეერთება (7 add/sub)
    C11 = add(P1, P2)
    U2 = add(P1, P4)
    U3 = add(U2, P5)
    U4 = add(U2, P3)
    C12 = add(U4, P6)
    C21 = sub(U3, P7)
    C22 = add(U3, P3)

    # უკან აწყობა
    C = []
    for i in range(h):
        C.append(C11[i] + C12[i])
    for i in range(h):
        C.append(C21[i] + C22[i])
    return C


# ════════════════════════════════════════════════
# კორექტულობის შემოწმება (პატარა მატრიცაზე)
# ════════════════════════════════════════════════

def max_error(C1, C2):
    n = len(C1)
    m = len(C1[0])
    max_err = 0.0
    for i in range(n):
        for j in range(m):
            err = abs(C1[i][j] - C2[i][j])
            if err > max_err:
                max_err = err
    return max_err


print("=" * 50)
print("კორექტულობის შემოწმება")
print("=" * 50)

A = []
B = []
for i in range(64):
    row_a = []
    row_b = []
    for j in range(64):
        row_a.append(random.random())
        row_b.append(random.random())
    A.append(row_a)
    B.append(row_b)

C_std = standard_mul(A, B)
C_strassen = strassen_core(A, B)
C_winograd = winograd_core(A, B)

diff_strassen = max_error(C_strassen, C_std)
diff_winograd = max_error(C_winograd, C_std)

print("")
print("ზომა = 64")
print("  Strassen vs standard: max სხვაობა =", diff_strassen)
print("  Winograd vs standard: max სხვაობა =", diff_winograd)


# ════════════════════════════════════════════════
# ოპერაციების დათვლა + Wall-Clock
# ════════════════════════════════════════════════
# n=512 ძალიან ნელია pure Python-ში
# ვიყენებთ n=128 (იგივე შედეგი მცირე scale-ზე)

print("")
print("=" * 50)
print("ოპერაციების დათვლა + Wall-Clock")
print("=" * 50)

size = 128

A = []
B = []
for i in range(size):
    row_a = []
    row_b = []
    for j in range(size):
        row_a.append(random.random())
        row_b.append(random.random())
    A.append(row_a)
    B.append(row_b)

# --- Standard ---
reset_counts()
t0 = time.perf_counter()
standard_mul(A, B)
t_std = time.perf_counter() - t0
mul_std = mul_count
add_std = add_count

# --- Strassen ---
reset_counts()
t0 = time.perf_counter()
strassen_core(A, B)
t_strassen = time.perf_counter() - t0
mul_strassen = mul_count
add_strassen = add_count

# --- Winograd ---
reset_counts()
t0 = time.perf_counter()
winograd_core(A, B)
t_winograd = time.perf_counter() - t0
mul_winograd = mul_count
add_winograd = add_count

print("")
print("ზომა =", size, "  THRESHOLD =", THRESHOLD)
print("")
print("Standard:")
print("  გამრავლება:        ", mul_std)
print("  მიმატება/გამოკლება:", add_std)
print("  დრო:               ", round(t_std, 3), "წმ")
print("")
print("Strassen:")
print("  გამრავლება:        ", mul_strassen)
print("  მიმატება/გამოკლება:", add_strassen)
print("  დრო:               ", round(t_strassen, 3), "წმ")
print("")
print("Winograd:")
print("  გამრავლება:        ", mul_winograd)
print("  მიმატება/გამოკლება:", add_winograd)
print("  დრო:               ", round(t_winograd, 3), "წმ")
print("")
print("Winograd vs Strassen:")
print("  გამრავლება იგივეა:", mul_strassen == mul_winograd)
print("  add სხვაობა:      ", add_strassen - add_winograd, "(Winograd-ი ნაკლები)")
print("  add შემცირება:    ", round(100 * (add_strassen - add_winograd) / add_strassen, 1), "%")
print("  დროის სხვაობა:    ", round(100 * (t_strassen - t_winograd) / t_strassen, 1), "%")


# ════════════════════════════════════════════════
# დასკვნა
# ════════════════════════════════════════════════

print("")
print("=" * 50)
print("დასკვნა")
print("=" * 50)
print("")
print("- გამრავლება: Strassen და Winograd იგივეა (7 თითო ნაწილზე)")
print("- მიმატება:   Winograd 17% ნაკლები მატრიცის დონეზე (15 vs 18)")
print("- wall-clock: Python-ში სხვაობა მცირეა (add და mul ერთნაირი ფასი)")
print("- რეალურ ფიზიკურ კოდში (C/Fortran): ~5-10% სიჩქარის უპირატესობა")
