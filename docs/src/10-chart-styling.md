# Chart specific styling

What each chart type adds on top of the settings all charts share, from bar shadows and the pie hole to the web of a radar chart and the draw order of a combined chart.

Everything below is set on the chart view. Colors, line widths and shapes belong to the data set instead, see [DataSet subclasses](/mpandroidchart/docs/dataset-subclasses/).

## Shared by the charts with an x axis

`LineChart`, `BarChart`, `ScatterChart`, `CandleStickChart`, `BubbleChart` and `CombinedChart` all extend `BarLineChartBase` and share two settings that the round charts do not have.

```kotlin
chart.isAutoScaleMinMaxEnabled = true
chart.isKeepPositionOnRotation = true
```

| Property | Meaning | Default |
| --- | --- | --- |
| `isAutoScaleMinMaxEnabled` | Recalculate both y axes on every draw from the entries currently in view. Useful for price charts, where a zoomed range would otherwise look flat | `false` |
| `isKeepPositionOnRotation` | Keep the top left corner on the same values when the view is resized, for example on a device rotation | `false` |

The zoom, drag and axis settings they share are covered in [Interaction with the chart](/mpandroidchart/docs/interaction/) and [The axis](/mpandroidchart/docs/axis/).

## BarChart

```kotlin
chart.isDrawBarShadowEnabled = true
chart.isDrawValueAboveBarEnabled = true
chart.isFitBarsEnabled = true
chart.isHighlightFullBarEnabled = false
```

| Property | Meaning | Default |
| --- | --- | --- |
| `isDrawBarShadowEnabled` | Draw a grey column behind each bar over the full height of the content area. It costs a lot of drawing time | `false` |
| `isDrawValueAboveBarEnabled` | Put the value label above the top of the bar instead of inside it | `true` |
| `isFitBarsEnabled` | Widen the x axis by half a bar width on each side so the first and last bar are fully visible | `false` |
| `isHighlightFullBarEnabled` | A tap highlights the whole stacked bar instead of the single stack value under the finger | `false` |

`isFitBarsEnabled` takes effect on the next `notifyDataSetChanged()`. The shadow color comes from the data set, `set.barShadowColor`.

Bars of several data sets are placed side by side with `groupBars`, which also changes the bar width and the x values of the entries and refreshes the chart:

```kotlin
chart.groupBars(fromX = 0f, groupSpace = 0.3f, barSpace = 0.05f)
```

`chart.getBarBounds(entry)` gives you the pixel rectangle a bar is drawn in, which is what you need to place a view or a tooltip over it. The overload taking a `RectF` avoids the allocation in hot code.

## HorizontalBarChart

`HorizontalBarChart` is a `BarChart` with the bars lying on their side, so everything in the section above applies unchanged. What changes is where the axes end up on screen.

- The x axis runs down the left or right edge and labels the bars.
- The two y axes run along the top and the bottom and carry the values, `axisLeft` at the top and `axisRight` at the bottom.
- `XAxis.XAxisPosition.BOTTOM` puts the bar labels on the left, `TOP` on the right and `BOTH_SIDED` on both.
- `isDrawValueAboveBarEnabled` places the value label past the end of the bar rather than above it.

```kotlin
chart.xAxis.position = XAxis.XAxisPosition.BOTTOM
chart.axisRight.isEnabled = false
chart.setExtraOffsets(0f, 0f, 24f, 0f)   // room for the value labels
```

The visible range functions and the touch helpers already account for the swap, so you keep passing x for entries and y for values.

## LineChart

`LineChart` adds no styling of its own. The look of a line is entirely on `LineDataSet`: the line `mode` including cubic and stepped, `cubicIntensity`, `lineWidth`, the circles, dashes, the fill and the highlight indicators.

```kotlin
val set = LineDataSet(entries, "Revenue").apply {
    mode = LineDataSet.Mode.CUBIC_BEZIER
    cubicIntensity = 0.18f
    lineWidth = 3f
    isDrawCirclesEnabled = false
    isDrawFilledEnabled = true
}
```

