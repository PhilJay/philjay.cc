# Performance with large data

What a chart spends its time on when it draws, which settings buy the most of it back, and how to measure instead of guess.

A chart with fifty thousand entries is not automatically slow. What decides the frame time is how much of that data is on screen, and how much text and how many shapes the renderer has to put down for it.

## Only the entries in view are drawn

Before a data set is drawn, the renderers work out which entries are visible from the same two properties you can read yourself:

```kotlin
val low = chart.lowestVisibleX
val high = chart.highestVisibleX
```

The entries just outside the screen are included so the line does not stop at the edge, and the renderers walk only that stretch. So the visible range decides the cost of a frame, not the total. Fifty thousand entries with two hundred on screen cost about what two hundred cost. Zooming out is the expensive direction, which is why capping it helps:

```kotlin
chart.setVisibleXRangeMaximum(200f)
chart.moveViewToX(0f)
```

Both are computed from the current x axis range, so they have to run after the data is set. In Compose that means the `update` lambda, not `setup`, which runs once before any data exists. [Modifying the viewport](/mpandroidchart/docs/viewport/) has the rest of the window settings and [Compose](/mpandroidchart/docs/compose/) explains the two lambdas.

> A bar chart works the same way: only the visible entries are fed into its `BarBuffer`. What is still sized from the total entry count is the buffer itself, which costs memory rather than frame time.

## Measured draw times

Every number below comes from the same run: an Android emulator, API 36, arm64, on an Apple Silicon Mac, with the whole data set on screen and nothing else running. The chart draws into an offscreen bitmap, so the figure is the chart's own draw and not a whole frame, and each size runs in a process of its own, because a warming compiler and a growing heap otherwise hide the trend. Each figure is the median of nine draws after warmups. Decimation is off, which is the default.

Each cell gives the draw time and then the frame rate that draw alone allows, which is 1000 divided by the milliseconds. It is a ceiling rather than a promise: a real frame still has to measure, lay out and composite, and the display caps it at 60 or 120 whatever the chart does. Read it as headroom. Anything under 60 means the chart cannot hold a smooth frame at that size on this device, and anything under 30 will be visible as stutter while panning.

| Entries on screen | Line | Bar |
| --- | --- | --- |
| 1,000 | 1.7 ms · 588 fps | 4.3 ms · 233 fps |
| 10,000 | 9.1 ms · 110 fps | 33.5 ms · 30 fps |
| 50,000 | 39.8 ms · 25 fps | 156.6 ms · 6 fps |
| 100,000 | 76.4 ms · 13 fps | 310.3 ms · 3 fps |

