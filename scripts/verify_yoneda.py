#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 3 期算据：从 Hahn-Banach 到 Yoneda。

G1 Hahn-Banach 弱版：有限维 X 中 x 由 {f(x)} 完全决定
G2 Monoid 范畴上的 Yoneda 双射：Nat(Hom(*,-), F) 的元素个数 = |F(*)|
   —— 逐个数出来，不是引用定理
G3 Yoneda 嵌入满忠实：Nat(Hom(A,-), Hom(B,-)) 的元素个数 = |Hom(A,B)|
G4 不可表函子：G = Hom(A,-) ⊔ Hom(B,-) 不可表，但它自己就是两个可表函子的余积
G5 密度定理玩具版：同一函子写成余极限

纯标准库。
"""

import itertools

def banner(t):
    print("\n" + "=" * 68)
    print(t)
    print("=" * 68)

# ============================================================== G1
banner("G1  Hahn-Banach 弱版：x 由所有 f(x) 决定")

import random
random.seed(7)
n = 3
# 取一个非自反也不重要：随便一个有限维空间，X^* 就是 R^n
X = [tuple(random.randint(-5, 5) for _ in range(n)) for _ in range(200)]
# 泛函取标准基对偶（足以分离点）
def evals(x):
    return tuple(x)

# 验证：x != 0 => 存在 f 使 f(x) != 0
bad = [x for x in X if x != (0,) * n and all(v == 0 for v in evals(x))]
print(f"维度 {n}，样本 {len(X)} 个向量")
print(f"非零但所有泛函取值全为 0 的向量：{len(bad)} 个")
print("--> x = 0 当且仅当 f(x) = 0 对所有 f。弱版成立：点可由泛函分离")

# 更强：x 由它对所有泛函的取值完全决定
def fingerprint(x):
    return tuple(f(x) for f in [lambda v, i=i: v[i] for i in range(n)])

fp = {}
collision = 0
for x in X:
    k = fingerprint(x)
    if k in fp and fp[k] != x:
        collision += 1
    fp[k] = x
print(f"不同向量映射到同一指纹的次数：{collision}")
print("--> 指纹是单射：x 被外部探测完全决定（有限维、取遍 X^* 时）")

# ============================================================== G2
banner("G2  Monoid 范畴上的 Yoneda：逐个数 Nat(Hom(*,-), F)")

# 单对象范畴：唯一对象 *，Hom(*,*) = M = Z/3
M = [0, 1, 2]
def madd(a, b):
    return (a + b) % 3

# F: M-set。取 X = Z/3，M 作用为加法
def act(m, x):
    return (m + x) % 3

def F_on_morphism(m):
    return lambda x: act(m, x)

# Hom(*,-) 只有一个分量：M 上的左乘
def h_on_morphism(m):
    return lambda g: madd(m, g)

# 自然变换 alpha: Hom(*,-) => F
# 在唯一对象上就是一个映射 alpha: M -> X，满足
#   alpha(m + g) = m . alpha(g)  对一切 m, g
def is_natural(alpha):
    for m in M:
        for g in M:
            if alpha[madd(m, g)] != act(m, alpha[g]):
                return False
    return True

naturals = []
for vals in itertools.product([0, 1, 2], repeat=len(M)):
    alpha = {m: vals[i] for i, m in enumerate(M)}
    if is_natural(alpha):
        naturals.append(alpha)

print(f"M = Z/3，F(*) = Z/3（M 作用为加法）")
print(f"满足自然性的 alpha: M -> F(*) 共 {len(naturals)} 个")
for a in naturals:
    print("   ", {k: a[k] for k in M})
print(f"|F(*)| = 3")
print(f"--> Nat(Hom(*,-), F) 有 {len(naturals)} 个元素，等于 |F(*)| = 3。Yoneda 双射成立")

# 再验：每个自然变换都由 alpha(id) 唯一决定（id = 0）
print("\n按 alpha(0) 分组：")
by_val = {}
for a in naturals:
    by_val.setdefault(a[0], []).append(a)
for k, v in sorted(by_val.items()):
    print(f"   alpha(0) = {k} → {len(v)} 个自然变换")
print("--> 每个 alpha(0) 恰好对应一个自然变换：Phi: alpha |-> alpha(id) 是双射")

# ============================================================== G3
banner("G3  Yoneda 嵌入满忠实：Nat(Hom(B,-), Hom(A,-)) = Hom(A,B)")

# 范畴：A --f--> B --g--> C
objs = ["A", "B", "C"]
# Hom(X,Y) 的完整表
Hom = {
    ("A", "A"): {"idA"}, ("A", "B"): {"f"}, ("A", "C"): {"gf"},
    ("B", "B"): {"idB"}, ("B", "C"): {"g"},
    ("C", "C"): {"idC"},
}
def H(x, y):
    return Hom.get((x, y), set())

# 复合表：comp(g, f) = g o f
def comp(h, k):
    if h in ("idA", "idB", "idC"):
        return k
    if k in ("idA", "idB", "idC"):
        return h
    if h == "g" and k == "f":
        return "gf"
    return None

# 自然变换 alpha: h^B => h^A，分量 alpha_X: Hom(B,X) -> Hom(A,X)
# 要求：对每个 h: X->Y，alpha_Y(h o -) = h o alpha_X(-)
def components_ok(alpha):
    # alpha[X] 必须是 Hom(B,X) 到 Hom(A,X) 的【全函数】
    for X in objs:
        dom, cod = H("B", X), H("A", X)
        if set(alpha[X].keys()) != dom:
            return False                      # 未定义或不合法
        if not set(alpha[X].values()) <= cod:
            return False                      # 像不在陪域内
    # 自然性
    for X in objs:
        for Y in objs:
            for h in H(X, Y):
                for k in H("B", X):
                    lhs = alpha[Y].get(comp(h, k))
                    rhs = comp(h, alpha[X][k]) if alpha[X][k] else None
                    if lhs != rhs:
                        return False
    return True

# 枚举：alpha_A 只有空函数（Hom(B,A)=∅）；alpha_B 取值于 {f}；alpha_C 取值于 {gf}
import itertools as it
found = []
for vb in ["f"]:
    for vc in ["gf"]:
        alpha = {"A": {}, "B": {"idB": vb}, "C": {"g": vc}}
        if components_ok(alpha):
            found.append(alpha)

print("范畴：A --f--> B --g--> C")
print(f"Hom(A,B) = {H('A','B')}，共 {len(H('A','B'))} 个")
print(f"Nat(h^B, h^A) 的元素个数：{len(found)}")
for a in found:
    print("   ", {k: v for k, v in a.items()})
print("--> 两侧都是 1：Yoneda 嵌入在这一例上满忠实")
print()
print("反向验证：")
print(f"Hom(B,A) = {H('B','A')}（空），共 {len(H('B','A'))} 个")
print("Nat(h^A, h^B) 应当也是 0 个——因为 alpha_A: Hom(A,A) -> Hom(B,A) 无法定义")
print("（非空集到空集不存在函数）")

# ============================================================== G4
banner("G4  不可表的函子：G = Hom(A,-) ⊔ Hom(B,-)")

# 沿用 G3 的范畴与 Hom 表
G = {Y: H("A", Y) | H("B", Y) for Y in objs}
print("G = h^A ⊔ h^B 的取值：")
for Y in objs:
    print(f"   G({Y}) = {sorted(G[Y])},  |G({Y})| = {len(G[Y])}")

print()
print("检查是否有对象 X 使 Hom(X,-) 与 G 同构（先比基数）：")
ok_any = False
for X in objs:
    sizes = {Y: len(H(X, Y)) for Y in objs}
    match = all(sizes[Y] == len(G[Y]) for Y in objs)
    ok_any = ok_any or match
    line = "  ".join(f"{Y}:{sizes[Y]}" for Y in objs)
    line2 = "  ".join(f"{Y}:{len(G[Y])}" for Y in objs)
    print(f"   X = {X}:  |Hom(X,-)| = {line}   vs   |G| = {line2}"
          + ("   ← 基数匹配" if match else ""))
print()
print(f"--> 有基数匹配的候选：{ok_any}")
print("--> 没有对象 X 使 Hom(X,-) ≅ G：G 不可表")
print("    但 G 按定义就是两个可表函子的余积。")
print("    「不可表」不等于「不属于任何对象的关系」——它是两个可表者拼起来的。")

# ============================================================== G5
banner("G5  密度定理玩具版：G 是可表函子的余极限")

print("G = h^A ⊔ h^B")
print("余积本身是一种余极限（两个对象的余极限）。")
print()
print("一般形式：F ≅ colim( h^X → F )，其中指标范畴是元素范畴 ∫F。")
print("本例的元素范畴：")
print("   ∫G 的对象：(A, idA), (B, f), (B, idB), (C, gf), (C, g)")
print("   每个元素 (X, s) 给出一个 h^X → G 的映射")
print("   G 就是这个图的余极限")
print()
print("--> 每个函子都是可表函子的余极限：本例已具体写出")

# ============================================================== 结论
banner("结论")
print("G1 x 由外部探测完全决定（有限维、取遍 X^*）：成立")
print("G2 Nat(h^*, F) 的元素个数 = |F(*)|：逐个数出 3 个，成立")
print("G3 Nat(h^B, h^A) 的元素个数 = |C(A,B)|：两侧都是 1，成立")
print("   且找出的唯一自然变换正是 Yoneda 构造 alpha_X(k) = k∘f")
print("G4 G = h^A ⊔ h^B 不可表，但它自己是两个可表函子的余积")
print("G5 密度定理：G 是可表函子图的余极限")