The one thing worth knowing at chart level is that cubic and dashed lines draw through a cached bitmap the size of the chart, which the chart releases when the view is detached. Straight and stepped lines go onto the chart canvas directly.

## PieChart

The pie is the chart type with the most of its own settings, because the hole, the center text and the slice labels have nowhere else to live.

### The hole and the ring

```kotlin
chart.isDrawHoleEnabled = true
chart.holeRadius = 58f
chart.holeColor = Color.WHITE
chart.transparentCircleRadius = 61f
chart.transparentCircleColor = Color.WHITE
chart.transparentCircleAlpha = 110
```

Both radii are percentages of the pie radius, not pixels. The translucent ring sits around the hole and is only drawn while its radius is larger than the hole radius, so `transparentCircleRadius = 0f` removes it. `isDrawSlicesUnderHoleEnabled` lets the slices continue underneath the hole instead of stopping at its edge.

### The center text

```kotlin
chart.isDrawCenterTextEnabled = true
chart.centerText = "Total\n1,204"
chart.centerTextColor = Color.BLACK
chart.centerTextSize = 12f
chart.centerTextTypeface = typeface
chart.centerTextRadiusPercent = 100f
chart.setCenterTextOffset(0f, -20f)
```

`centerText` is a `CharSequence`, so a `SpannableString` lets you style parts of it. It wraps inside a box whose width is `centerTextRadiusPercent` of the hole diameter, so lowering it makes the text wrap earlier and stay clear of the slices. The offset shifts the text away from the center in dp, positive to the right and downwards, which is what a half pie needs.

### Slice labels and shape

```kotlin
chart.isDrawEntryLabelsEnabled = true
chart.entryLabelColor = Color.WHITE
chart.entryLabelTextSize = 12f
chart.entryLabelTypeface = typeface

chart.isUsePercentValuesEnabled = true
chart.isDrawRoundedSlicesEnabled = true
```

The entry label is the `label` of each `PieEntry`. `isUsePercentValuesEnabled` hands the value formatter a share of the total instead of the raw value, so the labels read as percentages.

Rounded slices need the hole drawn and `isDrawSlicesUnderHoleEnabled` off. While they are on, a highlighted slice is not redrawn at all, so it gets neither the outward shift nor the highlight color.

### Angles and rotation

```kotlin
chart.maxAngle = 180f
chart.rotationAngle = 180f
chart.minAngleForSlices = 8f
chart.isRotationEnabled = false
```

| Property | Meaning | Default |
| --- | --- | --- |
| `maxAngle` | Degrees the whole pie spans, clamped to 90 until 360. 180 gives a half pie | `360` |
| `rotationAngle` | Degrees at which the first slice starts, 0 at 3 o'clock, increasing clockwise | `270` |
| `minAngleForSlices` | Smallest angle a slice is drawn with, clamped to 0 until half of `maxAngle` | `0` |
| `isRotationEnabled` | Whether dragging turns the pie | `true` |

A minimum angle is only applied when every slice still fits at that size, and it takes effect on the next `notifyDataSetChanged()`.

## RadarChart

A radar chart draws each entry on its own spoke and joins the entries of a data set into a polygon. The spokes and the rings between them are the web.

```kotlin
chart.isDrawWebEnabled = true
chart.webLineWidth = 1f
chart.webColor = Color.LTGRAY
chart.webLineWidthInner = 1f
chart.webColorInner = Color.LTGRAY
chart.webAlpha = 100
chart.skipWebLineCount = 1
```

| Property | Meaning | Default |
| --- | --- | --- |
| `webLineWidth` | Width in dp of the lines running from the center outwards | `1.5` |
| `webLineWidthInner` | Width in dp of the rings between the spokes | `0.75` |
| `webColor` | Color of the spokes | grey |
| `webColorInner` | Color of the rings | grey |
| `webAlpha` | Opacity of all web lines from 0 to 255 | `150` |
| `skipWebLineCount` | Spokes and their labels left out between two drawn ones. Negative values become 0 | `0` |
| `isDrawWebEnabled` | Whether the web is drawn at all | `true` |