```figure
<svg viewBox="0 0 760 330" width="100%" role="img" aria-label="Draw time by entries on screen, in milliseconds" style="max-width:760px;height:auto;display:block;margin:0 auto 6px">
<title>Draw time by entries on screen, in milliseconds</title>
<rect x="54" y="14" width="11" height="11" rx="3" fill="#00a9ab"/>
<text x="71" y="24" fill="rgba(255,255,255,0.78)" font-size="13">Line</text>
<rect x="105.6" y="14" width="11" height="11" rx="3" fill="#8b7cf6"/>
<text x="122.6" y="24" fill="rgba(255,255,255,0.78)" font-size="13">Bar</text>
<line x1="54" y1="278.0" x2="746" y2="278.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="282.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">0</text>
<line x1="54" y1="222.0" x2="746" y2="222.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="226.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">80</text>
<line x1="54" y1="166.0" x2="746" y2="166.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="170.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">160</text>
<line x1="54" y1="110.0" x2="746" y2="110.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="114.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">240</text>
<line x1="54" y1="54.0" x2="746" y2="54.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="58.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">320</text>
<path d="M93.5 278.0 V278.0 A1.19 1.19 0 0 1 94.69 276.81 H138.31 A1.19 1.19 0 0 1 139.5 278.0 V278.0 Z" fill="#00a9ab"><title>1,000 · Line: 1.7 ms</title></path>
<text x="116.5" y="269.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">1.7</text>
<path d="M141.5 278.0 V278.0 A3.01 3.01 0 0 1 144.51 274.99 H184.49 A3.01 3.01 0 0 1 187.5 278.0 V278.0 Z" fill="#8b7cf6"><title>1,000 · Bar: 4.3 ms</title></path>
<text x="164.5" y="268.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">4.3</text>
<text x="140.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">1,000</text>
<path d="M266.5 278.0 V275.63 A4 4 0 0 1 270.5 271.63 H308.5 A4 4 0 0 1 312.5 275.63 V278.0 Z" fill="#00a9ab"><title>10,000 · Line: 9.1 ms</title></path>
<text x="289.5" y="264.6" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">9.1</text>
<path d="M314.5 278.0 V258.55 A4 4 0 0 1 318.5 254.55 H356.5 A4 4 0 0 1 360.5 258.55 V278.0 Z" fill="#8b7cf6"><title>10,000 · Bar: 33.5 ms</title></path>
<text x="337.5" y="247.6" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">33.5</text>
<text x="313.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">10,000</text>
<path d="M439.5 278.0 V254.14000000000001 A4 4 0 0 1 443.5 250.14000000000001 H481.5 A4 4 0 0 1 485.5 254.14000000000001 V278.0 Z" fill="#00a9ab"><title>50,000 · Line: 39.8 ms</title></path>
<text x="462.5" y="243.1" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">39.8</text>
<path d="M487.5 278.0 V172.38 A4 4 0 0 1 491.5 168.38 H529.5 A4 4 0 0 1 533.5 172.38 V278.0 Z" fill="#8b7cf6"><title>50,000 · Bar: 156.6 ms</title></path>
<text x="510.5" y="161.4" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">156.6</text>
<text x="486.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">50,000</text>
<path d="M612.5 278.0 V228.51999999999998 A4 4 0 0 1 616.5 224.51999999999998 H654.5 A4 4 0 0 1 658.5 228.51999999999998 V278.0 Z" fill="#00a9ab"><title>100,000 · Line: 76.4 ms</title></path>
<text x="635.5" y="217.5" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">76.4</text>
<path d="M660.5 278.0 V64.78999999999999 A4 4 0 0 1 664.5 60.78999999999999 H702.5 A4 4 0 0 1 706.5 64.78999999999999 V278.0 Z" fill="#8b7cf6"><title>100,000 · Bar: 310.3 ms</title></path>
<text x="683.5" y="53.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">310.3</text>
<text x="659.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">100,000</text>
<line x1="54" y1="278" x2="746" y2="278" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
</svg>
```

A line costs about 0.76 microseconds per entry and a bar about 3.1, because a line is one batched call to the canvas and a bar chart is one call per bar. That ratio, not the absolute numbers, is the thing to carry to your own hardware.

## Decimation, and when it is worth it

Decimation drops entries that would land in the same pixel column, keeping the first, lowest, highest and last of each, so peaks survive. It is **off by default**: the reduction pass reads every visible entry itself, so it only pays when the drawing it saves is more expensive than the reading it adds.

| 50,000 entries | Off | On |
| --- | --- | --- |
| Plain line, one color | 39.8 ms | 62.4 ms |
| Line with a color per segment | 147.3 ms | 62.2 ms |
| Bars | 156.6 ms | 60.8 ms |

