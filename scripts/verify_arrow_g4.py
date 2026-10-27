#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 期算据：阿罗定理的三次自由选择。

四组：
  G1 两选项：多数决满足全部公理（证明「3 是紧的」）
  G2 三选项：多数决不传递（Condorcet 循环）
  G3 第二次选择换掉：单峰偏好多数决传递（Black 1948）
  G4 第三次选择的核心——穷举所有 IIA+帕累托+反称的聚合规则，
     看哪些能让社会偏好成为弱序。若只剩独裁型，
     则「独裁」不是被禁止的，是唯一幸存的。

纯标准库。
"""

import itertools

OPTS = "ABC"
VOTERS = 3


def strict_orders():
    return ["".join(p) for p in itertools.permutations(OPTS)]


def prefers(order, x, y):
    """order 里 x 是否排在 y 前。"""
    return order.index(x) < order.index(y)


def majority_winner(profile, x, y):
    votes = sum(1 for o in profile if prefers(o, x, y))
    if votes * 2 > len(profile):
        return x
    if votes * 2 < len(profile):
        return y
    return None  # 平票


def banner(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)


# ------------------------------------------------------------ G1 两选项可行
banner("G1  两选项时，多数决满足全部公理吗")
pairs = list(itertools.product(["A>B", "B>A"], repeat=VOTERS))
print(f"两选项、{VOTERS} 个选民，共 {len(pairs)} 个偏好剖面（每人 A>B 或 B>A）")
viol_p, viol_tr, viol_iia, viol_nd = 0, 0, 0, 0
for prof in pairs:
    w = majority_winner(prof, "A", "B")
    # 帕累托：全体一致则社会一致
    if all(v == "A>B" for v in prof) and w != "A":
        viol_p += 1
    if all(v == "B>A" for v in prof) and w != "B":
        viol_p += 1
    # 传递性：两选项时社会只有 A>B 或 B>A，不存在第三项，天然传递
    # 非独裁：没有任何一个选民的决定恒等于社会决定（除非全体一致）
print(f"帕累托违反：{viol_p} 次")
print("传递性：两选项下社会排序只有两种可能，无第三项可循环 → 恒成立")
print("IIA：只有一对选项，无关选项不存在 → 恒成立")
nd = all(
    not all(
        (prof[i] == "A>B") == (majority_winner(prof, "A", "B") == "A")
        for prof in pairs
    )
    for i in range(VOTERS)
)
print(f"非独裁：不存在某个选民单方面决定结果 → {'成立' if nd else '不成立'}")
print("--> 结论：两选项时多数决同时满足五条。定理里的「至少 3 个选项」是紧的。")

# ------------------------------------------------------------ G2 三选项循环
banner("G2  三选项时，多数决还传递吗")
condorcet = [("A>B>C", "B>C>A", "C>A>B")]
for prof in condorcet:
    print("剖面：" + " | ".join(prof))
    for x, y in [("A", "B"), ("B", "C"), ("A", "C")]:
        w = majority_winner(prof, x, y)
        votes = sum(1 for o in prof if prefers(o, x, y))
        print(f"  {x} vs {y}：{votes} : {VOTERS - votes} → {w} 胜")
print("--> A 胜 B、B 胜 C、C 胜 A。多数决产生循环，不是弱序。")

# ------------------------------------------------------------ G3 单峰
banner("G3  第二次选择换掉：偏好单峰时，多数决可行吗")
# 选项排在 A—B—C 轴上，每人只有唯一峰值
PEAK = {
    "A": ["A>B>C"],
    "B": ["B>A>C", "B>C>A"],
    "C": ["C>B>A"],
}
profiles = []
for peaks in itertools.product("ABC", repeat=VOTERS):
    for combo in itertools.product(*[PEAK[p] for p in peaks]):
        profiles.append(combo)
print(f"单峰偏好剖面：峰值组合 {3 ** VOTERS} 个，计入峰值 B 的两种序，共 {len(profiles)} 个")

bad = 0
for prof in profiles:
    wins = {}
    for x, y in [("A", "B"), ("B", "C"), ("A", "C")]:
        w = majority_winner(prof, x, y)
        if w is None:
            bad += 1
            break
        wins[(x, y)] = w
    else:
        # 传递性检查
        if wins[("A", "B")] == "A" and wins[("B", "C")] == "B" and wins[("A", "C")] != "A":
            bad += 1
        if wins[("B", "C")] == "C" and wins[("A", "B")] == "B" and wins[("A", "C")] != "C":
            bad += 1
print(f"违反传递性或出现平票的剖面：{bad} / {len(profiles)}")
print("--> 单峰偏好下多数决不循环。Black 1948：中位选民的偏好就是社会结果。")
print("    这说明「无限制域」这一条一旦换掉，定理立刻失效。")

# ------------------------------------------------------------ G4 独裁是否唯一
banner("G4  穷举：IIA + 帕累托 + 反称，哪些聚合规则给得出弱序")

# 成对比较的聚合规则 f: {0,1}^3 -> {0,1}
# 每位 = 该选民是否支持 x 胜过 y
# 条件：f(1,1,1)=1（帕累托）、f(~p)=1-f(p)（反称/中立）
# 满足这两条的函数：只需指定「恰有 1 人支持」的 3 种情形，共 2^3=8 个
cands = []
for bits in itertools.product([0, 1], repeat=3):
    def make(bits=bits):
        def f(p):
            k = sum(p)
            if k == 0:
                return 0
            if k == 3:
                return 1
            if k == 1:
                return bits[p.index(1)]
            z = [i for i, v in enumerate(p) if v == 0][0]
            return 1 - bits[z]
        return f
    cands.append((bits, make()))
print(f"候选聚合规则：{len(cands)} 个（已施加帕累托与反称）")

allprof = list(itertools.product(strict_orders(), repeat=VOTERS))
print(f"待检偏好剖面：{len(allprof)} 个\n")

survivors = []
for bits, f in cands:
    ok = True
    for prof in allprof:
        def win(x, y):
            p = tuple(1 if prefers(o, x, y) else 0 for o in prof)
            return f(p) == 1
        # 反对称由反称条件保证；只查传递
        if win("A", "B") and win("B", "C") and not win("A", "C"):
            ok = False
            break
        if win("B", "C") and win("C", "A") and not win("B", "A"):
            ok = False
            break
        if win("C", "A") and win("A", "B") and not win("C", "B"):
            ok = False
            break
    # 识别类型
    if bits == (1, 0, 0):
        name = "独裁者 1（只看选民 1 的意见）"
    elif bits == (0, 1, 0):
        name = "独裁者 2（只看选民 2 的意见）"
    elif bits == (0, 0, 1):
        name = "独裁者 3（只看选民 3 的意见）"
    elif bits == (0, 0, 0):
        name = "多数决"
    else:
        name = f"其他加权规则 bits={bits}"
    flag = "通过" if ok else "失败"
    if bits in [(0, 0, 0)]:
        flag += "（三选项下产生 Condorcet 循环）"
    print(f"  {name:<32} {flag}")
    if ok:
        survivors.append(name)

print(f"\n--> 能给出弱序的规则：{len(survivors)} 个")
for s in survivors:
    print(f"    · {s}")
print("--> 全部是独裁型。独裁不是被公理排斥掉的坏东西，是唯一留下来的解。")

# ------------------------------------------------------------ 结论
banner("结论")
print("G1  两选项：五条全满足 → 定理的「至少 3 个选项」是紧的")
print("G2  三选项：多数决循环 → 传递性失守")
print("G3  单峰偏好：多数决可行 → 换掉「无限制域」，定理失效")
print("G4  穷举 8 个候选规则，唯一通过传递性检验的是 3 个独裁型")
print("    → 独裁是唯一幸存解，不是被排除项")
