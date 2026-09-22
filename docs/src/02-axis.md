# The axis

The settings that both axes share: which parts are drawn, how many labels there are, how the value range is chosen, and the lines you can put on top.

`AxisBase` is the base class of `XAxis` and `YAxis`. Everything on this page works on either one.

```kotlin
val xAxis = chart.xAxis
val leftAxis = chart.axisLeft
val rightAxis = chart.axisRight
```

## What an axis is made of

An axis can draw four things, each of which can be turned off on its own.

- The **labels**, one per computed axis value.
- The **axis line**, drawn along the edge of the content area, parallel to the labels.
- The **grid lines**, one running across the content area from each label.
- The **limit lines** you add yourself, for a target or a threshold.

```figure
<svg viewBox="0 0 760 330" width="100%" role="img" aria-label="The four things an axis draws" style="max-width:760px;height:auto;display:block;margin:0 auto 6px">
<title>The four things an axis draws</title>
<line x1="170.0" y1="103.5" x2="600.0" y2="103.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="170.0" y1="149.0" x2="600.0" y2="149.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="170.0" y1="194.5" x2="600.0" y2="194.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="256.0" y1="58.0" x2="256.0" y2="240.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="256.0" y="260.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="middle">10</text>
<line x1="342.0" y1="58.0" x2="342.0" y2="240.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="342.0" y="260.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="middle">20</text>
<line x1="428.0" y1="58.0" x2="428.0" y2="240.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="428.0" y="260.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="middle">30</text>
<line x1="514.0" y1="58.0" x2="514.0" y2="240.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="514.0" y="260.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="middle">40</text>
<text x="158.0" y="244.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">0</text>
<text x="158.0" y="198.5" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">20</text>
<text x="158.0" y="153.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">40</text>
<text x="158.0" y="107.5" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">60</text>
<text x="158.0" y="62.0" fill="rgba(255,255,255,0.5)" font-size="12" text-anchor="end">80</text>
<path d="M170.0 178.1 L209.1 146.1 L248.2 166.5 L287.3 117.0 L326.4 141.7 L365.5 96.6 L404.5 128.6 L443.6 154.8 L482.7 137.4 L521.8 108.2 L560.9 125.7 L600.0 163.6" fill="none" stroke="#00a9ab" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
<line x1="170.0" y1="98.0" x2="600.0" y2="98.0" stroke="#8b7cf6" stroke-width="1.5" stroke-dasharray="6 4"/>
<text x="180.0" y="90.0" fill="#8b7cf6" font-size="11.5" text-anchor="start">Target</text>
<line x1="170.0" y1="58.0" x2="170.0" y2="240.0" stroke="rgba(255,255,255,0.22)" stroke-width="1.5"/>
<line x1="170.0" y1="240.0" x2="600.0" y2="240.0" stroke="rgba(255,255,255,0.22)" stroke-width="1.5"/>
<line x1="602.0" y1="98.0" x2="614.0" y2="98.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<text x="620.0" y="102.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="start">Limit line</text>
<line x1="602.0" y1="149.0" x2="614.0" y2="149.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<text x="620.0" y="153.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="start">Grid lines</text>
<line x1="602.0" y1="240.0" x2="614.0" y2="240.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<text x="620.0" y="244.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="start">Axis line</text>
<text x="170.0" y="286.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="start">Labels</text>
<text x="158.0" y="44.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="end">Labels</text>
</svg>
```

| Property | Meaning | Default |
| --- | --- | --- |
| `isEnabled` | Draws the axis at all. False hides every part of it, whatever the other settings say. | `true` |
| `isDrawLabelsEnabled` | Draws the labels. Grid and axis line are unaffected. | `true` |
| `isDrawAxisLineEnabled` | Draws the line along the axis. | `true` |
| `isDrawGridLinesEnabled` | Draws the grid lines. | `true` |

```kotlin
chart.xAxis.isDrawGridLinesEnabled = false
chart.axisRight.isEnabled = false
```

## How many labels

`labelCount` is a wish, not a promise. The renderer picks a round interval near `range / labelCount`, so you usually get a count close to what you asked for, with readable values. On the x axis it also keeps the interval at least one label wide, so long labels thin themselves out instead of overlapping.

