/* C2 Visual Research Lab — browser-only, reproducible static experiments.
 * Character paths come from the same embedded KanjiVG corpus as Rotation Lab.
 * This does NOT execute PRC source rendering or model/reader evaluation.
 */
"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const M = window.SinogramC2Math;
  const PATHS = window.SINOGRAM_KANJIVG_PATHS;
  if (!M || !PATHS) throw new Error("Required local C2/geometry scripts did not load");
  const SWEEP = Object.freeze([
    {t:2,near:0,control:0},{t:4,near:2,control:1},{t:8,near:11,control:6},
    {t:12,near:14,control:9},{t:16,near:16,control:15}
  ]);
  const UI = {
    en:{
      home:"Project home",rotationLab:"Rotation Lab",prcExplorer:"Mainland Chinese Explorer",language:"Language",
      eyebrow:"Geometry · perception · reproducible experiments",title:"Visual Research Lab",
      intro:"Turn one drawing by 180°, separate what stays invariant from what changes, and inspect why geometric similarity does not guarantee two readable characters.",
      scopeJapanese:"KanjiVG stroke paths · Japanese source",scopeMath:"Exact C₂ algebra · finite-grid rendering",scopeNoReading:"No human readability claim",
      c2Heading:"What survives a half-turn?",c2Intro:"The same KanjiVG path drawing appears in three synchronized views. Move the rotation centre or interpolate between its original, C₂-even and 180°-rotated forms.",
      glyph:"Source character",cx:"Centre offset X",cy:"Centre offset Y",balance:"Shape interpolation (−1 → +1)",
      halfTurn:"Half-turn 180°",play:"Animate",stop:"Stop animation",reset:"Reset geometry",
      live:"Interpolated single drawing",liveNote:"+1 = source; 0 = even component; −1 = 180° rotation.",
      even:"Even component · C₂ invariant",evenNote:"Half the sum of the source and its half-turn.",
      odd:"Odd component · changes sign",oddNote:"Warm = positive; blue = negative differences.",
      positive:"Positive",negative:"Negative",
      iou:"Binary rotational IoU (source vs turned)",difference:"Normalized asymmetric ink",clipping:"Ink clipped by canvas",
      c2Precision:"The algebra is exact on the unbounded plane; this interaction uses a padded 145×145 sampled raster. Rotation and pixel coverage are finite-grid approximations. Moving the centre can affect overlap and edge clipping. A C₂-even field does not prove a readable ambigram.",
      widthHeading:"Why preserving the historical renderer matters",
      widthIntro:"Move a synthetic measured median-to-contour radius. The historical v1.16 renderer divided that radius by two again; the corrected constructor uses the measured half-width. This schematic is not a licensed original outline.",
      halfWidth:"Measured half-width (illustrative units)",oldIoU:"Historical median source-outline IoU",newIoU:"Corrected median source-outline IoU",improvements:"Source-outline cases improved",
      widthCaveat:"Values are published geometric results from 32 pinned cases (PR #19), not values computed from the synthetic bands above and not measures of reading. Historical PRC v1.16 code and reproduction remain unchanged.",
      widthMethod:"Original method and replay safeguards",
      abHeading:"Matching strokes is not the same as changing a drawing",
      abIntro:"In a frozen experiment of 32 new character pairs, relaxing the registration threshold found more candidate matches but no final pixel changes. The bars show pairs with at least one stroke match, not readable ambigrams.",
      threshold:"Maximum stroke-spine RMS threshold",nearPairs:"Overlap-enriched pairs",controlPairs:"Hash-selected controls",matched:"New pairs with at least one match",changed:"New pairs with changed raster pixels",
      abCaveat:"Documented negative result: at threshold 16, 31/32 new pairs had a match but 0/32 changed final pixels. The original acceptance rule returned the union baseline. No human readability was tested.",
      abForensic:"Original two-pair forensic diagnosis",abStudy:"Independent 32-pair study (draft PR #21)",
      fieldHeading:"Local compensation and even harmonic fields",fieldIntro:"Two mathematical sketches of spatial thickness fields, not output from the R-ODD or harmonic constructors. Compare localized adjustment with a field invariant under 180° rotation.",
      fieldStrength:"Illustrative field intensity",localTitle:"Local response (concept only)",localNote:"A single localized Gaussian patch: not necessarily C₂-symmetric, and not the R-ODD operator.",
      harmonicTitle:"C₂-even harmonic field (concept only)",harmonicNote:"An even cosine-product field, f(−x,−y) = f(x,y). Not an optimized stroke result.",
      fieldCaveat:"PRs #14 (R-ODD) and #15 (harmonic) remain separate, unmerged experiments. This conceptual illustration does not establish that either method works better.",
      readingHeading:"A geometric match is a candidate, not a readable ambigram",
      readingIntro:"Source shapes may be close under half-turn, a constructor may or may not change the drawing, and human readers may or may not identify both characters. The measurements here address geometry, not blinded reading.",
      existingLab:"Explore 16 Rotation Lab examples",browsePRC:"Browse PRC coarse source candidates",researchDocs:"Research documentation",
      footer:"Original interactive code: MIT. Shared Japanese stroke paths: KanjiVG CC BY-SA 3.0. PRC source glyphs: Make Me a Hanzi / Arphic Public License. Heatmaps and width bands are synthetic. No model API or personal-data collection.",
      attribution:"Attribution and licenses",
      original:"original",evenWord:"even",rotated:"rotated",sourceBand:"Source-outline target (schematic)",legacyBand:"v1.16 · extra halving",correctedBand:"v2 · measured half-width"
    },
    zh:{
      home:"项目主页",rotationLab:"旋转实验室",prcExplorer:"中国大陆候选字探索",language:"语言",
      eyebrow:"几何 · 感知 · 可复现实验",title:"可视化研究实验室",
      intro:"将同一幅图旋转 180°，分离保持不变的部分与发生变化的部分，并观察为何几何相近不等于两种读法均可辨认。",
      scopeJapanese:"KanjiVG 笔画路径 · 日文字形来源",scopeMath:"C₂ 严格代数 · 有限栅格绘制",scopeNoReading:"不宣称人类可读性",
      c2Heading:"旋转半周，哪些部分保持不变？",c2Intro:"同一 KanjiVG 路径分为三个同步画面。移动旋转中心，或在原图、C₂ 偶分量与旋转 180° 后的图像之间插值。",
      glyph:"来源字符",cx:"旋转中心 X 偏移",cy:"旋转中心 Y 偏移",balance:"图形插值（−1 → +1）",
      halfTurn:"旋转 180°",play:"自动演示",stop:"停止动画",reset:"重置几何",
      live:"同一图形的插值结果",liveNote:"+1 = 原图；0 = 偶分量；−1 = 旋转 180°。",
      even:"偶分量 · C₂ 不变",evenNote:"原图与半周旋转图的和的一半。",
      odd:"奇分量 · 旋转后变号",oddNote:"暖色为正差异，蓝色为负差异。",
      positive:"正值",negative:"负值",
      iou:"二值图旋转 IoU",difference:"标准化非对称墨量",clipping:"边缘裁剪墨量",
      c2Precision:"无界平面上的代数关系严格成立；互动演示使用加边框的 145×145 采样栅格。旋转与覆盖率存在栅格近似。移动中心可能影响重合度或边缘裁剪。C₂ 偶分量不能证明可读性。",
      widthHeading:"为什么必须保留历史渲染器",
      widthIntro:"调节一个合成示意图中测量到的中线—轮廓半径。历史 v1.16 再除以二，修正版直接采用测得的半宽。该示意不是受许可保护的原字形轮廓。",
      halfWidth:"测得半宽（示意单位）",oldIoU:"历史原轮廓 IoU 中位数",newIoU:"修正版原轮廓 IoU 中位数",improvements:"改善的来源轮廓个数",
      widthCaveat:"数据来自 PR #19 固定的 32 个几何样本，与上方合成图示无计算关系，不是可读性测量。历史 PRC v1.16 实现与复算保持不变。",
      widthMethod:"原始方法与历史复现保护",
      abHeading:"笔画匹配不等于最终图像发生变化",
      abIntro:"预先固定的 32 组新字符对实验表明：放宽匹配阈值会产生更多笔画配对，但最终图像仍未改变。柱状图表示存在至少一个匹配的字符对数，并非可读合字数量。",
      threshold:"笔画中线 RMS 距离上限",nearPairs:"几何重合度优选组",controlPairs:"哈希选择对照组",matched:"至少有一处匹配的新字对",changed:"最终图像像素变化的新字对",
      abCaveat:"已记录的负结果：阈值为 16 时 31/32 组有笔画匹配，但图像变化仍为 0/32。原有接受规则返回简单并集。未测试人类可读性。",
      abForensic:"原始两组案例诊断",abStudy:"独立 32 组实验（草稿 PR #21）",
      fieldHeading:"局部补偿与 C₂ 偶谐波场",fieldIntro:"两个笔画厚度空间场的数学示意，而非 R-ODD 或谐波算法实际输出。比较局部调整与旋转 180° 后保持不变的场。",
      fieldStrength:"示意场强度",localTitle:"局部响应（仅概念）",localNote:"单个局部高斯斑块：未必符合 C₂ 对称，也不是 R-ODD 算子。",
      harmonicTitle:"C₂ 偶谐波场（仅概念）",harmonicNote:"偶余弦乘积场，f(−x,−y) = f(x,y)；不是经过优化的笔画结果。",
      fieldCaveat:"PR #14（R-ODD）和 #15（谐波）仍是独立、未合并的实验。概念图不证明哪种方法更有效。",
      readingHeading:"几何近似是候选，不是可读合字",
      readingIntro:"旋转后字形几何可能接近，构造算法未必改变绘图，人类读者也未必辨认两个目标字。本页测量的是几何，不是盲法阅读结果。",
      existingLab:"浏览旋转实验室的 16 例",browsePRC:"浏览 PRC 粗筛候选",researchDocs:"研究文档",
      footer:"交互代码：MIT。日文字形笔画：KanjiVG CC BY-SA 3.0。PRC 来源：Make Me a Hanzi / Arphic Public License。热图和笔画带为合成示意。无需模型 API，不收集个人数据。",
      attribution:"来源与许可",original:"原图",evenWord:"偶分量",rotated:"旋转图",sourceBand:"来源轮廓目标（示意）",legacyBand:"v1.16 · 再次减半",correctedBand:"v2 · 测得半宽"
    },
    ja:{
      home:"プロジェクト",rotationLab:"回転ラボ",prcExplorer:"中国簡体字の候補探索",language:"言語",
      eyebrow:"幾何 · 知覚 · 再現可能な実験",title:"ビジュアル研究ラボ",
      intro:"同じ図形を180°回転し、不変な部分と変化する部分を分離します。形状が近くても両方の文字として読めるとは限りません。",
      scopeJapanese:"KanjiVGストローク · 日本語系資料",scopeMath:"厳密なC₂代数 · 有限グリッド描画",scopeNoReading:"人の可読性は未検証",
      c2Heading:"半回転で何が残るのか？",c2Intro:"同じKanjiVG図形を3画面で同期表示します。回転中心を動かしたり、元画像・C₂偶成分・180°回転像の間を補間できます。",
      glyph:"元の漢字",cx:"回転中心 X のずれ",cy:"回転中心 Y のずれ",balance:"図形の補間（−1 → +1）",
      halfTurn:"180°回転",play:"アニメーション",stop:"停止",reset:"幾何をリセット",
      live:"単一図形の補間",liveNote:"+1＝元図形、0＝偶成分、−1＝180°回転。",
      even:"偶成分 · C₂不変",evenNote:"元画像と半回転像の和の半分。",
      odd:"奇成分 · 回転で符号反転",oddNote:"暖色は正、青は負の差分。",
      positive:"正",negative:"負",
      iou:"二値の回転IoU",difference:"正規化された非対称インク量",clipping:"領域外に切れたインク量",
      c2Precision:"無限平面での代数は厳密ですが、表示は余白を追加した145×145格子で近似します。回転や画素の被覆は離散化の影響を受け、中心移動により重なりや切り取りも変わります。C₂偶成分は可読性の証明ではありません。",
      widthHeading:"歴史的レンダラーを残す理由",
      widthIntro:"合成模式図で計測された中心線—輪郭の半径を動かします。歴史的v1.16は半径をさらに2で割り、修正版は測定した半幅をそのまま使います。元の字形輪郭を再配布する図ではありません。",
      halfWidth:"計測半幅（模式値）",oldIoU:"歴史版の元輪郭IoU中央値",newIoU:"修正版の元輪郭IoU中央値",improvements:"元輪郭との一致が改善した標本",
      widthCaveat:"値はPR #19の固定32標本から得た幾何結果であり、上の模式的な帯から算出した値でも読字スコアでもありません。歴史的PRC v1.16と再現手順は変更していません。",
      widthMethod:"手法と歴史的再現の保護",
      abHeading:"筆画の対応付けと図形の変化は別",
      abIntro:"事前に固定した異字32組では、対応付け閾値を緩めると候補が増えましたが、最終画像は一度も変わりませんでした。棒は対応がある組数であり、読めるアンビグラムの数ではありません。",
      threshold:"筆画中心線RMS距離の上限",nearPairs:"重なりの高い組",controlPairs:"ハッシュ選択の対照群",matched:"少なくとも1本が対応した新規組",changed:"最終ラスタが変化した新規組",
      abCaveat:"記録された負の結果：閾値16では31/32組に筆画の対応があるのに、最終画像の変化は0/32組。元の採択条件は単純な重ね合わせを返しました。人による可読性は未検証です。",
      abForensic:"最初の2組の原因調査",abStudy:"独立32組の実験（ドラフトPR #21）",
      fieldHeading:"局所補正とC₂偶の調和場",fieldIntro:"ストローク幅の空間場を示す2つの数学的模式図です。R-ODDや調和方式の実際の結果ではありません。局所調整と180°回転で不変な場を比べます。",
      fieldStrength:"模式的な場の強さ",localTitle:"局所反応（概念図）",localNote:"単一の局所ガウス分布。必ずしもC₂対称ではなく、R-ODD演算子そのものでもありません。",
      harmonicTitle:"C₂偶の調和場（概念図）",harmonicNote:"偶の余弦積場：f(−x,−y)=f(x,y)。最適化後の筆画ではありません。",
      fieldCaveat:"PR #14（R-ODD）と #15（調和場）は独立した未統合実験です。この模式図で優劣は判定できません。",
      readingHeading:"幾何学的近さは候補であり、読めるとは限らない",
      readingIntro:"回転後の字形が近いこと、構成手法が図を変更すること、人が両方の文字を読めることは別々の問題です。ここでの値は幾何の測定であり、盲検読字試験ではありません。",
      existingLab:"従来の回転ラボ16例を見る",browsePRC:"PRC粗探索候補を見る",researchDocs:"研究資料",
      footer:"オリジナルの対話コード：MIT。日本語字形：KanjiVG CC BY-SA 3.0。PRC字形：Make Me a Hanzi / Arphic Public License。熱マップと幅の帯は合成模式図です。モデルAPIや個人情報の収集は不要です。",
      attribution:"出典とライセンス",original:"元図",evenWord:"偶成分",rotated:"回転後",sourceBand:"元輪郭の目標（模式）",legacyBand:"v1.16 · 半幅を再び半減",correctedBand:"v2 · 測定した半幅"
    }
  };
  let lang = "en", source = null, analysed = null, animating = false;
  let animationHandle = null, phaseStart = null;
  const reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setLanguage(next) {
    lang = UI[next] ? next : "en";
    document.documentElement.lang = lang === "zh" ? "zh-Hans" : lang;
    $("lang").value = lang;
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const value = UI[lang][el.dataset.i18n];
      if (value !== undefined) el.textContent = value;
    });
    document.title = "C₂ · " + UI[lang].title + " | Sinogram Ambigrams";
    $("play").textContent = animating ? UI[lang].stop : UI[lang].play;
    drawC2();
    drawWidths();
  }

  function rasterizeGlyph(character) {
    const canvas = document.createElement("canvas");
    canvas.width = M.GRID; canvas.height = M.GRID;
    const context = canvas.getContext("2d", {willReadFrequently: true});
    context.translate(M.OFFSET, M.OFFSET);
    context.lineWidth = 5;
    context.strokeStyle = "#000";
    context.lineCap = "round";
    context.lineJoin = "round";
    for (const path of PATHS[character] || []) context.stroke(new Path2D(path));
    const rgba = context.getImageData(0, 0, M.GRID, M.GRID).data;
    const out = new Float64Array(M.GRID * M.GRID);
    for (let i = 0; i < out.length; i++) out[i] = rgba[i * 4 + 3] / 255;
    return out;
  }

  function drawImage(canvas, samples, mode) {
    const ctx = canvas.getContext("2d");
    const data = ctx.createImageData(M.GRID, M.GRID);
    for (let i = 0; i < samples.length; i++) {
      const o = i * 4, v = samples[i];
      if (mode === "odd") {
        const a = Math.max(0, Math.min(1, Math.abs(v) * 2));
        const pos = v >= 0;
        data.data[o] = pos ? 181 : 55;
        data.data[o + 1] = pos ? 93 : 108;
        data.data[o + 2] = pos ? 53 : 162;
        data.data[o + 3] = Math.round(a * 255);
      } else {
        const even = mode === "even";
        data.data[o] = even ? 20 : 28;
        data.data[o + 1] = even ? 94 : 48;
        data.data[o + 2] = even ? 81 : 46;
        data.data[o + 3] = Math.round(Math.max(0, Math.min(1, v)) * 255);
      }
    }
    ctx.clearRect(0, 0, M.GRID, M.GRID);
    ctx.putImageData(data, 0, 0);
  }

  function drawCentre() {
    const ctx = $("liveCanvas").getContext("2d");
    const x = M.CENTRE + Number($("cx").value),
          y = M.CENTRE + Number($("cy").value);
    ctx.save();
    ctx.strokeStyle = "#bd6636";
    ctx.lineWidth = .9;
    ctx.beginPath();
    ctx.moveTo(x - 5, y); ctx.lineTo(x + 5, y);
    ctx.moveTo(x, y - 5); ctx.lineTo(x, y + 5);
    ctx.stroke();
    ctx.restore();
  }

  function updateBlend() {
    if (!analysed) return;
    const t = Number($("balance").value);
    drawImage($("liveCanvas"), M.interpolate(analysed, t), "live");
    drawCentre();
    const status = t > .98 ? UI[lang].original :
                   t < -.98 ? UI[lang].rotated :
                   Math.abs(t) < .02 ? UI[lang].evenWord : "";
    $("balanceOut").textContent = (t >= 0 ? "+" : "") + t.toFixed(2) +
      (status ? " · " + status : "");
  }

  function drawC2() {
    if (!source) return;
    analysed = M.decompose(source, M.GRID,
      M.CENTRE + Number($("cx").value),
      M.CENTRE + Number($("cy").value));
    drawImage($("evenCanvas"), analysed.even, "even");
    drawImage($("oddCanvas"), analysed.odd, "odd");
    updateBlend();
    $("cxOut").textContent = $("cx").value;
    $("cyOut").textContent = $("cy").value;
    $("iou").textContent = analysed.binaryIoU.toFixed(3);
    $("difference").textContent = (100 * analysed.relativeDifference).toFixed(1) + "%";
    $("clipping").textContent = analysed.clipped.toFixed(2);
  }

  function stopAnimation() {
    animating = false; phaseStart = null;
    if (animationHandle !== null) cancelAnimationFrame(animationHandle);
    animationHandle = null;
    $("play").textContent = UI[lang].play;
  }
  function animate(timestamp) {
    if (!animating) return;
    if (phaseStart === null) phaseStart = timestamp;
    const t = Math.cos(2 * Math.PI * (timestamp - phaseStart) / 5000);
    $("balance").value = (Math.round(t * 20) / 20).toFixed(2);
    updateBlend();
    animationHandle = requestAnimationFrame(animate);
  }

  function drawWidths() {
    const c = $("widthCanvas"), ctx = c.getContext("2d");
    const h = Number($("halfWidth").value), label = UI[lang];
    ctx.clearRect(0, 0, c.width, c.height);
    const rows = [
      {y:52, width:2*h, color:"#2c6960", title:label.sourceBand},
      {y:124, width:h, color:"#b66342", title:label.legacyBand},
      {y:196, width:2*h, color:"#2c6960", title:label.correctedBand}
    ];
    ctx.font = "14px system-ui, sans-serif";
    for (const row of rows) {
      ctx.fillStyle = "#233f38"; ctx.fillText(row.title, 20, row.y - 23);
      ctx.beginPath();ctx.moveTo(43,row.y);ctx.lineTo(531,row.y);
      ctx.strokeStyle=row.color;ctx.lineWidth=row.width;ctx.lineCap="round";ctx.stroke();
      ctx.beginPath();ctx.moveTo(43,row.y);ctx.lineTo(531,row.y);
      ctx.strokeStyle="#fff";ctx.lineWidth=1.5;ctx.setLineDash([8,6]);ctx.stroke();
      ctx.setLineDash([]);
    }
    $("halfWidthOut").textContent = String(h);
  }

  function drawAB() {
    const row = SWEEP.find(x => x.t === Number($("threshold").value));
    if (!row) return;
    $("nearBar").style.width = (100 * row.near / 16) + "%";
    $("controlBar").style.width = (100 * row.control / 16) + "%";
    $("nearOut").textContent = row.near + "/16";
    $("controlOut").textContent = row.control + "/16";
    $("matched").textContent = row.near + row.control + "/32";
  }

  function drawField(id, strength, harmonic) {
    const canvas = $(id), ctx = canvas.getContext("2d"), N = canvas.width;
    const image = ctx.createImageData(N, N);
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const qx = 2 * x / (N-1) - 1, qy = 2 * y / (N-1) - 1;
      const local = Math.exp(-((qx - .37)**2 + (qy + .21)**2) / (.18**2 * 2));
      const value = strength * (harmonic ?
        Math.cos(Math.PI * qx) * Math.cos(2 * Math.PI * qy) : local);
      const a = Math.max(0, Math.min(1, Math.abs(value)));
      const warm = value >= 0, k = (y*N+x)*4;
      image.data[k] = Math.round(243*(1-a) + (warm ? 175 : 59)*a);
      image.data[k+1] = Math.round(248*(1-a) + (warm ? 95 : 112)*a);
      image.data[k+2] = Math.round(243*(1-a) + (warm ? 61 : 163)*a);
      image.data[k+3] = 255;
    }
    ctx.putImageData(image, 0, 0);
    ctx.strokeStyle = "rgba(35,65,54,.35)";ctx.lineWidth=1;
    ctx.beginPath();ctx.moveTo(N/2,0);ctx.lineTo(N/2,N);
    ctx.moveTo(0,N/2);ctx.lineTo(N,N/2);ctx.stroke();
    ctx.beginPath();ctx.arc(N/2,N/2,3,0,2*Math.PI);ctx.stroke();
  }
  function drawFields() {
    const value = Number($("fieldStrength").value);
    $("fieldStrengthOut").textContent=value.toFixed(2);
    drawField("localField",value,false);
    drawField("harmonicField",value,true);
  }

  $("glyph").addEventListener("change", () => {
    stopAnimation();
    source = rasterizeGlyph($("glyph").value);
    $("balance").value = "1";
    drawC2();
  });
  for (const id of ["cx","cy"]) $(id).addEventListener("input",drawC2);
  $("balance").addEventListener("input",() => {stopAnimation();updateBlend()});
  $("halfTurn").addEventListener("click",() => {
    stopAnimation();
    $("balance").value = Number($("balance").value) > 0 ? "-1" : "1";
    updateBlend();
  });
  $("play").addEventListener("click",() => {
    if (animating) {stopAnimation();return;}
    if (reducedMotion) { $("balance").value="-1";updateBlend();return; }
    animating=true;phaseStart=null;
    $("play").textContent=UI[lang].stop;
    animationHandle=requestAnimationFrame(animate);
  });
  $("reset").addEventListener("click",() => {
    stopAnimation();
    $("cx").value=0;$("cy").value=0;$("balance").value=1;drawC2();
  });
  $("halfWidth").addEventListener("input",drawWidths);
  $("threshold").addEventListener("change",drawAB);
  $("fieldStrength").addEventListener("input",drawFields);
  $("lang").addEventListener("change",event=>setLanguage(event.target.value));

  const qs = new URLSearchParams(window.location.search);
  if (PATHS[qs.get("glyph")] && [...$("glyph").options].some(o=>o.value===qs.get("glyph")))
    $("glyph").value=qs.get("glyph");
  source = rasterizeGlyph($("glyph").value);
  setLanguage(qs.get("lang") || "en");
  drawAB();drawFields();
})();
