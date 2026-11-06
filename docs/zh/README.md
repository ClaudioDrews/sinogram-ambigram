# 汉字旋转双读字形 · Sinogram Ambigrams

**旋转 180°，同一图形能否呈现另一种字形与含义？**

**语言：** [English](../../README.md) · 简体中文 · [日本語](../ja/README.md)

本项目结合**几何、语言、视觉感知与意义**，探索汉字和日语汉字的旋转双读字形（rotational ambigrams）：同一图形在正向与旋转 180° 后，可能呈现不同的字符。灵感来自 [Issei Nomura](https://x.com/IsseiNomura) 的双读文字艺术。这是一项独立研究与艺术实验，与该艺术家没有合作或背书关系。

![在浏览器中生成 甲 与 由 的示例](../../assets/generator-preview.png)

### 旋转字形示例

![四组候选字形，每组分别展示 0° 与 180° 的同一 SVG](../../assets/rotation-gallery.png)

*由生成器生成的四组实验性字形：甲 ↔ 由、吉 ↔ 阜、目 ↔ 目、回 ↔ 回。请将两个方向与目标字符进行视觉比较。*

## 立即体验

- **[双读字形生成器](https://claudiodrews.github.io/sinogram-ambigram/generator/)**：输入一个汉字，搜索旋转后几何形状相近的候选字，合成可旋转的 SVG、切换构造方法并下载。仅提供**少量人工整理的语义替代字**，不是完整的同义词词典。
- **[Rotation Lab](https://claudiodrews.github.io/sinogram-ambigram/demo/)**：探索 **16 个示例**，包括复杂结构、笔画重合、显著性调节、中心对称和构件布局。两种演示均支持英语、中文和日语界面。

**[项目网站](https://claudiodrews.github.io/sinogram-ambigram/)** 和上方两个交互工具已通过 GitHub Pages 发布。也可以从 [`generator/`](../../generator/) 和 [`demo/`](../../demo/) 查看源代码。

## 基本方法

1. 从已有的旋转距离数据中为输入字符寻找候选配对。
2. 读取 KanjiVG 的笔画矢量路径，将候选字旋转 180° 后叠加。
3. 尝试笔画显著性融合、直接叠加、共用骨架或 C₂ 对称方法。
4. 若没有适合的直接候选，可尝试小型语义替代列表。
5. 展示可旋转 SVG、采用的方法与反馈方式。

目前的研究数据包括 **2,770 个字符**与 **5,180 条精细测量记录**。生成器内置 **432 个字符**的笔画矢量，其他字符可尝试联网加载。原始字符集合主要来自日语常用汉字和人名用汉字，**并未涵盖所有中文汉字**。生成的图形需要通过实际旋转和目视比较来判断效果。

## 代码与研究资料

当前 Python 依赖需要 **Python 3.12 或更新版本**。

- [理论](../../theory/)：180° 旋转、IDS 结构代数及字形规则。
- [方法](../../methods/)：候选搜索、距离度量与生成思路。
- [研究结果](../../findings/)：候选字对、实验结果和方法比较。
- [数据](../../data/)：CSV 排名、字符列表和来源信息。
- [Python 代码](../../code/)：实验性处理与测试。
- [生成器说明（英文）](../../generator/README.md)：运行与技术细节。

## 参与与致谢

欢迎[提交 GitHub Issue](https://github.com/ClaudioDrews/sinogram-ambigram/issues/new)，附上字符配对、方法、SVG 或截图与改进建议；也可通过[电子邮件](mailto:21au6i06R3w55891@proton.me)联系作者 Claudio Drews。原创代码和文字遵循 [MIT](../../LICENSE)；源自 KanjiVG 的笔画矢量及其改编内容遵循 [CC BY-SA 3.0](../../NOTICE.md)。详见[版权与来源说明](../../NOTICE.md)。
