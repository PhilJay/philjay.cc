# Setting data

How to build entries, data sets and a data object for every chart type, from a single line to a combined chart.

## The shape of the data

Three classes, always the same three, whichever chart you use.

An **entry** is one value. `Entry` for a line or scatter point, and a subclass wherever a value needs more than an x and a y: `BarEntry`, `PieEntry`, `CandleEntry`, `BubbleEntry`, `RadarEntry`.

A **data set** is one series: its entries plus the styling that applies to all of them. `LineDataSet`, `BarDataSet`, and so on. The label you pass is what the legend shows and what [`getDataSetByLabel`](/mpandroidchart/docs/chartdata/) looks up.

A **data object** holds every series of the chart. `LineData`, `BarData`, `PieData`. This is what you assign to the chart.

```kotlin
val set = LineDataSet(entries, "Revenue")
chart.data = LineData(set)
```

Assigning `chart.data` recalculates the ranges, the axes, the legend and the offsets, then redraws. There is no second call to make.

Data objects take sets in three ways: `LineData()` for an empty one, `LineData(set1, set2)` for a few, and `LineData(listOf(set1, set2))` for a list. An `ArrayList` you hand over is kept by reference, any other list is copied. `PieData` is the exception, because it holds a single set: it takes `PieData()` or `PieData(set)`.

## Entries must be sorted by x

The library finds entries by binary search, so a data set expects its entries in ascending x order. Unsorted entries may still draw correctly, but lookups, highlighting and the x range are then unreliable.

Sort before you build the set:

```kotlin
val entries = points.map { Entry(it.time, it.value) }.sortedBy { it.x }
```

`EntryXComparator` does the same for a mutable list, which is handy from Java:

```kotlin
entries.sortWith(EntryXComparator())
```

When you add to an existing set, `addEntryOrdered` inserts at the right place instead of appending:

```kotlin
set.addEntryOrdered(Entry(12f, 88f))
```

Pie and radar entries are the exception. They have no x at all, and their position is their index in the set.

## The typed payload

An entry can carry the object it was made from. `Entry` is generic in that payload, and the data set follows along.

Without a payload, use the factory function, which gives you an `Entry<Nothing>`:

```kotlin
val set = LineDataSet(values.mapIndexed { i, v -> Entry(i.toFloat(), v) }, "Revenue")
```

With a payload, pass `data` and the type is inferred:

```kotlin
val set: LineDataSet<Order> = LineDataSet(
    orders.map { Entry(it.day, it.total, data = it) },
    "Orders",
)
```

The payload is read only, it is shared and not copied by `copy()`, and it is ignored by drawing. It is there so you can get your own object back when the user picks a value:

```kotlin
chart.onValueSelected { e, _ ->
    val order = e.data as? Order ?: return@onValueSelected
    showDetails(order)
}
```

The cast is needed because the selection listener hands you an `Entry<*>`. If you want the type without a cast, keep a reference to your typed set and read its entries:

```kotlin
val order = set.getEntryForIndex(index).data
```

> Payloads survive parcelling only if they implement `Parcelable`. Writing an entry whose payload does not throws a `ParcelFormatException`.

## Icons on entries

Every entry takes a `Drawable` that is drawn at its position:

```kotlin
val star = ContextCompat.getDrawable(context, R.drawable.star)
val entries = values.mapIndexed { i, v -> BarEntry(i.toFloat(), v, star) }
```

Drawing them is on by default per set, so you switch icons off through `isDrawIconsEnabled`, and you move them with `iconsOffset`:

```kotlin
set.isDrawIconsEnabled = true
set.iconsOffset = MPPointF(0f, 40f)
```

## Line chart

`LineChart` takes `Entry` objects in a `LineDataSet`. The x value is a position on the axis, not an index, so you are free to leave gaps.