```figure
<svg viewBox="0 0 760 330" width="100%" role="img" aria-label="Draw time at 50,000 entries with decimation off and on, in milliseconds" style="max-width:760px;height:auto;display:block;margin:0 auto 6px">
<title>Draw time at 50,000 entries with decimation off and on, in milliseconds</title>
<rect x="54" y="14" width="11" height="11" rx="3" fill="#8b7cf6"/>
<text x="71" y="24" fill="rgba(255,255,255,0.78)" font-size="13">Decimation off</text>
<rect x="179.60000000000002" y="14" width="11" height="11" rx="3" fill="#00a9ab"/>
<text x="196.60000000000002" y="24" fill="rgba(255,255,255,0.78)" font-size="13">Decimation on</text>
<line x1="54" y1="278.0" x2="746" y2="278.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="282.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">0</text>
<line x1="54" y1="222.0" x2="746" y2="222.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="226.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">40</text>
<line x1="54" y1="166.0" x2="746" y2="166.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="170.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">80</text>
<line x1="54" y1="110.0" x2="746" y2="110.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="114.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">120</text>
<line x1="54" y1="54.0" x2="746" y2="54.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="58.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">160</text>
<path d="M122.33333333333331 278.0 V226.28 A4 4 0 0 1 126.33333333333331 222.28 H164.33333333333331 A4 4 0 0 1 168.33333333333331 226.28 V278.0 Z" fill="#8b7cf6"><title>Plain line,|one colour · Decimation off: 39.8 ms</title></path>
<text x="145.3" y="215.3" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">39.8</text>
<path d="M170.33333333333331 278.0 V194.64 A4 4 0 0 1 174.33333333333331 190.64 H212.33333333333331 A4 4 0 0 1 216.33333333333331 194.64 V278.0 Z" fill="#00a9ab"><title>Plain line,|one colour · Decimation on: 62.4 ms</title></path>
<text x="193.3" y="183.6" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">62.4</text>
<text x="169.3" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Plain line,</text>
<text x="169.3" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">one colour</text>
<path d="M352.99999999999994 278.0 V75.78 A4 4 0 0 1 356.99999999999994 71.78 H394.99999999999994 A4 4 0 0 1 398.99999999999994 75.78 V278.0 Z" fill="#8b7cf6"><title>Line, a colour|per segment · Decimation off: 147.3 ms</title></path>
<text x="376.0" y="64.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">147.3</text>
<path d="M400.99999999999994 278.0 V194.92 A4 4 0 0 1 404.99999999999994 190.92 H442.99999999999994 A4 4 0 0 1 446.99999999999994 194.92 V278.0 Z" fill="#00a9ab"><title>Line, a colour|per segment · Decimation on: 62.2 ms</title></path>
<text x="424.0" y="183.9" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">62.2</text>
<text x="400.0" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Line, a colour</text>
<text x="400.0" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">per segment</text>
<path d="M583.6666666666666 278.0 V62.75999999999999 A4 4 0 0 1 587.6666666666666 58.75999999999999 H625.6666666666666 A4 4 0 0 1 629.6666666666666 62.75999999999999 V278.0 Z" fill="#8b7cf6"><title>Bars · Decimation off: 156.6 ms</title></path>
<text x="606.7" y="51.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">156.6</text>
<path d="M631.6666666666666 278.0 V196.88 A4 4 0 0 1 635.6666666666666 192.88 H673.6666666666666 A4 4 0 0 1 677.6666666666666 196.88 V278.0 Z" fill="#00a9ab"><title>Bars · Decimation on: 60.8 ms</title></path>
<text x="654.7" y="185.9" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">60.8</text>
<text x="630.7" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Bars</text>
<line x1="54" y1="278" x2="746" y2="278" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
</svg>
```

Turn it on with `chart.isDecimationEnabled = true` when a lot of entries are on screen at once and each costs a draw call of its own: a bar chart, a line with a color per segment, a line with circles. At 100,000 bars it is the difference between 310 ms and 115 ms. Leave it off for a plain single color line, where it costs about half as much again as it saves.

## Against 3.1.0

The same scenarios, measured the same way on the same device, against the last Java release. Both sides draw the same picture: same data, same chart size, same viewport, no value labels, no circles. Decimation has no equivalent in 3.1.0, so 4.0 runs with it off here.

| Scenario | 3.1.0 | 4.0 | |
| --- | --- | --- | --- |
| Line, 10,000 | 10.7 ms | 9.1 ms | 1.18x faster |
| Line, 50,000 | 46.2 ms | 39.8 ms | 1.16x faster |
| Line, 100,000 | 91.4 ms | 76.4 ms | 1.20x faster |
| Bars, 50,000 | 97.9 ms | 156.6 ms | 1.60x slower |
| Bars, 100,000 | 176.0 ms | 310.3 ms | 1.76x slower |
| Bars, 50,000, decimation on | 97.9 ms | 60.8 ms | 1.61x faster |
| Bars, 100,000, decimation on | 176.0 ms | 114.5 ms | 1.54x faster |

