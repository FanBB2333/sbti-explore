# SBTI 解析记录

这个仓库记录的是当前 [sbti.unun.dev](https://sbti.unun.dev/) 页面里前端脚本所实现的判定逻辑，而不是心理学意义上的“人格理论”。

=

## 仓库结构

- `README.md`
  - 用中文说明当前页面的题目结构、总答案数、维度折叠方式、人格匹配规则和特殊覆盖规则。
- `analyze.py`
  - 把当前页面里的核心判定逻辑重写成一个可执行、可导入的 Python 脚本，便于复算和验证。
- `tests/test_analyze.py`
  - 用最小测试约束总数、常规人格命中、`DRUNK` 覆盖和 `HHHH` 兜底。

## 先说结论

这套题当前一共有：

- `30` 道常规题
- `1` 道必出的特殊题 `drink_gate_q1`
- `1` 道条件触发隐藏题 `drink_gate_q2`

因此“完整可提交答卷”的总数不是固定 `31` 题的简单乘法，而是：

```text
3^30 × (3 + 2) = 5 × 3^30 = 1,029,455,660,473,245
```

这里的 `(3 + 2)` 来自特殊题分支：

- `drink_gate_q1` 选项共有 4 个
- 其中选到“饮酒”时，还会再出现一题二选一隐藏题
- 所以特殊部分不是单纯 `4` 种，而是：
  - 非饮酒分支：`3` 种
  - 饮酒分支：`2` 种

## 页面当前到底有多少种结果

最终显示层面一共有 `27` 种结果：

- `25` 个常规人格模板
- `1` 个隐藏人格：`DRUNK`
- `1` 个兜底人格：`HHHH`

其中真正参与常规匹配的模板只有 `25` 个。`DRUNK` 和 `HHHH` 都是后置覆盖规则。

## 题目如何折叠成 15 个维度

30 道常规题被分成 `15` 个维度，每个维度正好 `2` 题，每题得分只有 `1 / 2 / 3`。

对应关系如下：

| 维度 | 名称 | 题号 |
| --- | --- | --- |
| `S1` | 自尊自信 | `q1`, `q2` |
| `S2` | 自我清晰度 | `q3`, `q4` |
| `S3` | 核心价值 | `q5`, `q6` |
| `E1` | 依恋安全感 | `q7`, `q8` |
| `E2` | 情感投入度 | `q9`, `q10` |
| `E3` | 边界与依赖 | `q11`, `q12` |
| `A1` | 世界观倾向 | `q13`, `q14` |
| `A2` | 规则与灵活度 | `q15`, `q16` |
| `A3` | 人生意义感 | `q17`, `q18` |
| `Ac1` | 动机导向 | `q19`, `q20` |
| `Ac2` | 决策风格 | `q21`, `q22` |
| `Ac3` | 执行模式 | `q23`, `q24` |
| `So1` | 社交主动性 | `q25`, `q26` |
| `So2` | 人际边界感 | `q27`, `q28` |
| `So3` | 表达与真实度 | `q29`, `q30` |

每个维度的两题相加后，得到一个 `2` 到 `6` 的总分，再压缩成三级：

- `<= 3` 记为 `L`
- `= 4` 记为 `M`
- `>= 5` 记为 `H`

也就是说，30 道题最后只保留成一个 15 位的 `L/M/H` 向量。

## 为什么维度空间是 3^15

单个维度由两道三选一题构成，总共有 `3 × 3 = 9` 种答法。  
这 9 种答法被分配到 `L / M / H` 三类时，恰好每类都是 3 种：

- `L`：`(1,1)`、`(1,2)`、`(2,1)`
- `M`：`(1,3)`、`(2,2)`、`(3,1)`
- `H`：`(2,3)`、`(3,2)`、`(3,3)`

所以：

- 15 个维度共有 `3^15 = 14,348,907` 种维度向量
- 每一种维度向量，对应 `3^15` 种常规答卷
- 再乘上特殊题分支，就回到了完整答卷总数 `5 × 3^30`

## 常规人格是怎么判出来的

页面把这 15 个维度按固定顺序拼接：

```text
S1 S2 S3 E1 E2 E3 A1 A2 A3 Ac1 Ac2 Ac3 So1 So2 So3
```

每个维度只会落到 `L / M / H` 之一。  
然后把用户向量与 25 个常规人格模板逐个比较。

比较时会先把：

- `L -> 1`
- `M -> 2`
- `H -> 3`

然后按 15 个维度逐位比较，计算总“距离”：

```text
distance = Σ |user_i - type_i|
```

这个距离就是页面里真正用于排序的核心指标。

同时页面还会记录：

- `exact`
  - 有多少个维度完全命中
- `similarity`
  - 匹配度百分比，计算公式为：
  - `round((1 - distance / 30) * 100)`

排序规则是：

1. `distance` 越小越靠前
2. 如果距离相同，`exact` 越大越靠前
3. 如果还相同，`similarity` 越大越靠前
4. 如果还完全相同，则保留源码里 `NORMAL_TYPES` 的原始顺序

第三条理论上和第一条高度相关，因为 `similarity` 本质上就是 `distance` 的线性换算，但源码依然保留了这一层比较。

## 特殊覆盖规则

常规人格第一名算出来之后，页面还会做两层覆盖。

### 1. DRUNK 隐藏人格

页面必出一道特殊题：

- `drink_gate_q1`：您平时有什么爱好？

如果这里选择“饮酒”，页面会再插入一道隐藏题：

- `drink_gate_q2`：您对饮酒的态度是？

只有当 `drink_gate_q2 = 2` 时，最终结果会被强制改为：

- `DRUNK`

这一步会直接覆盖掉原本的常规人格第一名。

### 2. HHHH 兜底人格

如果没有触发 `DRUNK`，页面会检查常规人格第一名的 `similarity`。

当：

- `bestNormal.similarity < 60`

就会强制改为：

- `HHHH`

按页面的公式，这和下面这句话是等价的：

- 常规模板最近距离 `distance >= 13`

## 25 个常规人格模板

下面是页面当前写死的 25 个模板。  
每个模板都是一个 15 维的 `L/M/H` 模式串。

```text
CTRL    HHH-HMH-MHH-HHH-MHM
ATM-er  HHH-HHM-HHH-HMH-MHL
Dior-s  MHM-MMH-MHM-HMH-LHL
BOSS    HHH-HMH-MMH-HHH-LHL
THAN-K  MHM-HMM-HHM-MMH-MHL
OH-NO   HHL-LMH-LHH-HHM-LHL
GOGO    HHM-HMH-MMH-HHH-MHM
SEXY    HMH-HHL-HMM-HMM-HLH
LOVE-R  MLH-LHL-HLH-MLM-MLH
MUM     MMH-MHL-HMM-LMM-HLL
FAKE    HLM-MML-MLM-MLM-HLH
OJBK    MMH-MMM-HML-LMM-MML
MALO    MLH-MHM-MLH-MLH-LMH
JOKE-R  LLH-LHL-LML-LLL-MLM
WOC!    HHL-HMH-MMH-HHM-LHH
THIN-K  HHL-HMH-MLH-MHM-LHH
SHIT    HHL-HLH-LMM-HHM-LHH
ZZZZ    MHL-MLH-LML-MML-LHM
POOR    HHL-MLH-LMH-HHH-LHL
MONK    HHL-LLH-LLM-MML-LHM
IMSB    LLM-LMM-LLL-LLL-MLM
SOLO    LML-LLH-LHL-LML-LHM
FUCK    MLL-LHL-LLM-MLL-HLH
DEAD    LLL-LLM-LML-LLL-LHM
IMFW    LLH-LHL-LML-LLL-MLL
```

## 页面里和结果无关、但容易误解的点

- 题目顺序会在开始测试时被打乱
  - 这只影响展示顺序，不影响分数和最终人格。
- 特殊题 `drink_gate_q1` 会被随机插入到常规题列表中
  - 这只影响它出现在第几题，不影响逻辑。
- 如果选了“饮酒”，隐藏题 `drink_gate_q2` 会插在 `drink_gate_q1` 后面
  - 同样只影响展示，不影响规则本身。

## 脚本怎么用

这个仓库里的 [analyze.py](/Users/l1ght/repos/sbti-explore/analyze.py) 是对当前逻辑的 Python 重写。

最常用的命令有三个：

### 打印总览

```bash
python analyze.py summary
```

### 打印 25 个常规模板

```bash
python analyze.py patterns
```

### 直接按 15 维模式模拟分类

```bash
python analyze.py classify-levels --levels HHH-HMH-MHH-HHH-MHM
```

如果你想模拟饮酒隐藏人格：

```bash
python analyze.py classify-levels \
  --levels HHH-HMH-MHH-HHH-MHM \
  --drink-gate-choice 3 \
  --drink-trigger-choice 2
```

上面这条命令会直接得到 `DRUNK`，因为它触发了页面里的隐藏覆盖规则。

## 测试

当前测试文件是 [tests/test_analyze.py](/Users/l1ght/repos/sbti-explore/tests/test_analyze.py)。

运行方式：

```bash
python -m unittest discover -s tests -v
```

它目前锁定的行为包括：

- 总完整答卷数是否仍然是 `1,029,455,660,473,245`
- 维度折叠阈值是否仍然是 `<=3 -> L`, `=4 -> M`, `>=5 -> H`
- 一个与 `CTRL` 模板完全相同的 15 维向量是否会得到 `CTRL`
- `drink_gate_q2 = 2` 是否仍然强制覆盖成 `DRUNK`
- 一个低匹配向量是否仍然会被兜底到 `HHHH`

## 备注

这里记录的是当前站点脚本实现出来的“程序规则”，不是作者是否原本想表达的“设计意图”。  
如果线上页面未来更新了题库、阈值、模板顺序或隐藏分支，这份说明和脚本都需要重新对照页面源码更新。