```kotlin
val values = listOf(42f, 48f, 45f, 60f, 58f, 72f, 70f, 84f, 79f, 92f, 88f, 97f)

val entries = values.mapIndexed { i, v -> Entry(i.toFloat(), v) }

val set = LineDataSet(entries, "Revenue").apply {
    color = Color.rgb(90, 140, 255)
    lineWidth = 2.5f
    circleRadius = 4f
    isDrawValuesEnabled = false
    mode = LineDataSet.Mode.CUBIC_BEZIER
}

chart.data = LineData(set)
chart.xAxis.valueFormatter = IndexAxisValueFormatter(months)
```

Several series are several sets. Use `axisDependency` to plot one of them against the right y axis:

```kotlin
val costs = LineDataSet(costEntries, "Costs").apply {
    axisDependency = YAxis.AxisDependency.RIGHT
}
chart.data = LineData(revenue, costs)
```

## Bar chart

`BarChart` takes `BarEntry` objects. The x value is the centre of the bar, and the width comes from the data object, not from the set, because all bars of a chart share it.

```kotlin
val values = listOf(38f, 52f, 46f, 70f, 64f, 82f, 58f, 74f)

val entries = values.mapIndexed { i, v -> BarEntry(i.toFloat(), v) }

val set = BarDataSet(entries, "Orders").apply {
    color = Color.rgb(90, 140, 255)
    barCornerRadius = 6f
}

chart.data = BarData(set).apply { barWidth = 0.55f }
```

`barWidth` is in x value units, not pixels, and defaults to `0.85`. With bars one x apart that leaves a gap of 0.15 between them.

A bar is drawn half a width to each side of its x, so with a wide bar the first and last one reach past the ends of the axis range and get clipped. This widens the range by half a bar width on each side so they fit:

```kotlin
chart.isFitBarsEnabled = true
```

It takes effect on the next `notifyDataSetChanged()`, which assigning data already does, so set it before you assign.

## Grouped bars

Several `BarDataSet` objects can be drawn side by side instead of on top of each other. `groupBars` does the positioning for you by rewriting the x of every entry.

```kotlin
val groupSpace = 0.08f
val barSpace = 0.03f
val barWidth = 0.2f
// (0.2 + 0.03) * 4 sets + 0.08 = 1.0 per group

val data = BarData(setA, setB, setC, setD).apply { this.barWidth = barWidth }
chart.data = data

chart.xAxis.axisMinimum = 1980f
chart.xAxis.axisMaximum = 1980f + data.getGroupWidth(groupSpace, barSpace) * groupCount
chart.xAxis.isCenterAxisLabelsEnabled = true
chart.xAxis.granularity = 1f

chart.groupBars(1980f, groupSpace, barSpace)
```

Four things have to hold for this to work.

- The data must already be on the chart. `chart.groupBars` throws `IllegalStateException` otherwise.
- The data must hold at least two sets. `BarData.groupBars` throws `IllegalStateException` otherwise.
- `barWidth` must be set first, because the group width is computed from it.
- The x values your entries carry are overwritten and lost. Group *i* is entry *i* of every set, taken by position in the list, so give each set its entries in the same order.

`getGroupWidth(groupSpace, barSpace)` returns what one group takes on the axis: `setCount * (barWidth + barSpace) + groupSpace`. Pick the three numbers so that it comes out at a round value like 1, then the axis labels line up with the groups.

`chart.groupBars` calls `notifyDataSetChanged()` for you. `BarData.groupBars`, which you would use inside a combined chart, does not.

## Stacked bars

A stacked bar is one `BarEntry` with a list of values instead of a single y:

```kotlin
val stacks = listOf(
    listOf(30f, 20f, 12f),
    listOf(42f, 18f, 16f),
    listOf(36f, 26f, 10f),
)

val entries = stacks.mapIndexed { i, s -> BarEntry(i.toFloat(), s) }

val set = BarDataSet(entries, "Spend").apply {
    colors = listOf(Color.BLUE, Color.RED, Color.YELLOW)
    stackLabels = listOf("Births", "Divorces", "Marriages")
}

chart.data = BarData(set).apply { barWidth = 0.55f }
```