```figure
<svg viewBox="0 0 860 330" width="100%" role="img" aria-label="The same draw in 3.1.0 and 4.0, in milliseconds" style="max-width:860px;height:auto;display:block;margin:0 auto 6px">
<title>The same draw in 3.1.0 and 4.0, in milliseconds</title>
<rect x="54" y="14" width="11" height="11" rx="3" fill="#8b7cf6"/>
<text x="71" y="24" fill="rgba(255,255,255,0.78)" font-size="13">3.1.0</text>
<rect x="113.0" y="14" width="11" height="11" rx="3" fill="#00a9ab"/>
<text x="130.0" y="24" fill="rgba(255,255,255,0.78)" font-size="13">4.0</text>
<line x1="54" y1="278.0" x2="846" y2="278.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="282.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">0</text>
<line x1="54" y1="222.0" x2="846" y2="222.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="226.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">80</text>
<line x1="54" y1="166.0" x2="846" y2="166.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="170.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">160</text>
<line x1="54" y1="110.0" x2="846" y2="110.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="114.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">240</text>
<line x1="54" y1="54.0" x2="846" y2="54.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="58.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">320</text>
<path d="M73.0 278.0 V274.51 A4 4 0 0 1 77.0 270.51 H115.0 A4 4 0 0 1 119.0 274.51 V278.0 Z" fill="#8b7cf6"><title>Line|10,000 · 3.1.0: 10.7 ms</title></path>
<text x="96.0" y="263.5" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">10.7</text>
<path d="M121.0 278.0 V275.63 A4 4 0 0 1 125.0 271.63 H163.0 A4 4 0 0 1 167.0 275.63 V278.0 Z" fill="#00a9ab"><title>Line|10,000 · 4.0: 9.1 ms</title></path>
<text x="144.0" y="264.6" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">9.1</text>
<text x="120.0" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Line</text>
<text x="120.0" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">10,000</text>
<path d="M205.0 278.0 V249.66 A4 4 0 0 1 209.0 245.66 H247.0 A4 4 0 0 1 251.0 249.66 V278.0 Z" fill="#8b7cf6"><title>Line|50,000 · 3.1.0: 46.2 ms</title></path>
<text x="228.0" y="238.7" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">46.2</text>
<path d="M253.0 278.0 V254.14000000000001 A4 4 0 0 1 257.0 250.14000000000001 H295.0 A4 4 0 0 1 299.0 254.14000000000001 V278.0 Z" fill="#00a9ab"><title>Line|50,000 · 4.0: 39.8 ms</title></path>
<text x="276.0" y="243.1" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">39.8</text>
<text x="252.0" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Line</text>
<text x="252.0" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">50,000</text>
<path d="M337.0 278.0 V218.01999999999998 A4 4 0 0 1 341.0 214.01999999999998 H379.0 A4 4 0 0 1 383.0 218.01999999999998 V278.0 Z" fill="#8b7cf6"><title>Line|100,000 · 3.1.0: 91.4 ms</title></path>
<text x="360.0" y="207.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">91.4</text>
<path d="M385.0 278.0 V228.51999999999998 A4 4 0 0 1 389.0 224.51999999999998 H427.0 A4 4 0 0 1 431.0 228.51999999999998 V278.0 Z" fill="#00a9ab"><title>Line|100,000 · 4.0: 76.4 ms</title></path>
<text x="408.0" y="217.5" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">76.4</text>
<text x="384.0" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Line</text>
<text x="384.0" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">100,000</text>
<path d="M469.0 278.0 V213.47 A4 4 0 0 1 473.0 209.47 H511.0 A4 4 0 0 1 515.0 213.47 V278.0 Z" fill="#8b7cf6"><title>Bars|50,000 · 3.1.0: 97.9 ms</title></path>
<text x="492.0" y="202.5" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">97.9</text>
<path d="M517.0 278.0 V172.38 A4 4 0 0 1 521.0 168.38 H559.0 A4 4 0 0 1 563.0 172.38 V278.0 Z" fill="#00a9ab"><title>Bars|50,000 · 4.0: 156.6 ms</title></path>
<text x="540.0" y="161.4" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">156.6</text>
<text x="516.0" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Bars</text>
<text x="516.0" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">50,000</text>
<path d="M601.0 278.0 V158.79999999999998 A4 4 0 0 1 605.0 154.79999999999998 H643.0 A4 4 0 0 1 647.0 158.79999999999998 V278.0 Z" fill="#8b7cf6"><title>Bars|100,000 · 3.1.0: 176.0 ms</title></path>
<text x="624.0" y="147.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">176.0</text>
<path d="M649.0 278.0 V64.78999999999999 A4 4 0 0 1 653.0 60.78999999999999 H691.0 A4 4 0 0 1 695.0 64.78999999999999 V278.0 Z" fill="#00a9ab"><title>Bars|100,000 · 4.0: 310.3 ms</title></path>
<text x="672.0" y="53.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">310.3</text>
<text x="648.0" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Bars</text>
<text x="648.0" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">100,000</text>
<path d="M733.0 278.0 V158.79999999999998 A4 4 0 0 1 737.0 154.79999999999998 H775.0 A4 4 0 0 1 779.0 158.79999999999998 V278.0 Z" fill="#8b7cf6"><title>Bars 100,000|decimation on · 3.1.0: 176.0 ms</title></path>
<text x="756.0" y="147.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">176.0</text>
<path d="M781.0 278.0 V201.85000000000002 A4 4 0 0 1 785.0 197.85000000000002 H823.0 A4 4 0 0 1 827.0 201.85000000000002 V278.0 Z" fill="#00a9ab"><title>Bars 100,000|decimation on · 4.0: 114.5 ms</title></path>
<text x="804.0" y="190.9" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">114.5</text>
<text x="780.0" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Bars 100,000</text>
<text x="780.0" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">decimation on</text>
<line x1="54" y1="278" x2="846" y2="278" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
</svg>
```

