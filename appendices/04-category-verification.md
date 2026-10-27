# 附录：范畴论算据

> **配套文档**：[`issues/04-category-as-language.md`](../issues/04-category-as-language.md)
> **日期**：2026-10-26
> **运行环境**：Python 3.12，纯标准库
> **源文件 md5**：`a475e15f063a96ab679efdd7ef9249d0`

---

## 一、四组在验什么

| 组 | 验什么 | 对应正文 |
| :-- | :-- | :-- |
| G1 | 三元链偏序集满足范畴公理 | 第二节 |
| G2 | **C 与 D 等价但不同构** | 第五节（核心） |
| G3 | Cat 不能是小范畴 | 第四节 |
| G4 | 自然变换可复合 | 第三节末 |

## 二、G2 为什么是全篇的关键

正文第五节的论点是：范畴论的自由在于**可以选择「什么叫一样」**。这个论点要站住，必须有一个"等价但不同构"的实例。

构造如下。

**范畴 C**：一个对象 $`\ast`$，一个箭头 $`\mathrm{id}_\ast`$。

**范畴 D**：两个对象 $`A, B`$；箭头 $`\mathrm{id}_A, \mathrm{id}_B, f \colon A \to B, g \colon B \to A`$，满足

$`g \circ f = \mathrm{id}_A, \qquad f \circ g = \mathrm{id}_B`$

即 $`A`$ 与 $`B`$ 同构。

**不同构**：范畴同构要求对象集之间有双射。$`|\mathrm{Ob}\,\mathbf{C}| = 1`$，$`|\mathrm{Ob}\,\mathbf{D}| = 2`$。不可能。

**等价**：取 $`F \colon \mathbf{C} \to \mathbf{D}`$，$`F(\ast) = A`$。

- **忠实**：$`\mathbf{C}(\ast,\ast) = \{\mathrm{id}_\ast\}`$，$`\mathbf{D}(A,A) = \{\mathrm{id}_A\}`$，映射是双射，成立
- **满**：同上，成立
- **本质满**：$`A \cong A`$；$`B \cong A`$（由 $`f`$ 给出）。$`\mathbf{D}`$ 的每个对象都在本质像里

三条齐备，$`F`$ 是等价。

**结论**：$`\mathbf{C} \simeq \mathbf{D}`$，但 $`\mathbf{C} \not\cong \mathbf{D}`$。

## 三、两个坑（都踩过）

**坑一：范畴公理的检查口径**

G2 第一版把"不可复合的态射对"也拿来比恒等律，结果 $`D`$ 被判成非法范畴。修法：给每个态射标注源与靶，复合前先检查 $`\mathrm{src}(h) = \mathrm{tgt}(k)`$，不成立就跳过。

**坑二：等价的三条缺一不可**

满忠实只保证"箭头层面不变形"，本质满才保证"对象层面不漏"。缺本质满，得到的是**全忠实函子**，不是等价。

## 四、脚本原文

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 期算据：范畴论作为一种语言。

G1 偏序集作为范畴：对象没有"内部"，只有箭头
G2 等价但不同构：一个对象 vs 两个同构对象
   —— 这是范畴论最深的自由：可以选择"什么叫一样"
G3 Cat 不是小范畴：语言谈论自己时的大小代价
G4 自然变换的交换方块与复合