| Property | Meaning | Default |
| --- | --- | --- |
| `labelCount` | Number of labels you want, clamped to `axisMinLabels`..`axisMaxLabels`. | `6` |
| `isForceLabelsEnabled` | Draws exactly `labelCount` labels, evenly spread. | `false` |
| `axisMinLabels` | Lower bound applied to `labelCount`. | `2` |
| `axisMaxLabels` | Upper bound applied to `labelCount`. | `25` |

Forcing the count gives you an exact number of labels at the price of uneven values, which is what you want when you fixed the range yourself. A granularity still wins: if the forced interval would fall below it, the axis keeps the granularity and draws fewer labels.

```kotlin
chart.axisLeft.axisMinimum = 30f
chart.axisLeft.axisMaximum = 110f
chart.axisLeft.labelCount = 5
chart.axisLeft.isForceLabelsEnabled = true
```

> The old `setLabelCount(count, force)` is gone. `labelCount` and `isForceLabelsEnabled` are two independent properties now, and you can change either one without touching the other.

## Granularity

Granularity is the smallest interval the axis is allowed to use. Without it, zooming in keeps halving the interval until the same label appears twice, for example three labels reading "4" because the real values are 4.0, 4.3 and 4.6 and the axis formats whole numbers.

```kotlin
chart.xAxis.granularity = 1f
```

Assigning `granularity` also sets `isGranularityEnabled` to `true`, so one line is enough. The property starts at `1`, but the feature is off until you enable it. You can also enable it on its own with `isGranularityEnabled = true` to use the default interval of 1.

## The value range

By default both ends of the range are computed from the data whenever the data changes. Assign either end to fix it.

```kotlin
chart.axisLeft.axisMinimum = 0f     // always start at zero
chart.axisLeft.axisMaximum = 100f
```

An assignment marks that end custom: `isAxisMinCustom` and `isAxisMaxCustom` read `true`, and the value survives every later recalculation. To hand an end back to the chart, call `resetAxisMinimum()` or `resetAxisMaximum()`. The change takes effect the next time the range is computed, which is the next `notifyDataSetChanged()` or the next assignment of `chart.data`.

`spaceMin` and `spaceMax` pad a computed end in value space. They are ignored for an end you fixed yourself.

```kotlin
chart.xAxis.spaceMin = 0.5f   // half a slot before the first entry
chart.xAxis.spaceMax = 0.5f
```

`BarChart`, `ScatterChart` and `CandleStickChart` already set both to `0.5` on their x axis, which is what keeps the outer bars and points off the edge.

> `spaceMin` and `spaceMax` only work on the x axis. The y axis computes its range differently and uses `spaceTop` and `spaceBottom`, which are percentages. See [the y axis](/mpandroidchart/docs/yaxis/).

`axisRange` is the distance between the two ends and is updated whenever either end changes.

## Text

The label text settings come from `ComponentBase` and are shared with the legend and the description.

| Property | Meaning | Default |
| --- | --- | --- |
| `textSize` | Label size in dp, clamped to 6..24. | `10` |
| `textColor` | Label color. | black |
| `typeface` | `Typeface` for the labels, or null for the default. | `null` |
| `xOffset` | Horizontal space in dp between the labels and what they sit next to. | `5` |
| `yOffset` | Vertical space in dp between the labels and what they sit next to. | `4` on the x axis, `0` on the y axis |

```kotlin
chart.axisLeft.apply {
    textSize = 11f
    textColor = Color.parseColor("#8A93A6")
    typeface = ResourcesCompat.getFont(context, R.font.inter)
}
```

## Grid lines and the axis line

Both are plain lines with a color, a width in dp and an optional dash pattern.

| Property | Meaning | Default |
| --- | --- | --- |
| `gridColor` | Color of the grid lines. | gray |
| `gridLineWidth` | Grid line width in dp. | `0.5` |
| `axisLineColor` | Color of the axis line. | gray |
| `axisLineWidth` | Axis line width in dp. | `0.5` |
| `isDrawGridLinesBehindDataEnabled` | Draws the grid behind the data instead of on top of it. | `true` |

