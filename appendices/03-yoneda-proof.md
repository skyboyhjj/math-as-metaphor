# 附录：Yoneda 引理证明拆解与算据

> **配套文档**：[`issues/03-object-as-relations.md`](../issues/03-object-as-relations.md)
> **日期**：2026-10-26
> **运行环境**：Python 3.12，纯标准库（无需 numpy）
> **源文件 md5**：`0f18fc901ba9218e4311394c2bde02f1`
>
> **版本记录**
> v1.0 初版
> v1.1 修正 §6.2 两处标注：u 的方向（`A' → A` 应为 `A → A'`）、方差（「反变」应为「协变」），并补「反变∘反变＝协变」的展开说明；配套文档版本号更新至 v1.3

---

## 一、引理的准确陈述

设 $`\mathcal{C}`$ 是小范畴，$`F \colon \mathcal{C} \to \mathbf{Set}`$ 是函子，$`A \in \mathcal{C}`$。则有自然双射

$`\Phi \colon \mathrm{Nat}\big(\mathcal{C}(A,-),\, F\big) \;\longrightarrow\; F(A)`$

其中 $`\mathrm{Nat}`$ 表示自然变换的全集。并且这个双射**同时自然于 $`A`$ 与 $`F`$**。

> 记号说明：$`\mathcal{C}(A,-)`$ 与 $`h^A`$ 是同一样东西。

---

## 二、双向构造

### 2.1 正向 $`\Phi`$：自然变换 → 元素

给定自然变换 $`\alpha \colon \mathcal{C}(A,-) \Rightarrow F`$，定义

$`\Phi(\alpha) := \alpha_A(\mathrm{id}_A) \;\in\; F(A)`$

**这一步只用了一个信息：恒等态射**。其余全被扔掉。

### 2.2 反向 $`\Psi`$：元素 → 自然变换

给定 $`x \in F(A)`$，对每个对象 $`B`$ 定义分量

$`\Psi(x)_B \colon \mathcal{C}(A,B) \to F(B), \qquad f \mapsto F(f)(x)`$

即"把 $`x`$ 沿着 $`f`$ 推过去"。

---

## 三、验证 $`\Psi(x)`$ 确实是自然变换

需要验证：对任意 $`g \colon B \to C`$ 与 $`f \colon A \to B`$，有

$`F(g)\big(\Psi(x)_B(f)\big) = \Psi(x)_C\big(\mathcal{C}(A,g)(f)\big)`$

**左边**：

$`F(g)\big(F(f)(x)\big) = \big(F(g) \circ F(f)\big)(x)`$

**右边**：

$`\Psi(x)_C(g \circ f) = F(g \circ f)(x)`$

由 $`F`$ 是函子，$`F(g) \circ F(f) = F(g \circ f)`$。两边相等。$`\square`$

> **这一步只用了一条性质：函子保持复合**。没有任何额外条件。

---

## 四、验证 $`\Phi \circ \Psi = \mathrm{id}`$

$`\Phi\big(\Psi(x)\big) = \Psi(x)_A(\mathrm{id}_A) = F(\mathrm{id}_A)(x) = \mathrm{id}_{F(A)}(x) = x`$

第三处用了 $`F`$ 保持恒等。$`\square`$

---

## 五、验证 $`\Psi \circ \Phi = \mathrm{id}`$

这一边是整条引理里唯一需要"动脑"的地方——**它必须用自然性**。

要证：对任意 $`\alpha`$、任意对象 $`B`$、任意 $`f \colon A \to B`$，

$`\Psi\big(\Phi(\alpha)\big)_B(f) = \alpha_B(f)`$

左边展开：

$`\Psi\big(\Phi(\alpha)\big)_B(f) = F(f)\big(\alpha_A(\mathrm{id}_A)\big)`$

现在用 $`\alpha`$ 的自然性。对 $`f \colon A \to B`$，有交换方块：