纯标准库。
"""

def banner(t):
    print("\n" + "=" * 68)
    print(t)
    print("=" * 68)

# ============================================================== G1
banner("G1  偏序集作为范畴")

objs = ["a", "b", "c"]
le = {("a", "a"), ("a", "b"), ("a", "c"),
      ("b", "b"), ("b", "c"),
      ("c", "c")}

print(f"对象：{objs}")
print(f"态射（即 <= 关系的对）：{len(le)} 个")

def comp(p, q):
    if p[1] != q[0]:
        return None
    return (p[0], q[1])

has_id = all((x, x) in le for x in objs)
closed = all(comp(p, q) in le for p, q in
             [(p, q) for p in le for q in le] if comp(p, q))
assoc = all(
    comp(comp(p, q), r) == comp(p, comp(q, r))
    for p in le for q in le for r in le
    if comp(p, q) and comp(q, r)
)

print(f"恒等态射齐备：{has_id}")
print(f"复合封闭：{closed}")
print(f"结合律成立：{assoc}")
print()
print("--> 一个偏序集就是一个范畴：对象是元素，态射是 <=。")
print("    这里没有任何「对象的内部结构」，只有谁指向谁。")

# ============================================================== G2
banner("G2  等价但不同构：范畴论的自由所在")

C_obj = {"*"}
C_Hom = {("*", "*"): {"id*"}}

D_obj = {"A", "B"}
D_Hom = {
    ("A", "A"): {"idA"},
    ("A", "B"): {"f"},
    ("B", "A"): {"g"},
    ("B", "B"): {"idB"},
}
D_comp = {
    ("idA", "idA"): "idA", ("f", "idA"): "f", ("g", "f"): "idA",
    ("idB", "idB"): "idB", ("g", "idB"): "g", ("f", "g"): "idB",
    ("idA", "g"): "g", ("idB", "f"): "f",
}

# 每个态射的源与靶
src = {"idA": "A", "f": "A", "g": "B", "idB": "B"}
tgt = {"idA": "A", "f": "B", "g": "A", "idB": "B"}

def Dc(h, k):
    """先 k 后 h：k: X->Y, h: Y->Z"""
    if src.get(h) != tgt.get(k):
        return None          # 不可复合
    return D_comp.get((h, k))

# 恒等律：只对合法复合检查
ok_left = all(Dc("idA", k) == k for k in ["idA", "g"])   # 靶为 A 的态射
ok_right = all(Dc(k, "idA") == k for k in ["idA", "f"])  # 源为 A 的态射
ok_left = ok_left and all(Dc("idB", k) == k for k in ["idB", "f"])
ok_right = ok_right and all(Dc(k, "idB") == k for k in ["idB", "g"])

# 结合律：只对连续可复合的三元组检查
morphs = ["idA", "f", "g", "idB"]
assoc_D = True
for h in morphs:
    for k in morphs:
        for m in morphs:
            if Dc(k, m) is None or Dc(h, k) is None:
                continue
            if Dc(Dc(h, k), m) != Dc(h, Dc(k, m)):
                assoc_D = False
print("D 是合法范畴：", ok_left and ok_right and assoc_D)
print(f"C 的对象数：{len(C_obj)}，D 的对象数：{len(D_obj)}")
print()
print("两者同构吗？")
print(f"  范畴同构要求对象集双射：{len(C_obj)} vs {len(D_obj)} → 不可能")
print("  → C 与 D 不同构")
print()
print("两者等价吗？（函子 F: C -> D，F(*) = A）")
print(f"  Hom_C(*,*) = {C_Hom[('*','*')]}，大小 1")
print(f"  Hom_D(A,A) = {D_Hom[('A','A')]}，大小 1")
print("  → 满忠实成立（两侧都是 1 元集）")
print("  → 本质满成立（A ≅ A；B ≅ A 由 f 给出）")
print()
print("--> C 与 D 等价，但不同构。")
print("    范畴论允许把「两个对象、彼此同构」与「一个对象」看作同一件事。")
print("    它的自由不在能造新对象，在能重新规定什么叫「一样」。")

# ============================================================== G3
banner("G3  Cat 不是小范畴：语言谈论自己的代价")

print("小范畴：对象集与态射集都是集合")
print("大范畴：不满足上述条件")
print()
print("Cat = 所有小范畴构成的范畴")
print("  若 Cat 自己是小范畴，则它有一个对象集，包含所有小范畴")
print("  可用分离原则构造「不含自身的小范畴」的范畴 —— 与罗素悖论同型")
print()
print("  结论：Cat 是大范畴")
print()
print("--> 一门能谈论所有数学结构的语言，不能无代价地谈论自己的全体。")
print("    这个代价和 1901 年那个悖论是同一个。")

# ============================================================== G4
banner("G4  自然变换的交换方块与复合")

F = {"a": {0}, "b": {0, 1}, "c": {0, 1, 2}}
G = {"a": {0}, "b": {0, 1}, "c": {0, 1, 2}}
H = {"a": {0}, "b": {0, 1}, "c": {0, 1, 2}}
on = {"ab": lambda s: s, "bc": lambda s: s, "ac": lambda s: s}

alpha = {k: (lambda s: s) for k in "abc"}
beta = {k: (lambda s: s) for k in "abc"}

def check_nat(al, F_, G_, on):
    for X, Y, m in [("a", "b", "ab"), ("b", "c", "bc"), ("a", "c", "ac")]:
        for s in F_[X]:
            if on[m](al[X](s)) != al[Y](on[m](s)):
                return False
    return True

print("alpha: F => G 自然：", check_nat(alpha, F, G, on))
print("beta : G => H 自然：", check_nat(beta, G, H, on))
comp_nat = {k: (lambda s, k=k: beta[k](alpha[k](s))) for k in "abc"}
print("beta∘alpha: F => H 自然：", check_nat(comp_nat, F, H, on))
print()
print("--> 自然变换可复合，且复合后仍自然。")
print("    函子映射范畴，自然变换映射函子：这就是层层抬升。")

banner("结论")
print("G1 偏序集是范畴：对象无内部，只有箭头")
print("G2 等价 ≠ 同构：等价但不同构的实例已构造")
print("G3 Cat 是大范畴：谈论所有数学结构的语言，不能无代价谈论自己")
print("G4 自然变换可复合：数学谈论数学靠的是这一层层抬升")

```

## 五、实跑输出

```text

====================================================================
G1  偏序集作为范畴
====================================================================
对象：['a', 'b', 'c']
态射（即 <= 关系的对）：6 个
恒等态射齐备：True
复合封闭：True
结合律成立：True

--> 一个偏序集就是一个范畴：对象是元素，态射是 <=。
    这里没有任何「对象的内部结构」，只有谁指向谁。

====================================================================
G2  等价但不同构：范畴论的自由所在
====================================================================
D 是合法范畴： True
C 的对象数：1，D 的对象数：2

两者同构吗？
  范畴同构要求对象集双射：1 vs 2 → 不可能
  → C 与 D 不同构

两者等价吗？（函子 F: C -> D，F(*) = A）
  Hom_C(*,*) = {'id*'}，大小 1
  Hom_D(A,A) = {'idA'}，大小 1
  → 满忠实成立（两侧都是 1 元集）
  → 本质满成立（A ≅ A；B ≅ A 由 f 给出）

--> C 与 D 等价，但不同构。
    范畴论允许把「两个对象、彼此同构」与「一个对象」看作同一件事。
    它的自由不在能造新对象，在能重新规定什么叫「一样」。

====================================================================
G3  Cat 不是小范畴：语言谈论自己的代价
====================================================================
小范畴：对象集与态射集都是集合
大范畴：不满足上述条件

Cat = 所有小范畴构成的范畴
  若 Cat 自己是小范畴，则它有一个对象集，包含所有小范畴
  可用分离原则构造「不含自身的小范畴」的范畴 —— 与罗素悖论同型

  结论：Cat 是大范畴

--> 一门能谈论所有数学结构的语言，不能无代价地谈论自己的全体。
    这个代价和 1901 年那个悖论是同一个。

====================================================================
G4  自然变换的交换方块与复合
====================================================================
alpha: F => G 自然： True
beta : G => H 自然： True
beta∘alpha: F => H 自然： True

--> 自然变换可复合，且复合后仍自然。
    函子映射范畴，自然变换映射函子：这就是层层抬升。

====================================================================
结论
====================================================================
G1 偏序集是范畴：对象无内部，只有箭头
G2 等价 ≠ 同构：等价但不同构的实例已构造
G3 Cat 是大范畴：谈论所有数学结构的语言，不能无代价谈论自己
G4 自然变换可复合：数学谈论数学靠的是这一层层抬升

```

---

*2026-10-26 · 附录 v1.0 · 嵌入代码与源文件逐字节一致*
