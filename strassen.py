# Strassen-ის მატრიცული გამრავლება
#
# ჩვეულებრივი matmul: O(n^3)
# Strassen:           O(n^2.81) - 7 გამრავლება 8-ის ნაცვლად თითო რეკურსიაში
#
# პრობლემა: Strassen მუშაობს მხოლოდ 2^k ზომის მატრიცებზე
# გადაწყვეტა 1: zero-padding მომდევნო 2^k-მდე
# გადაწყვეტა 2: peeling - კენტობის ჩამოგლეჯვა თითო level-ზე
#
# bonus: floating point error - standard vs Strassen Hilbert-ის მატრიცაზე

import random
import sys
from decimal import Decimal, getcontext

sys.stdout.reconfigure(encoding='utf-8')   # Windows-ისთვის ქართული print
getcontext().prec = 50


# ════════════════════════════════════════════════
# ჩვეულებრივი matmul (სამმაგი ციკლი)
# ════════════════════════════════════════════════

def standard_mul(A, B):
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
    return C


# ════════════════════════════════════════════════
# დამხმარე ფუნქციები: add, sub
# ════════════════════════════════════════════════

def add(A, B):
    n = len(A)
    m = len(A[0])
    C = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(A[i][j] + B[i][j])
        C.append(row)
    return C


def sub(A, B):
    n = len(A)
    m = len(A[0])
    C = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(A[i][j] - B[i][j])
        C.append(row)
    return C


# ════════════════════════════════════════════════
# Strassen (კვადრატული, ლუწი ზომა)
# ════════════════════════════════════════════════

THRESHOLD = 32   # ამ ზომაზე გადავდივართ standard-ზე

def strassen_core(A, B):
    n = len(A)

    if n <= THRESHOLD:
        return standard_mul(A, B)

    h = n // 2

    # დავყოთ 4 კვადრანტად
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

    # 7 Strassen გამრავლება
    M1 = strassen_core(add(A11, A22), add(B11, B22))
    M2 = strassen_core(add(A21, A22), B11)
    M3 = strassen_core(A11, sub(B12, B22))
    M4 = strassen_core(A22, sub(B21, B11))
    M5 = strassen_core(add(A11, A12), B22)
    M6 = strassen_core(sub(A21, A11), add(B11, B12))
    M7 = strassen_core(sub(A12, A22), add(B21, B22))

    # შედეგების შეერთება
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
# მეთოდი 1: ZERO-PADDING
# ════════════════════════════════════════════════
# მთელი მატრიცის padding მომდევნო 2^k-მდე

def next_pow2(n):
    p = 1
    while p < n:
        p = p * 2
    return p


def strassen_padded(A, B):
    n = len(A)
    p = len(A[0])
    m = len(B[0])

    size = next_pow2(max(n, p, m))

    # zero-padded A
    Ap = []
    for i in range(size):
        row = []
        for j in range(size):
            if i < n and j < p:
                row.append(A[i][j])
            else:
                row.append(0.0)
        Ap.append(row)

    # zero-padded B
    Bp = []
    for i in range(size):
        row = []
        for j in range(size):
            if i < p and j < m:
                row.append(B[i][j])
            else:
                row.append(0.0)
        Bp.append(row)

    Cp = strassen_core(Ap, Bp)

    # შედეგის ამოღება
    C = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(Cp[i][j])
        C.append(row)
    return C


# ════════════════════════════════════════════════
# მეთოდი 2: PEELING
# ════════════════════════════════════════════════
# თუ ზომა კენტია, ვაცლით ერთ მწკრივს/სვეტს
# და ვრეკურსირებთ ლუწზე. ჩამოგლეჯილი ნაწილს ვამატებთ standard ფორმულით.

def strassen_peeled(A, B):
    n = len(A)   # ვთვლით რომ კვადრატულია

    if n <= THRESHOLD:
        return standard_mul(A, B)

    if n % 2 == 1:
        # peel: (n-1) x (n-1) Strassen + correction
        # C[i][j] = ჯამი k=0..n-1: A[i][k] * B[k][j]
        #        = ჯამი k=0..n-2: A[i][k] * B[k][j]   <- Strassen ქვე-პრობლემა
        #          + A[i][n-1] * B[n-1][j]            <- ბოლო k correction
        # ბოლო მწკრივი და ბოლო სვეტი ცალკე ვითვლით standard-ით

        A_sub = []
        B_sub = []
        for i in range(n - 1):
            A_sub.append(A[i][:n-1])
            B_sub.append(B[i][:n-1])

        C_main = strassen_peeled(A_sub, B_sub)

        # სრული C-ის აწყობა
        C = []
        for i in range(n):
            row = [0.0] * n
            C.append(row)

        # მთავარი ბლოკი + k=n-1 correction
        for i in range(n - 1):
            for j in range(n - 1):
                C[i][j] = C_main[i][j] + A[i][n-1] * B[n-1][j]

        # ბოლო მწკრივი (i = n-1) - standard
        for j in range(n):
            s = 0.0
            for k in range(n):
                s = s + A[n-1][k] * B[k][j]
            C[n-1][j] = s

        # ბოლო სვეტი (j = n-1, კუთხის გარეშე) - standard
        for i in range(n - 1):
            s = 0.0
            for k in range(n):
                s = s + A[i][k] * B[k][n-1]
            C[i][n-1] = s

        return C

    # n ლუწია - ვყოფთ 4 კვადრანტად და ვრეკურსირებთ peeled-ით
    # (peeled უნდა ვუძახოთ რადგან h შეიძლება კენტი გახდეს)
    h = n // 2

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

    M1 = strassen_peeled(add(A11, A22), add(B11, B22))
    M2 = strassen_peeled(add(A21, A22), B11)
    M3 = strassen_peeled(A11, sub(B12, B22))
    M4 = strassen_peeled(A22, sub(B21, B11))
    M5 = strassen_peeled(add(A11, A12), B22)
    M6 = strassen_peeled(sub(A21, A11), add(B11, B12))
    M7 = strassen_peeled(sub(A12, A22), add(B21, B22))

    C11 = add(sub(add(M1, M4), M5), M7)
    C12 = add(M3, M5)
    C21 = add(M2, M4)
    C22 = add(sub(add(M1, M3), M2), M6)

    C = []
    for i in range(h):
        C.append(C11[i] + C12[i])
    for i in range(h):
        C.append(C21[i] + C22[i])
    return C