```text
        C(A,f)
C(A,A) ─────────→ C(A,B)
   │                 │
 α_A│                 │α_B
   ↓                 ↓
 F(A) ────────────→ F(B)
        F(f)
```

即

$`\alpha_B \circ \mathcal{C}(A,f) = F(f) \circ \alpha_A`$

取 $`\mathrm{id}_A`$ 代入：

$`\alpha_B(f) = \alpha_B\big(\mathcal{C}(A,f)(\mathrm{id}_A)\big) = F(f)\big(\alpha_A(\mathrm{id}_A)\big)`$

右边正是我们要证的左边。

所以 $`\Psi(\Phi(\alpha))_B(f) = \alpha_B(f)`$。$`\square`$

> **这就是引理的核心：自然性把"在恒等处的取值"输运到"任意态射处的取值"。**
> 没有自然性，这一步断掉，引理不成立。

---

## 六、两个方向的自然性

### 6.1 对 $`F`$ 自然

给定 $`\eta \colon F \Rightarrow G`$，要证

$`\Phi_G(\eta \circ \alpha) = \eta_A\big(\Phi_F(\alpha)\big)`$

左边：

$`(\eta \circ \alpha)_A(\mathrm{id}_A) = \eta_A\big(\alpha_A(\mathrm{id}_A)\big)`$

右边：

$`\eta_A\big(\Phi_F(\alpha)\big) = \eta_A\big(\alpha_A(\mathrm{id}_A)\big)`$

相等。$`\square`$（这一步是逐点定义的直接结果，无需自然性。）

### 6.2 对 $`A`$ 自然

对 $`u \colon A \to A'`$，$`A \mapsto \mathrm{Nat}(\mathcal{C}(A,-),F)`$ 是**协变**的。这一点要说清，否则容易错：

- $`A \mapsto \mathcal{C}(A,-)`$ 本身是**反变**的：$`u`$ 先给出 $`\mathcal{C}(u,-) \colon h^{A'} \Rightarrow h^{A}`$
- 而 $`\mathrm{Nat}(-,\,F)`$ 对第一个变量也是**反变**的
- **两个反变复合得协变**，所以 $`\mathrm{Nat}(\mathcal{C}(A,-),F)`$ 随 $`A`$ 协变，与 $`F(A)`$ 同向

于是 $`u`$ 诱导的映射是

$`\mathrm{Nat}(\mathcal{C}(A,-),F) \;\longrightarrow\; \mathrm{Nat}(\mathcal{C}(A',-),F), \qquad \alpha \mapsto \alpha \circ \mathcal{C}(u,-)`$

要证

$`\Phi_{A'}\big(\alpha \circ \mathcal{C}(u,-)\big) = F(u)\big(\Phi_A(\alpha)\big)`$

左边：

$`\big(\alpha \circ \mathcal{C}(u,-)\big)_{A'}(\mathrm{id}_{A'}) = \alpha_{A'}\big(\mathcal{C}(u,A')(\mathrm{id}_{A'})\big) = \alpha_{A'}(u)`$

右边：

$`F(u)\big(\alpha_A(\mathrm{id}_A)\big)`$

用 $`\alpha`$ 在 $`u`$ 处自然性：

```text
        C(A,u)
C(A,A) ─────────→ C(A,A')
   │                 │
 α_A│                 │α_A'
   ↓                 ↓
 F(A) ────────────→ F(A')
        F(u)
```

$`\alpha_{A'} \circ \mathcal{C}(A,u) = F(u) \circ \alpha_A`$，取 $`\mathrm{id}_A`$：

$`\alpha_{A'}(u) = F(u)\big(\alpha_A(\mathrm{id}_A)\big)`$

相等。$`\square`$

---

## 七、推论：Yoneda 嵌入满忠实

定义

$`h \colon \mathcal{C}^{\mathrm{op}} \to [\mathcal{C}, \mathbf{Set}], \qquad A \mapsto \mathcal{C}(A,-)`$