Lines are about a fifth quicker. Bars at their full extent are slower than they were, which is worth saying plainly rather than leaving out: a 4.0 bar chart that draws every entry does more work than 3.x did. Decimation more than covers it, and then some, but it has to be asked for. If you draw tens of thousands of bars at once, turn it on.

### What to expect on a phone

A 60 Hz frame is 16.67 ms and a chart realistically gets about half of it. On the numbers above that is roughly 10,000 line entries or 2,500 bars on the emulator, and a phone is slower again: expect a recent high-end device to be 2 to 3 times slower and a mid-range one 3 to 5 times.

As a cross check away from the bitmap, the example app's performance screen with 30,000 points on a real hardware accelerated surface renders whole frames at a median of 32 ms while panning, which is the same order as the 24 ms the bitmap measurement implies for that size. The two ways of measuring agree.

These figures replace earlier ones in this chapter that were measured differently and could not be reproduced.

## Against other charting libraries

The Compose charting libraries that come up most often, measured the same way on the same device. Every library gets a view of the same size and the same entries, and is configured to show the whole series at once rather than the scrolling window most of them show by default. The ranges below cover what five runs of each produced, one library per process, with the frame rate each draw time allows beside it.

| Library | 10,000 | 50,000 | |
| --- | --- | --- | --- |
| MPAndroidChart 4.0 | 8-10 ms · 100-125 fps | 30-40 ms · 25-33 fps | |
| KoalaPlot 0.12.1 | 13-17 ms · 59-77 fps | 60-75 ms · 13-17 fps | about 2x slower |
| Vico 2.5.2 | 20-25 ms · 40-50 fps | 85-90 ms · 11-12 fps | about 2.5x slower |
| YCharts 2.1.0 | 30-36 ms · 28-33 fps | 170-210 ms · 5-6 fps | 4x to 5x slower |