The values are drawn bottom to top in list order, and the set needs one color per stack value. `stackLabels` names the legend entries, one per stack value, and the set label follows them as an entry without a form.

Setting the stack values computes a few things on the entry: `y` becomes their sum, `positiveSum` and `negativeSum` hold the two halves, and `ranges` holds the start and end on the y axis of each value. Negative values stack downwards from zero, positive values upwards, so a stack can cross the axis. `isStacked` tells you whether an entry has a stack at all, and `getSumBelow(index)` sums the stack values after that index, the ones stacked above it.

A tap selects one value of the stack and reports its position in `Highlight.stackIndex`. To select the whole bar instead:

```kotlin
chart.isHighlightFullBarEnabled = true
```

## Horizontal bar chart

`HorizontalBarChart` uses the same `BarEntry`, `BarDataSet` and `BarData` as the vertical one. Only the drawing is turned: the x axis runs up the left side and the values extend to the right.

That also turns the order around. Entry 0 sits at the bottom, so reverse your x values if you want the first item at the top:

```kotlin
val items = listOf("Rent" to 64f, "Food" to 48f, "Travel" to 36f, "Fun" to 28f)
val entries = items.asReversed().mapIndexed { i, (_, v) -> BarEntry(i.toFloat(), v) }

chart.data = BarData(BarDataSet(entries, "Budget")).apply { barWidth = 0.5f }
chart.xAxis.valueFormatter = IndexAxisValueFormatter(items.map { it.first }.reversed())
```

## Pie chart

`PieChart` takes `PieEntry` objects, which have a value and an optional label but no x. A slice's position is its index in the set, and the pie is always exactly one data set.

```kotlin
val items = listOf("Mobile" to 44f, "Web" to 28f, "Desktop" to 18f, "Other" to 10f)

val set = PieDataSet(items.map { (label, v) -> PieEntry(v, label) }, "Sessions").apply {
    colors = ColorTemplate.MATERIAL_COLORS
    sliceSpace = 3f
    selectionShift = 5f
}

chart.data = PieData(set)
```

The legend gets one entry per slice, taken from the entry labels, and the set label is appended after them as an entry without a form. Give the set a blank label to keep it out. `PieData.yValueSum` gives you the total of all slices, which is what a percent formatter divides by.

## Scatter chart

`ScatterChart` takes plain `Entry` objects in a `ScatterDataSet`. What makes a set distinct is its shape.

```kotlin
val set = ScatterDataSet(points.sortedBy { it.x }, "Samples").apply {
    setScatterShape(ScatterChart.ScatterShape.CIRCLE)
    scatterShapeSize = 18f
    color = Color.rgb(90, 140, 255)
}

chart.data = ScatterData(setA, setB, setC)
```

`setScatterShape` swaps in the built-in renderer for one of `SQUARE`, `CIRCLE`, `TRIANGLE`, `CROSS`, `X`, `CHEVRON_UP` and `CHEVRON_DOWN`. The default is `SQUARE`.

| Property | Meaning | Default |
| --- | --- | --- |
| `scatterShapeSize` | Size of the shape in dp | `15` |
| `scatterShapeHoleRadius` | Radius of the hole in the middle, in dp | `0` |
| `scatterShapeHoleColor` | Color of that hole; `ColorTemplate.COLOR_NONE` draws none | `COLOR_NONE` |
| `shapeRenderer` | The renderer itself, for a shape of your own | `SquareShapeRenderer` |

Assign `shapeRenderer` directly with your own `IShapeRenderer` when none of the seven fit.

## Candlestick chart

`CandleStickChart` takes `CandleEntry` objects with the four values of a period, in the order high, low, open, close.

```kotlin
val entries = bars.map { CandleEntry(it.index, it.high, it.low, it.open, it.close) }

val set = CandleDataSet(entries, "ACME").apply {
    shadowWidth = 1.5f
    shadowColorSameAsCandle = true
    increasingColor = Color.rgb(60, 220, 78)
    increasingPaintStyle = Paint.Style.FILL
    decreasingColor = Color.rgb(240, 80, 80)
    decreasingPaintStyle = Paint.Style.FILL
    barSpace = 0.25f
}

chart.data = CandleData(set)
```