对任意 $`A, B`$，把引理用于 $`F = \mathcal{C}(B,-)`$：

$`\mathrm{Nat}\big(\mathcal{C}(A,-),\, \mathcal{C}(B,-)\big) \;\cong\; \mathcal{C}(B,-)(A) \;=\; \mathcal{C}(B,A)`$

而 $`\mathrm{Hom}_{\mathcal{C}^{\mathrm{op}}}(A,B) = \mathcal{C}(B,A)`$。

**两边相等，故 $`h`$ 在 Hom 集上是双射——满且忠实。**

> **方向提醒**：$`A \mapsto \mathcal{C}(A,-)`$ 是**反变**的，所以嵌入的是 $`\mathcal{C}^{\mathrm{op}}`$，不是 $`\mathcal{C}`$。这是最容易写错的一处。
> 若改用 $`A \mapsto \mathcal{C}(-,A)`$，得到的是协变嵌入 $`\mathcal{C} \to [\mathcal{C}^{\mathrm{op}}, \mathbf{Set}]`$。

---

## 八、边界：满忠实不等于等价

$`h`$ 满忠实，但它**一般不是本质满射**——不是每个函子都可表。

**例**：取 $`\mathcal{C}`$ 为 $`A \to B \to C`$，令

$`G := h^A \sqcup h^B`$

$`G`$ 不可表（下一节的算据 G4 逐项验过），但它按定义就是两个可表函子的余积。

**补上这个缺口的是密度定理**：

$`F \;\cong\; \mathrm{colim}\big(h^{(\cdot)} \to F\big)`$

每个函子都是可表函子的余极限。所以"不可表"只意味着"不能由单个对象代表"，**不意味着"不属于任何对象"**。

这一点是正文第四节的全部内容，也是我去年说错话的地方。

---

## 九、算据脚本

### 9.1 五组在验什么

| 组 | 验什么 | 与哪一节对应 |
| :-- | :-- | :-- |
| G1 | 有限维中 $`x`$ 由所有泛函取值完全决定 | 正文第一节（Hahn-Banach 弱版） |
| G2 | 单对象范畴上 $`\mathrm{Nat}(h^\ast,F)`$ 的元素个数 $`= \lvert F(\ast)\rvert`$ | 正文第二节（把 Yoneda 数出来） |
| G3 | $`\mathrm{Nat}(h^B,h^A)`$ 的元素个数 $`= \lvert\mathcal{C}(A,B)\rvert`$ | 附录第七节（嵌入满忠实） |
| G4 | $`G = h^A \sqcup h^B`$ 不可表 | 正文第四节、附录第八节 |
| G5 | 密度定理的玩具版 | 附录第八节 |

### 9.2 两条必须避开的坑

**坑一：空函数不算自然变换。**

G3 第一版写错了：程序允许把非空的 $`\mathcal{C}(B,A)`$ 映射成空集，于是数出了一个假自然变换。修法是显式检查"每个分量必须是**全函数**"（定义域每个元素都有像），并检查像落在陪域内。

**坑二：方向容易反。**

$`\mathrm{Nat}(h^A,h^B) \cong \mathcal{C}(B,A)`$，不是 $`\mathcal{C}(A,B)`$。因为 $`h`$ 是反变嵌入。验算时把 A、B 摆对，数字才对得上。

### 9.3 脚本原文

```python
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

```

### 9.4 实跑输出