```figure
<svg viewBox="0 0 760 330" width="100%" role="img" aria-label="Draw time by charting library, in milliseconds" style="max-width:760px;height:auto;display:block;margin:0 auto 6px">
<title>Draw time by charting library, in milliseconds</title>
<rect x="54" y="14" width="11" height="11" rx="3" fill="#00a9ab"/>
<text x="71" y="24" fill="rgba(255,255,255,0.78)" font-size="13">10,000 entries</text>
<rect x="179.60000000000002" y="14" width="11" height="11" rx="3" fill="#8b7cf6"/>
<text x="196.60000000000002" y="24" fill="rgba(255,255,255,0.78)" font-size="13">50,000 entries</text>
<line x1="54" y1="278.0" x2="746" y2="278.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="282.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">0</text>
<line x1="54" y1="227.1" x2="746" y2="227.1" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="231.1" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">50</text>
<line x1="54" y1="176.2" x2="746" y2="176.2" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="180.2" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">100</text>
<line x1="54" y1="125.3" x2="746" y2="125.3" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="129.3" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">150</text>
<line x1="54" y1="74.4" x2="746" y2="74.4" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="44" y="78.4" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">200</text>
<path d="M93.5 278.0 V272.8363636363636 A4 4 0 0 1 97.5 268.8363636363636 H135.5 A4 4 0 0 1 139.5 272.8363636363636 V278.0 Z" fill="#00a9ab"><title>MPAndroidChart|4.0 · 10,000 entries: 8-10 ms</title></path>
<text x="116.5" y="261.8" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">8-10</text>
<path d="M141.5 278.0 V246.36363636363637 A4 4 0 0 1 145.5 242.36363636363637 H183.5 A4 4 0 0 1 187.5 246.36363636363637 V278.0 Z" fill="#8b7cf6"><title>MPAndroidChart|4.0 · 50,000 entries: 30-40 ms</title></path>
<text x="164.5" y="235.4" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">30-40</text>
<text x="140.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">MPAndroidChart</text>
<text x="140.5" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">4.0</text>
<path d="M266.5 278.0 V266.72727272727275 A4 4 0 0 1 270.5 262.72727272727275 H308.5 A4 4 0 0 1 312.5 266.72727272727275 V278.0 Z" fill="#00a9ab"><title>KoalaPlot|0.12.1 · 10,000 entries: 13-17 ms</title></path>
<text x="289.5" y="255.7" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">13-17</text>
<path d="M314.5 278.0 V213.27272727272725 A4 4 0 0 1 318.5 209.27272727272725 H356.5 A4 4 0 0 1 360.5 213.27272727272725 V278.0 Z" fill="#8b7cf6"><title>KoalaPlot|0.12.1 · 50,000 entries: 60-75 ms</title></path>
<text x="337.5" y="202.3" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">60-75</text>
<text x="313.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">KoalaPlot</text>
<text x="313.5" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">0.12.1</text>
<path d="M439.5 278.0 V259.0909090909091 A4 4 0 0 1 443.5 255.0909090909091 H481.5 A4 4 0 0 1 485.5 259.0909090909091 V278.0 Z" fill="#00a9ab"><title>Vico|2.5.2 · 10,000 entries: 20-25 ms</title></path>
<text x="462.5" y="248.1" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">20-25</text>
<path d="M487.5 278.0 V192.9090909090909 A4 4 0 0 1 491.5 188.9090909090909 H529.5 A4 4 0 0 1 533.5 192.9090909090909 V278.0 Z" fill="#8b7cf6"><title>Vico|2.5.2 · 50,000 entries: 85-90 ms</title></path>
<text x="510.5" y="181.9" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">85-90</text>
<text x="486.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">Vico</text>
<text x="486.5" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">2.5.2</text>
<path d="M612.5 278.0 V248.4 A4 4 0 0 1 616.5 244.4 H654.5 A4 4 0 0 1 658.5 248.4 V278.0 Z" fill="#00a9ab"><title>YCharts|2.1.0 · 10,000 entries: 30-36 ms</title></path>
<text x="635.5" y="237.4" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">30-36</text>
<path d="M660.5 278.0 V88.54545454545453 A4 4 0 0 1 664.5 84.54545454545453 H702.5 A4 4 0 0 1 706.5 88.54545454545453 V278.0 Z" fill="#8b7cf6"><title>YCharts|2.1.0 · 50,000 entries: 170-210 ms</title></path>
<text x="683.5" y="77.5" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="middle" font-variant-numeric="tabular-nums">170-210</text>
<text x="659.5" y="300.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">YCharts</text>
<text x="659.5" y="316.0" fill="rgba(255,255,255,0.5)" font-size="12.5" text-anchor="middle">2.1.0</text>
<line x1="54" y1="278" x2="746" y2="278" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
</svg>
```

Take it as an order of magnitude rather than a league table, which is why the numbers above are ranges. The four do not draw quite the same picture: the pixels each one covered differ by up to half again, KoalaPlot draws a much denser grid than the rest, and none of them was tuned beyond being told to show everything.

Two things about measuring this produced convincing nonsense before they were caught, and both are worth knowing if you run your own comparison. A chart that has not been handed its data yet covers an empty canvas in microseconds, which reads as a spectacular result, so a run has to prove it put something on screen before its time counts. And a library drawn for the first time since it was installed came out four times slower than on its next run, because the device keeps what it compiled between launches.

## Value labels are the most expensive thing on screen

Every drawn label runs your value formatter and then `Canvas.drawText`, far more work per entry than a line segment, so the library has a brake built in. Values are drawn only while

```text
data.entryCount < chart.maxVisibleCount * viewPortHandler.scaleX
```

Three details are easy to get wrong:

- `entryCount` is the sum over every data set of the chart, not the number of entries in view.
- `maxVisibleCount` is 100 by default, so a chart holding 500 entries shows no labels at all until the user has zoomed past 5x.
- `scaleX` is the current horizontal zoom, 1 when fully zoomed out. `HorizontalBarChart` compares against `scaleY` instead.