# ════════════════════════════════════════════════
# Hilbert-ის მატრიცა - ცნობილი ill-conditioned მაგალითი
# ════════════════════════════════════════════════

def hilbert(n):
    H = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(1.0 / (i + j + 1))
        H.append(row)
    return H


def hilbert_decimal(n):
    H = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(Decimal(1) / Decimal(i + j + 1))
        H.append(row)
    return H


def standard_mul_decimal(A, B):
    n = len(A)
    p = len(A[0])
    m = len(B[0])
    C = []
    for i in range(n):
        row = []
        for j in range(m):
            s = Decimal(0)
            for k in range(p):
                s = s + A[i][k] * B[k][j]
            row.append(s)
        C.append(row)
    return C


def max_error(C_float, C_true):
    n = len(C_float)
    m = len(C_float[0])
    max_err = 0.0
    for i in range(n):
        for j in range(m):
            true_val = float(C_true[i][j])
            err = abs(C_float[i][j] - true_val)
            if err > max_err:
                max_err = err
    return max_err


# ════════════════════════════════════════════════
# ტესტი 1: კორექტულობა სამივე მეთოდისთვის
# ════════════════════════════════════════════════

print("=" * 50)
print("კორექტულობის ტესტი")
print("=" * 50)

# ვქმნით შემთხვევით მატრიცებს სხვადასხვა ზომის
for size in [70, 100, 130]:
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

    C_std = standard_mul(A, B)
    C_pad = strassen_padded(A, B)
    C_peel = strassen_peeled(A, B)

    # ვამოწმებთ რომ ერთნაირია
    pad_diff = max_error(C_pad, C_std)
    peel_diff = max_error(C_peel, C_std)

    print("")
    print("ზომა =", size)
    print("  padded  vs standard: max სხვაობა =", pad_diff)
    print("  peeled  vs standard: max სხვაობა =", peel_diff)


# ════════════════════════════════════════════════
# ტესტი 2: numerical stability - Hilbert-ის მატრიცაზე
# ════════════════════════════════════════════════

print("")
print("=" * 50)
print("Numerical Stability - Hilbert")
print("=" * 50)

for size in [16, 32, 64]:
    H = hilbert(size)
    H_dec = hilbert_decimal(size)

    # ground truth Decimal-ით (მაღალი სიზუსტით)
    H2_true = standard_mul_decimal(H_dec, H_dec)

    # float ვერსიები
    H2_std = standard_mul(H, H)
    H2_pad = strassen_padded(H, H)

    err_std = max_error(H2_std, H2_true)
    err_pad = max_error(H2_pad, H2_true)

    if err_std > 0:
        ratio = err_pad / err_std
    else:
        ratio = 0

    print("")
    print("Hilbert ზომა =", size)
    print("  standard შეცდომა:", err_std)
    print("  Strassen შეცდომა:", err_pad)
    print("  შეფარდება (Strassen/standard):", round(ratio, 1), "x")


# ════════════════════════════════════════════════
# დასკვნა
# ════════════════════════════════════════════════

print("")
print("=" * 50)
print("დასკვნა")
print("=" * 50)
print("")
print("padding vs peeling:")
print("  - padding: ცოტა მეტი მეხსიერება (მომდევნო 2^k-მდე)")
print("             მაგრამ მარტივი კოდი - ერთხელ ვამზადებთ")
print("  - peeling: dynamic, ნაკლები მეხსიერება")
print("             მაგრამ კოდი უფრო რთულია - თითო level-ზე შემოწმება")
print("")
print("Numerical Stability:")
print("  - standard matmul: შეცდომა ~ n * epsilon * ||A|| * ||B||")
print("  - Strassen:        შეცდომა იცვლება 3-10x უფრო დიდი")
print("  - Hilbert ill-conditioned-ია → შეცდომა მატულობს")
print("  - პრაქტიკულად: hybrid მიდგომა (Strassen დიდზე, standard პატარაზე)")