```kotlin
chart.axisLeft.apply {
    gridColor = Color.parseColor("#1F2A3C")
    gridLineWidth = 1f
    isDrawAxisLineEnabled = false
    enableGridDashedLine(10f, 10f, 0f)
}
```

`enableGridDashedLine(lineLength, spaceLength, phase)` takes pixels: the length of a dash, the gap after it, and where in the pattern to start (pass `0`). `disableGridDashedLine()` goes back to a solid line and `isGridDashedLineEnabled` tells you which one is active. The axis line has the same three functions under `enableAxisLineDashedLine`, `disableAxisLineDashedLine` and `isAxisLineDashedLineEnabled`.

## Limit lines

A `LimitLine` is a line at a fixed value with an optional label. On a y axis it runs horizontally, on an x axis vertically. Use it for a target, a threshold or an average.

```kotlin
val limit = LimitLine(140f, "Critical").apply {
    lineWidth = 2f
    lineColor = Color.RED
    textSize = 11f
    labelPosition = LimitLine.LimitLabelPosition.RIGHT_TOP
    enableDashedLine(10f, 10f, 0f)
}

chart.axisLeft.addLimitLine(limit)
```

| Property | Meaning | Default |
| --- | --- | --- |
| `limit` | The value the line sits at. Set in the constructor. | |
| `label` | Text next to the line. An empty string draws no label. | `""` |
| `lineWidth` | Line width in dp, clamped to 0.2..12. | `1` |
| `lineColor` | Line color. | light red |
| `labelPosition` | Corner the label is drawn at. | `RIGHT_TOP` |
| `textStyle` | Paint style of the label text. | `FILL_AND_STROKE` |
| `isEnabled` | Draws this line. False skips it without removing it. | `true` |

The four label positions are `LEFT_TOP`, `LEFT_BOTTOM`, `RIGHT_TOP` and `RIGHT_BOTTOM`. For a horizontal line on a y axis, left and right pick the end of the line and top and bottom pick the side of it. For a vertical line on an x axis it is the other way around: left and right pick the side, top and bottom pick the end. The radar chart draws limit lines on its y axis only, and never draws their labels.

`limitLines` is the list of lines on the axis, in the order they were added. `removeLimitLine(line)` takes one out and `removeAllLimitLines()` clears them. Adding more than six logs a warning, because past that point they stop being readable.

By default limit lines are drawn on top of the data. Put them behind it with:

```kotlin
chart.axisLeft.isDrawLimitLinesBehindDataEnabled = true
```

## Formatting the labels

`valueFormatter` turns an axis value into label text. Set any `IAxisValueFormatter`, which is a `fun interface`, so a lambda works:

```kotlin
chart.axisLeft.valueFormatter = IAxisValueFormatter { value, _ -> "${value.toInt()} €" }
```

Until you set one, the axis returns a `DefaultAxisValueFormatter` built from the computed `decimals`. [Formatting values](/mpandroidchart/docs/formatters/) covers the built in formatters and how to write your own.

## Values the axis computes

The axis renderer fills these on every draw pass, from the visible range. You can read them, but not assign them.

| Property | Meaning |
| --- | --- |
| `entries` | The values labels and grid lines are drawn at. The array is only ever grown, so read the first `entryCount` of them. |
| `entryCount` | How many of them there are. |
| `centeredEntries` | The midpoints between neighbouring entries, used when labels are centered. |
| `decimals` | Decimal digits the default formatter uses, derived from the label interval. |
| `longestLabel` | The formatted label with the most characters. |

They are empty until the chart has data and has been laid out, so reading them from `onCreate` gives you nothing. `getFormattedLabel(index)` returns the text of one entry, or an empty string for an index outside the range.

## Next

- [The x axis](/mpandroidchart/docs/xaxis/) for positions, rotation and index based labels.
- [The y axis](/mpandroidchart/docs/yaxis/) for the left and right axis, padding and the zero line.
- [Formatting values](/mpandroidchart/docs/formatters/) for label and value text.