When you never want labels, say so on the data set rather than relying on the count. Both of these default to true:

```kotlin
set.isDrawValuesEnabled = false
set.isDrawIconsEnabled = false
```

> Pie and radar charts report their own entry count as `maxVisibleCount`, so the check always passes and labels are always drawn. There the data set switches are the only way to turn them off.

## Circles, and why a large radius costs more

A line data set draws a circle at every visible entry unless you say otherwise:

```kotlin
set.isDrawCirclesEnabled = false
```

Circles are stamped from one cached bitmap per circle color, rebuilt only when the colors or the radii change, so steady data costs nothing extra. The radius matters twice over: each bitmap is `circleRadius * 2.1` pixels square, and each stamp blends that many pixels onto the canvas, so doubling it roughly quadruples both. The default is 4 dp, and values below 1 are refused.

## Curve mode and the offscreen bitmap

`LineDataSet.Mode.LINEAR` and `STEPPED` fill one reused float array with the visible segments and hand the whole thing to a single `Canvas.drawLines` call. `CUBIC_BEZIER` and `HORIZONTAL_BEZIER` build a `Path` with one `cubicTo` per segment, which is more work per entry and cannot be batched the same way.

```kotlin
set.mode = LineDataSet.Mode.LINEAR
```

A linear line with more than one color also loses the batching, because each segment is drawn in its own call so it can carry its own color.

Both curve modes and any dashed line draw onto an offscreen bitmap the size of the chart, which the renderer composes onto the canvas at the end of the pass; a plain solid linear line goes straight onto the chart canvas instead. Dashing is the cheapest thing here to give up, with `set.disableDashedLine()`.

## Hardware acceleration

One property switches the view between a hardware and a software layer:

```kotlin
chart.isHardwareAccelerationEnabled = true
```

That is all it does. A fresh chart has no layer at all, so the property reads false even though the window is already hardware accelerated.

Worth keeping apart from that property is whether the drawing reaches the GPU, because a chart drawn to a hardware accelerated window and one drawn to a software `Canvas` behave nothing alike. A window is hardware accelerated by default: the draw is recorded into a display list and the GPU rasterises it, so one batched call is nearly free however many points it covers. On a software canvas, which is what `toBitmap()` and a software layer give you, the CPU fills every pixel itself. That is exactly why reducing the point count can fail to help.

A hardware layer earns its keep only for a chart whose content does not change while the chart itself moves, because the view is rendered into a texture once and reused while you scroll or fade it. A chart that invalidates on every frame redraws into that texture anyway and only pays for it.

## Clipping

| Property | Default | What it does |
| --- | --- | --- |
| `isClipDataToContentEnabled` | `true` | Clips the data, the grid lines and the highlights to the content rectangle |
| `isClipValuesToContentEnabled` | `false` | Clips the value labels as well |

Turn the first off when a thick line or a large shape near the edge is being cut in half. The second costs one canvas save and restore per frame, which is nothing next to drawing the labels themselves, so turn it on for looks rather than for speed.

## Thin the data before you draw it

When a series has more points than the screen has pixels, most of them cannot be seen. Every chart with an x axis can leave those out while it draws, and does so by default:

```kotlin
chart.isDecimationEnabled = false
```

While it is on, the renderers keep the first, the lowest, the highest and the last entry of each pixel column and skip the rest, so peaks and troughs survive and the shape stays the same. On a line chart it also leaves out the circles another circle would have covered. Your data is untouched; this happens on the way to the canvas.

Whether it is worth its own cost depends entirely on what one entry costs to draw, and the numbers above say it plainly. At 50,000 entries a line with a color per segment goes from 147.3 ms to 62.2 ms and a bar chart from 156.6 ms to 60.8 ms, because in both a single entry is a draw call of its own. A plain line goes the other way, from 39.8 ms to 62.4 ms, because there the reduction pass costs more than the one batched call it saves. Turn it on for bars and for a line with more than one color; leave it off, as it comes, for a plain line.

`Approximator` is the other way to thin a series, once while you build the data rather than on every draw. It takes a flat `FloatArray` of `x0, y0, x1, y1, ...` and a tolerance, reduces it with the Douglas-Peucker algorithm, and returns the same layout:

```kotlin
val reduced = Approximator().reduceWithDouglasPeucker(points, 2f)
```

The tolerance is in the same unit as the points you pass in. Nothing in the library calls it for you, so run it on a background thread while the data is being built.