The chart has a single y axis, reached as `chart.yAxis`, which scales the distance from the center. The x axis labels the spokes.

```kotlin
chart.yAxis.apply {
    axisMinimum = 0f
    axisMaximum = 80f
    labelCount = 5
    isDrawLabelsEnabled = false
}

chart.xAxis.valueFormatter = IAxisValueFormatter { v, _ -> activities[v.toInt()] }
```

Rotation works like on the pie chart: `rotationAngle` decides where the first spoke sits and `isRotationEnabled` decides whether dragging turns the web.

## ScatterChart

The chart adds only the shape catalogue. Which shape is used, how big it is and whether it has a hole is set per data set.

```kotlin
val set = ScatterDataSet(entries, "Batch A").apply {
    setScatterShape(ScatterChart.ScatterShape.TRIANGLE)
    scatterShapeSize = 12f
    scatterShapeHoleRadius = 3f
    scatterShapeHoleColor = Color.WHITE
}
```

`ScatterShape` covers `SQUARE`, `CIRCLE`, `TRIANGLE`, `CROSS`, `X`, `CHEVRON_UP` and `CHEVRON_DOWN`. Squares and circles draw fastest, triangles slowest. For anything else, assign your own `set.shapeRenderer`, see [Custom data sets](/mpandroidchart/docs/custom-datasets/).

## CandleStickChart

The chart adds nothing beyond the shared x and y chart settings. Candles are styled entirely on `CandleDataSet`: the body colors for rising and falling candles, the shadow color and width, whether the body is filled and how wide the bar space is.

```kotlin
val set = CandleDataSet(entries, "Price").apply {
    shadowColor = Color.DKGRAY
    shadowWidth = 0.7f
    decreasingColor = Color.RED
    decreasingPaintStyle = Paint.Style.FILL
    increasingColor = Color.rgb(122, 242, 84)
    increasingPaintStyle = Paint.Style.STROKE
    neutralColor = Color.BLUE
}
```

Once a candle set has a `decreasingColor`, its legend shows two forms, one in the decreasing and one in the increasing color, sharing the set label.

## BubbleChart

The bubble chart also adds nothing of its own. The area of a bubble, not its radius, represents the size carried by each `BubbleEntry`, and the scaling is on the data set.

```kotlin
val set = BubbleDataSet(entries, "Volume").apply {
    isNormalizeSizeEnabled = true
    highlightCircleWidth = 1.5f
}
```

## CombinedChart

A combined chart draws line, bar, scatter, candle and bubble data from one `CombinedData` in the same content area.

```kotlin
chart.drawOrder = listOf(
    CombinedChart.DrawOrder.BAR,
    CombinedChart.DrawOrder.BUBBLE,
    CombinedChart.DrawOrder.CANDLE,
    CombinedChart.DrawOrder.LINE,
    CombinedChart.DrawOrder.SCATTER,
)
chart.isHighlightFullBarEnabled = false
chart.isDrawValueAboveBarEnabled = true
chart.isDrawBarShadowEnabled = false
```

`drawOrder` decides which kind is drawn first and therefore ends up at the back. The default order is bar, bubble, line, candle, scatter. An empty list is ignored.

The three bar properties are the same ones the `BarChart` has, except that `isHighlightFullBarEnabled` defaults to `true` here.

Assigning `chart.data` rebuilds the highlighter and creates one sub renderer per data kind the data actually holds, in the current draw order. You can reach them to change how one kind is drawn:

```kotlin
val combined = chart.renderer as CombinedChartRenderer
combined.subRenderers[0] = MyBarRenderer(chart, chart.animator, chart.viewPortHandler)
```

> Changing `drawOrder` after the data is set does not rebuild the sub renderers on its own. Call `createRenderers()` on the `CombinedChartRenderer`, or assign the data again.