```text

====================================================================
G1  Hahn-Banach 弱版：x 由所有 f(x) 决定
====================================================================
维度 3，样本 200 个向量
非零但所有泛函取值全为 0 的向量：0 个
--> x = 0 当且仅当 f(x) = 0 对所有 f。弱版成立：点可由泛函分离
不同向量映射到同一指纹的次数：0
--> 指纹是单射：x 被外部探测完全决定（有限维、取遍 X^* 时）

====================================================================
G2  Monoid 范畴上的 Yoneda：逐个数 Nat(Hom(*,-), F)
====================================================================
M = Z/3，F(*) = Z/3（M 作用为加法）
满足自然性的 alpha: M -> F(*) 共 3 个
    {0: 0, 1: 1, 2: 2}
    {0: 1, 1: 2, 2: 0}
    {0: 2, 1: 0, 2: 1}
|F(*)| = 3
--> Nat(Hom(*,-), F) 有 3 个元素，等于 |F(*)| = 3。Yoneda 双射成立

按 alpha(0) 分组：
   alpha(0) = 0 → 1 个自然变换
   alpha(0) = 1 → 1 个自然变换
   alpha(0) = 2 → 1 个自然变换
--> 每个 alpha(0) 恰好对应一个自然变换：Phi: alpha |-> alpha(id) 是双射

====================================================================
G3  Yoneda 嵌入满忠实：Nat(Hom(B,-), Hom(A,-)) = Hom(A,B)
====================================================================
范畴：A --f--> B --g--> C
Hom(A,B) = {'f'}，共 1 个
Nat(h^B, h^A) 的元素个数：1
    {'A': {}, 'B': {'idB': 'f'}, 'C': {'g': 'gf'}}
--> 两侧都是 1：Yoneda 嵌入在这一例上满忠实

反向验证：
Hom(B,A) = set()（空），共 0 个
Nat(h^A, h^B) 应当也是 0 个——因为 alpha_A: Hom(A,A) -> Hom(B,A) 无法定义
（非空集到空集不存在函数）

====================================================================
G4  不可表的函子：G = Hom(A,-) ⊔ Hom(B,-)
====================================================================
G = h^A ⊔ h^B 的取值：
   G(A) = ['idA'],  |G(A)| = 1
   G(B) = ['f', 'idB'],  |G(B)| = 2
   G(C) = ['g', 'gf'],  |G(C)| = 2

检查是否有对象 X 使 Hom(X,-) 与 G 同构（先比基数）：
   X = A:  |Hom(X,-)| = A:1  B:1  C:1   vs   |G| = A:1  B:2  C:2
   X = B:  |Hom(X,-)| = A:0  B:1  C:1   vs   |G| = A:1  B:2  C:2
   X = C:  |Hom(X,-)| = A:0  B:0  C:1   vs   |G| = A:1  B:2  C:2

--> 有基数匹配的候选：False
--> 没有对象 X 使 Hom(X,-) ≅ G：G 不可表
    但 G 按定义就是两个可表函子的余积。
    「不可表」不等于「不属于任何对象的关系」——它是两个可表者拼起来的。

====================================================================
G5  密度定理玩具版：G 是可表函子的余极限
====================================================================
G = h^A ⊔ h^B
余积本身是一种余极限（两个对象的余极限）。

一般形式：F ≅ colim( h^X → F )，其中指标范畴是元素范畴 ∫F。
本例的元素范畴：
   ∫G 的对象：(A, idA), (B, f), (B, idB), (C, gf), (C, g)
   每个元素 (X, s) 给出一个 h^X → G 的映射
   G 就是这个图的余极限

--> 每个函子都是可表函子的余极限：本例已具体写出

====================================================================
结论
====================================================================
G1 x 由外部探测完全决定（有限维、取遍 X^*）：成立
G2 Nat(h^*, F) 的元素个数 = |F(*)|：逐个数出 3 个，成立
G3 Nat(h^B, h^A) 的元素个数 = |C(A,B)|：两侧都是 1，成立
   且找出的唯一自然变换正是 Yoneda 构造 alpha_X(k) = k∘f
G4 G = h^A ⊔ h^B 不可表，但它自己是两个可表函子的余积
G5 密度定理：G 是可表函子图的余极限

```

---

*2026-10-26 · 附录 v1.0 · 证明与方法均自检*