The inherited `y` of a candle entry is set once at construction to the middle between high and low. Changing `high` or `low` later does not move it, so build a new entry instead of editing one.

`shadowRange` is the distance between high and low, `bodyRange` the distance between open and close.

## Bubble chart

`BubbleChart` takes `BubbleEntry` objects: a point plus a size.

```kotlin
val entries = deals
    .map { BubbleEntry(it.quarter, it.probability, it.amount) }
    .sortedBy { it.x }

val set = BubbleDataSet(entries, "Deals").apply {
    colors = ColorTemplate.VORDIPLOM_COLORS
    highlightCircleWidth = 1.5f
}

chart.data = BubbleData(set)
```

The size is in value space. By default `isNormalizeSizeEnabled` is on, which scales every bubble relative to the largest size in the set, so the biggest bubble always fills the same area whatever your numbers are. Switch it off to have the sizes taken literally.

## Radar chart

`RadarChart` takes `RadarEntry` objects, which hold only a value. Entry *i* of every set sits on axis *i* of the web, so all sets need the same number of entries.

```kotlin
val labels = listOf("Speed", "Power", "Range", "Agility", "Stealth", "Armor")

fun set(values: List<Float>, label: String, color: Int) =
    RadarDataSet(values.map { RadarEntry(it) }, label).apply {
        this.color = color
        fillColor = color
        fillAlpha = 56
        isDrawFilledEnabled = true
        lineWidth = 2.5f
    }

chart.data = RadarData(
    set(listOf(50f, 85f, 40f, 90f, 80f, 45f), "Last week", Color.MAGENTA),
    set(listOf(90f, 60f, 80f, 70f, 50f, 85f), "This week", Color.CYAN),
)
chart.xAxis.valueFormatter = IndexAxisValueFormatter(labels)
```

The text around the web comes from the chart's x axis, so an `IndexAxisValueFormatter` over your labels is the way to name the axes.

## Combined chart

`CombinedChart` draws up to five kinds at once. `CombinedData` has one slot per kind, and you fill the ones you need:

```kotlin
chart.data = CombinedData().apply {
    barData = BarData(barSet).apply { barWidth = 0.5f }
    lineData = LineData(lineSet)
}
```

The slots are `lineData`, `barData`, `scatterData`, `candleData` and `bubbleData`. Each one is a complete data object of its own, so everything above still applies, including `groupBars` on the bar part.

What is drawn last ends up on top. `drawOrder` controls that:

```kotlin
chart.drawOrder = listOf(CombinedChart.DrawOrder.BAR, CombinedChart.DrawOrder.LINE)
```

Assign it before `chart.data`, because the data setter is what builds the sub renderers from this list. The default order is bar, bubble, line, candle, scatter. A kind you leave out of the list is not drawn, so list every kind you have set.

> Add and remove sets through the child data objects, never on the combined object itself. `CombinedData` rebuilds its own set list from the children on every recalculation, so anything added directly is dropped.

## Changing data afterwards

Assigning a new data object does everything at once. If instead you change entries in place, tell the chart afterwards:

```kotlin
set.entries = newEntries
chart.notifyDataSetChanged()
```

That one call asks the data object to recompute its ranges, recalculates the axes, the legend and the offsets, and redraws. See [dynamic data](/mpandroidchart/docs/dynamic-data/) for adding and removing values while the chart is on screen, and [the ChartData class](/mpandroidchart/docs/chartdata/) for what the data object caches and when.

## Where to go next

- [ChartData subclasses](/mpandroidchart/docs/chartdata-subclasses/) for what each data class adds.
- [The DataSet class](/mpandroidchart/docs/dataset/) for the styling shared by every series.
- [Formatters](/mpandroidchart/docs/formatters/) for turning values into the text on the axes and above the entries.
- [Colors](/mpandroidchart/docs/colors/) for the color lists used above.