## Do not allocate while drawing

The renderers run inside `onDraw`, and the library goes out of its way not to allocate there: the buffers are refilled in place, and `MPPointF`, `MPPointD` and `FSize` come from shared `ObjectPool` instances.

Those buffers are sized from the total entry count rather than the visible one, so fifty thousand points on a single colored line reserve about 1.6 MB for as long as the set is assigned. That is the real cost of a large total count: memory, not frame time.

Your own code is the other half:

- **Formatters.** `getFormattedValue` is called for every drawn label on every frame. Build the `NumberFormat` or `SimpleDateFormat` once as a property of the formatter, never inside the function. [Formatters](/mpandroidchart/docs/formatters/) shows the shape.
- **Markers.** `refreshContent` runs before every marker draw, so for a marker that follows a drag it runs per frame. Keep the views and change only their content. [Markers](/mpandroidchart/docs/markers/) has the details.

Building the data is plain object work with no view involved, so do it on a background thread. Only assigning `chart.data` and calling `chart.notifyDataSetChanged()` have to happen on the main thread.

## Measure, do not guess

Every chart can write its internals to logcat under the tag `MPAndroidChart`:

```kotlin
chart.isLogEnabled = true
```

On the axis charts the useful line is printed at the end of each draw:

```text
Drawtime: 6 ms, average: 7 ms, cycles: 42
```

`chart.resetTracking()` zeroes the total and the cycle count, which is what you call right before the interaction you actually want to time.

The example app has two screens built for exactly this, Line chart performance and Bar chart performance. Each shows what the chart's own draw cost, the worst frame of the last second, and how many entries are on screen, with switches for the entry count, decimation, value labels and the label limit, plus the line shape, circles, fill and a color per segment on one and stacking, rounded corners and bar shadows on the other. The tables above come from them.

Two caveats. Logging itself costs time on every draw, so the numbers are a comparison between settings rather than an absolute. And the draw time does not include `notifyDataSetChanged`, which is where the axis recalculation happens. For anything beyond a rough comparison, record a trace with the Android Studio profiler.

## The settings that pay off most

Roughly in order of what they buy, with the measured figures where there are any. All of them are emulator numbers.

| Setting | What it buys |
| --- | --- |
| `chart.setVisibleXRangeMaximum(n)` | The biggest lever there is. Cost follows the points on screen, not the points you hold: 10,000 on screen draws in 9.1 ms where 100,000 takes 76.4 ms. A million point set scrolls perfectly well at a sensible zoom. |
| A single `color` on a line set | 39.8 ms against 147.3 ms at 50,000 entries. One color is one batched draw call; a color per segment is a call per segment. |
| `set.isDrawValuesEnabled = false` | Removes the text pass. `chart.maxVisibleCount` decides the zoom at which labels start appearing, so raising it costs you the same way. |
| `set.isDrawCirclesEnabled = false` | Removes one bitmap stamp per visible point. |
| `chart.isDecimationEnabled = true` | Off as it comes. At 50,000 entries it takes bars from 156.6 ms to 60.8 ms and a line with a color per segment from 147.3 ms to 62.2 ms. It costs a plain line 39.8 ms against 62.4, so leave it off there. |
| `set.mode = LineDataSet.Mode.LINEAR` | One batched call instead of a path with a segment per entry. |
| `set.disableDashedLine()` | Takes the line off the offscreen bitmap pass. |
| Leaving `isDrawFilledEnabled` off | A filled line rebuilds a path in chunks of 128 entries every frame. |
| `chart.isDrawBarShadowEnabled = false` | One fewer rectangle per bar. |
| Batching appends | A live feed that calls `notifyDataSetChanged()` per entry pays about 0.4 ms each time. Append what arrived, then notify once. |

None of these is worth applying blindly. Turn on `isLogEnabled`, note the average, change one thing, and compare.

## Where to go next

- [Dynamic and realtime data](/mpandroidchart/docs/dynamic-data/) for adding and dropping entries while the chart is on screen.
- [Modifying the viewport](/mpandroidchart/docs/viewport/) for the zoom and scroll limits that decide the visible range.
- [Custom renderers](/mpandroidchart/docs/custom-renderers/) if you want to change what a draw pass does.
- [Miscellaneous](/mpandroidchart/docs/miscellaneous/) for the object pools and the logging switch.
