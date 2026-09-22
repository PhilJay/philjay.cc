# Setting data

How to build entries, data sets and a data object for every chart type, from a single line to a combined chart.

## The shape of the data

Three classes, always the same three, whichever chart you use.

An **entry** is one value. `Entry` for a line or scatter point, and a subclass wherever a value needs more than an x and a y: `BarEntry`, `PieEntry`, `CandleEntry`, `BubbleEntry`, `RadarEntry`.

A **data set** is one series: its entries plus the styling that applies to all of them. `LineDataSet`, `BarDataSet`, and so on. The label you pass is what the legend shows and what [`getDataSetByLabel`](/mpandroidchart/docs/chartdata/) looks up.

A **data object** holds every series of the chart. `LineData`, `BarData`, `PieData`. This is what you assign to the chart.

```figure
<svg viewBox="0 0 760 262" width="100%" role="img" aria-label="How a chart's data is put together" style="max-width:760px;height:auto;display:block;margin:0 auto 6px">
<title>How a chart's data is put together</title>
<rect x="148.0" y="44.0" width="566.0" height="182.0" rx="6" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<text x="164.0" y="70.0" fill="rgba(255,255,255,0.78)" font-size="13.5" text-anchor="start" font-weight="700">LineData</text>
<text x="240.0" y="70.0" fill="rgba(255,255,255,0.32)" font-size="11.5" text-anchor="start">holds every series</text>
<text x="24.0" y="70.0" fill="rgba(255,255,255,0.78)" font-size="13" text-anchor="start">chart.data =</text>
<line x1="126.0" y1="65.0" x2="142.0" y2="65.0" stroke="rgba(255,255,255,0.22)" stroke-width="1.5"/>
<rect x="164.0" y="90.0" width="534.0" height="72.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<rect x="164" y="90" width="3" height="72" rx="1.5" fill="#00a9ab"/>
<text x="180.0" y="112.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="start" font-weight="700">LineDataSet</text>
<text x="272.0" y="112.0" fill="rgba(255,255,255,0.32)" font-size="11.5" text-anchor="start">"Revenue"   one series, plus how it is drawn</text>
<rect x="180.0" y="124.0" width="102.0" height="26.0" rx="5" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="231.0" y="141.0" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">Entry(0, 12)</text>
<rect x="292.0" y="124.0" width="102.0" height="26.0" rx="5" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="343.0" y="141.0" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">Entry(1, 18)</text>
<rect x="404.0" y="124.0" width="102.0" height="26.0" rx="5" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="455.0" y="141.0" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">Entry(2, 15)</text>
<rect x="516.0" y="124.0" width="102.0" height="26.0" rx="5" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="567.0" y="141.0" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">Entry(3, 24)</text>
<text x="636.0" y="141.0" fill="rgba(255,255,255,0.32)" font-size="12" text-anchor="start">...</text>
<rect x="164.0" y="174.0" width="534.0" height="34.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<rect x="164" y="174" width="3" height="34" rx="1.5" fill="#8b7cf6"/>
<text x="180.0" y="196.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="start" font-weight="700">LineDataSet</text>
<text x="272.0" y="196.0" fill="rgba(255,255,255,0.32)" font-size="11.5" text-anchor="start">"Costs"   a second series, drawn its own way</text>
<text x="164.0" y="248.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">An entry is one value, a data set is one series, a data object is the lot</text>
</svg>
```

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

```figure
<svg viewBox="0 0 700 212" width="100%" role="img" aria-label="A line chart of the sample values" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>A line chart of the sample values</title>
<line x1="44.0" y1="83.5" x2="682.0" y2="83.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="115.0" x2="682.0" y2="115.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="146.5" x2="682.0" y2="146.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M44.0 157.8 C67.2 157.8 78.8 147.8 102.0 147.8 C125.2 147.8 136.8 152.8 160.0 152.8 C183.2 152.8 194.8 127.6 218.0 127.6 C241.2 127.6 252.8 131.0 276.0 131.0 C299.2 131.0 310.8 107.4 334.0 107.4 C357.2 107.4 368.8 110.8 392.0 110.8 C415.2 110.8 426.8 87.3 450.0 87.3 C473.2 87.3 484.8 95.7 508.0 95.7 C531.2 95.7 542.8 73.8 566.0 73.8 C589.2 73.8 600.8 80.6 624.0 80.6 C647.2 80.6 658.8 65.4 682.0 65.4" fill="none" stroke="#00a9ab" stroke-width="2.5" stroke-linecap="round"/>
<circle cx="44.0" cy="157.8" r="4" fill="#00a9ab"/>
<circle cx="102.0" cy="147.8" r="4" fill="#00a9ab"/>
<circle cx="160.0" cy="152.8" r="4" fill="#00a9ab"/>
<circle cx="218.0" cy="127.6" r="4" fill="#00a9ab"/>
<circle cx="276.0" cy="131.0" r="4" fill="#00a9ab"/>
<circle cx="334.0" cy="107.4" r="4" fill="#00a9ab"/>
<circle cx="392.0" cy="110.8" r="4" fill="#00a9ab"/>
<circle cx="450.0" cy="87.3" r="4" fill="#00a9ab"/>
<circle cx="508.0" cy="95.7" r="4" fill="#00a9ab"/>
<circle cx="566.0" cy="73.8" r="4" fill="#00a9ab"/>
<circle cx="624.0" cy="80.6" r="4" fill="#00a9ab"/>
<circle cx="682.0" cy="65.4" r="4" fill="#00a9ab"/>
<text x="44.0" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Jan</text>
<text x="160.0" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Mar</text>
<text x="276.0" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">May</text>
<text x="392.0" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Jul</text>
<text x="508.0" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Sep</text>
<text x="624.0" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Nov</text>
<text x="34.0" y="165.2" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">40</text>
<text x="34.0" y="114.8" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">70</text>
<text x="34.0" y="64.4" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">100</text>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">"Revenue"</text>
</svg>
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

```figure
<svg viewBox="0 0 700 212" width="100%" role="img" aria-label="A bar chart of the sample values" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>A bar chart of the sample values</title>
<line x1="44.0" y1="83.5" x2="682.0" y2="83.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="115.0" x2="682.0" y2="115.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="146.5" x2="682.0" y2="146.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M61.9 178.0 V133.6 A6 6 0 0 1 67.9 127.6 H99.8 A6 6 0 0 1 105.8 133.6 V178.0 Z" fill="#00a9ab"/>
<text x="83.9" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q1</text>
<path d="M141.7 178.0 V115.0 A6 6 0 0 1 147.7 109.0 H179.6 A6 6 0 0 1 185.6 115.0 V178.0 Z" fill="#00a9ab"/>
<text x="163.6" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q2</text>
<path d="M221.4 178.0 V123.0 A6 6 0 0 1 227.4 117.0 H259.3 A6 6 0 0 1 265.3 123.0 V178.0 Z" fill="#00a9ab"/>
<text x="243.4" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q3</text>
<path d="M301.2 178.0 V91.2 A6 6 0 0 1 307.2 85.2 H339.1 A6 6 0 0 1 345.1 91.2 V178.0 Z" fill="#00a9ab"/>
<text x="323.1" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q4</text>
<path d="M380.9 178.0 V99.1 A6 6 0 0 1 386.9 93.1 H418.8 A6 6 0 0 1 424.8 99.1 V178.0 Z" fill="#00a9ab"/>
<text x="402.9" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q5</text>
<path d="M460.7 178.0 V75.2 A6 6 0 0 1 466.7 69.2 H498.6 A6 6 0 0 1 504.6 75.2 V178.0 Z" fill="#00a9ab"/>
<text x="482.6" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q6</text>
<path d="M540.4 178.0 V107.1 A6 6 0 0 1 546.4 101.1 H578.3 A6 6 0 0 1 584.3 107.1 V178.0 Z" fill="#00a9ab"/>
<text x="562.4" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q7</text>
<path d="M620.2 178.0 V85.9 A6 6 0 0 1 626.2 79.9 H658.1 A6 6 0 0 1 664.1 85.9 V178.0 Z" fill="#00a9ab"/>
<text x="642.1" y="198.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">Q8</text>
<line x1="44.0" y1="178.0" x2="682.0" y2="178.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<text x="34.0" y="128.9" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">40</text>
<text x="34.0" y="75.9" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">80</text>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">"Orders"</text>
<text x="682.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">barWidth 0.55 leaves the gap</text>
</svg>
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

```figure
<svg viewBox="0 0 700 250" width="100%" role="img" aria-label="Four bar sets drawn side by side" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>Four bar sets drawn side by side</title>
<line x1="44.0" y1="89.0" x2="682.0" y2="89.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="122.0" x2="682.0" y2="122.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="155.0" x2="682.0" y2="155.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M52.5 188.0 V92.9 A3 3 0 0 1 55.5 89.9 H92.0 A3 3 0 0 1 95.0 92.9 V188.0 Z" fill="#3987e5"/>
<path d="M101.4 188.0 V108.0 A3 3 0 0 1 104.4 105.0 H141.0 A3 3 0 0 1 144.0 108.0 V188.0 Z" fill="#d95926"/>
<path d="M150.3 188.0 V119.3 A3 3 0 0 1 153.3 116.3 H189.9 A3 3 0 0 1 192.9 119.3 V188.0 Z" fill="#199e70"/>
<path d="M199.2 188.0 V134.4 A3 3 0 0 1 202.2 131.4 H238.8 A3 3 0 0 1 241.8 134.4 V188.0 Z" fill="#c98500"/>
<text x="147.1" y="208.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">1980</text>
<path d="M265.2 188.0 V76.0 A3 3 0 0 1 268.2 73.0 H304.7 A3 3 0 0 1 307.7 76.0 V188.0 Z" fill="#3987e5"/>
<path d="M314.1 188.0 V100.5 A3 3 0 0 1 317.1 97.5 H353.6 A3 3 0 0 1 356.6 100.5 V188.0 Z" fill="#d95926"/>
<path d="M363.0 188.0 V111.8 A3 3 0 0 1 366.0 108.8 H402.5 A3 3 0 0 1 405.5 111.8 V188.0 Z" fill="#199e70"/>
<path d="M411.9 188.0 V125.0 A3 3 0 0 1 414.9 122.0 H451.4 A3 3 0 0 1 454.4 125.0 V188.0 Z" fill="#c98500"/>
<text x="359.8" y="208.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">1981</text>
<path d="M477.8 188.0 V81.6 A3 3 0 0 1 480.8 78.6 H517.4 A3 3 0 0 1 520.4 81.6 V188.0 Z" fill="#3987e5"/>
<path d="M526.8 188.0 V87.3 A3 3 0 0 1 529.8 84.3 H566.3 A3 3 0 0 1 569.3 87.3 V188.0 Z" fill="#d95926"/>
<path d="M575.7 188.0 V115.6 A3 3 0 0 1 578.7 112.6 H615.2 A3 3 0 0 1 618.2 115.6 V188.0 Z" fill="#199e70"/>
<path d="M624.6 188.0 V128.8 A3 3 0 0 1 627.6 125.8 H664.1 A3 3 0 0 1 667.1 128.8 V188.0 Z" fill="#c98500"/>
<text x="572.5" y="208.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">1982</text>
<line x1="44.0" y1="188.0" x2="682.0" y2="188.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#3987e5"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">A</text>
<rect x="85.6" y="23.0" width="9" height="9" rx="2" fill="#d95926"/>
<text x="100.6" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">B</text>
<rect x="127.2" y="23.0" width="9" height="9" rx="2" fill="#199e70"/>
<text x="142.2" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">C</text>
<rect x="168.8" y="23.0" width="9" height="9" rx="2" fill="#c98500"/>
<text x="183.8" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">D</text>
<line x1="52.5" y1="224.0" x2="95.0" y2="224.0" stroke="#00a9ab" stroke-width="1.2"/>
<text x="73.8" y="240.0" fill="#00a9ab" font-size="10.5" text-anchor="middle">barWidth</text>
<line x1="95.0" y1="224.0" x2="101.4" y2="224.0" stroke="#8b7cf6" stroke-width="1.2"/>
<text x="143.4" y="240.0" fill="#8b7cf6" font-size="10.5" text-anchor="middle">barSpace</text>
<line x1="248.2" y1="224.0" x2="265.2" y2="224.0" stroke="#c98500" stroke-width="1.2"/>
<text x="256.7" y="240.0" fill="#c98500" font-size="10.5" text-anchor="middle">groupSpace</text>
<text x="682.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">four sets, one group per x</text>
</svg>
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

```figure
<svg viewBox="0 0 700 236" width="100%" role="img" aria-label="A stacked bar chart of the sample values" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>A stacked bar chart of the sample values</title>
<line x1="44.0" y1="92.5" x2="682.0" y2="92.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="129.0" x2="682.0" y2="129.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="165.5" x2="682.0" y2="165.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<rect x="91.8" y="147.2" width="117.0" height="54.8" fill="#00a9ab"/>
<rect x="91.8" y="108.8" width="117.0" height="36.5" fill="#8b7cf6"/>
<path d="M91.8 106.8 V90.8 A6 6 0 0 1 97.8 84.8 H202.8 A6 6 0 0 1 208.8 90.8 V106.8 Z" fill="#c98500"/>
<text x="150.3" y="222.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">2024</text>
<rect x="304.5" y="125.3" width="117.0" height="76.7" fill="#00a9ab"/>
<rect x="304.5" y="90.5" width="117.0" height="32.9" fill="#8b7cf6"/>
<path d="M304.5 88.5 V65.3 A6 6 0 0 1 310.5 59.3 H415.5 A6 6 0 0 1 421.5 65.3 V88.5 Z" fill="#c98500"/>
<text x="363.0" y="222.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">2025</text>
<rect x="517.2" y="136.3" width="117.0" height="65.7" fill="#00a9ab"/>
<rect x="517.2" y="86.9" width="117.0" height="47.5" fill="#8b7cf6"/>
<path d="M517.2 84.9 V72.6 A6 6 0 0 1 523.2 66.6 H628.1 A6 6 0 0 1 634.1 72.6 V84.9 Z" fill="#c98500"/>
<text x="575.7" y="222.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="middle">2026</text>
<line x1="44.0" y1="202.0" x2="682.0" y2="202.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Births</text>
<rect x="118.6" y="23.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<text x="133.6" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Divorces</text>
<rect x="206.4" y="23.0" width="9" height="9" rx="2" fill="#c98500"/>
<text x="221.4" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Marriages</text>
<text x="682.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">one entry, three values</text>
</svg>
```

The values are drawn bottom to top in list order, and the set needs one color per stack value. `stackLabels` names the legend entries, one per stack value, and the set label follows them as an entry without a form.

`barCornerRadius` rounds the bar as a whole, which for a stack means only the end farthest from zero. `isStackSectionsRounded = true` rounds every section of the stack instead.

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

```figure
<svg viewBox="0 0 640 216" width="100%" role="img" aria-label="A horizontal bar chart of the sample values" style="max-width:640px;height:auto;display:block;margin:0 auto 6px">
<title>A horizontal bar chart of the sample values</title>
<path d="M68.0 58.6 H555.4 A5 5 0 0 1 560.4 63.6 V70.9 A5 5 0 0 1 555.4 75.9 H68.0 Z" fill="#00a9ab"/>
<text x="58.0" y="71.2" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="end">Rent</text>
<text x="568.4" y="71.2" fill="rgba(255,255,255,0.78)" font-size="11" text-anchor="start">64</text>
<path d="M68.0 93.1 H432.3 A5 5 0 0 1 437.3 98.1 V105.4 A5 5 0 0 1 432.3 110.4 H68.0 Z" fill="#00a9ab"/>
<text x="58.0" y="105.8" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="end">Food</text>
<text x="445.3" y="105.8" fill="rgba(255,255,255,0.78)" font-size="11" text-anchor="start">48</text>
<path d="M68.0 127.6 H340.0 A5 5 0 0 1 345.0 132.6 V139.9 A5 5 0 0 1 340.0 144.9 H68.0 Z" fill="#00a9ab"/>
<text x="58.0" y="140.2" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="end">Travel</text>
<text x="353.0" y="140.2" fill="rgba(255,255,255,0.78)" font-size="11" text-anchor="start">36</text>
<path d="M68.0 162.1 H278.4 A5 5 0 0 1 283.4 167.1 V174.4 A5 5 0 0 1 278.4 179.4 H68.0 Z" fill="#00a9ab"/>
<text x="58.0" y="174.8" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="end">Fun</text>
<text x="291.4" y="174.8" fill="rgba(255,255,255,0.78)" font-size="11" text-anchor="start">28</text>
<line x1="68.0" y1="50.0" x2="68.0" y2="188.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<rect x="68.0" y="23.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="83.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">"Budget"</text>
<text x="622.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">entry 0 sits at the bottom, so the list is reversed</text>
</svg>
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

```figure
<svg viewBox="0 0 640 286" width="100%" role="img" aria-label="A pie chart of the sample values" style="max-width:640px;height:auto;display:block;margin:0 auto 6px">
<title>A pie chart of the sample values</title>
<text x="40.0" y="30.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Sessions</text>
<path d="M210 152 L212.5 64.0 A88 88 0 0 1 244.7 232.9 Z" fill="#3987e5"/>
<text x="318.1" y="135.4" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="start">Mobile 44%</text>
<path d="M210 152 L240.1 234.7 A88 88 0 0 1 124.1 170.9 Z" fill="#d95926"/>
<text x="157.0" y="252.4" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="end">Web 28%</text>
<path d="M210 152 L123.1 166.1 A88 88 0 0 1 156.3 82.3 Z" fill="#199e70"/>
<text x="107.7" y="115.5" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="end">Desktop 18%</text>
<path d="M210 152 L160.3 79.4 A88 88 0 0 1 207.5 64.0 Z" fill="#c98500"/>
<text x="176.0" y="51.4" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="end">Other 10%</text>
<rect x="400.0" y="113.0" width="9" height="9" rx="2" fill="#3987e5"/>
<text x="415.0" y="122.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Mobile</text>
<rect x="474.6" y="113.0" width="9" height="9" rx="2" fill="#d95926"/>
<text x="489.6" y="122.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Web</text>
<rect x="400.0" y="137.0" width="9" height="9" rx="2" fill="#199e70"/>
<text x="415.0" y="146.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Desktop</text>
<rect x="481.2" y="137.0" width="9" height="9" rx="2" fill="#c98500"/>
<text x="496.2" y="146.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Other</text>
<text x="400.0" y="88.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="start">one set only, and a slice per entry</text>
</svg>
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

```figure
<svg viewBox="0 0 700 226" width="100%" role="img" aria-label="A scatter chart with a shape per set" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>A scatter chart with a shape per set</title>
<line x1="44.0" y1="88.0" x2="682.0" y2="88.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="124.0" x2="682.0" y2="124.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="160.0" x2="682.0" y2="160.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<rect x="255.6" y="93.4" width="8" height="8" fill="#00a9ab"/>
<rect x="380.1" y="78.8" width="8" height="8" fill="#00a9ab"/>
<rect x="99.6" y="104.0" width="8" height="8" fill="#00a9ab"/>
<rect x="106.5" y="109.0" width="8" height="8" fill="#00a9ab"/>
<rect x="314.7" y="100.5" width="8" height="8" fill="#00a9ab"/>
<rect x="433.8" y="92.6" width="8" height="8" fill="#00a9ab"/>
<rect x="404.3" y="150.8" width="8" height="8" fill="#00a9ab"/>
<rect x="569.4" y="72.1" width="8" height="8" fill="#00a9ab"/>
<rect x="150.2" y="76.0" width="8" height="8" fill="#00a9ab"/>
<rect x="171.6" y="83.8" width="8" height="8" fill="#00a9ab"/>
<rect x="440.5" y="126.0" width="8" height="8" fill="#00a9ab"/>
<rect x="100.5" y="88.5" width="8" height="8" fill="#00a9ab"/>
<rect x="464.9" y="109.1" width="8" height="8" fill="#00a9ab"/>
<rect x="331.5" y="95.6" width="8" height="8" fill="#00a9ab"/>
<circle cx="535.8" cy="132.0" r="4.5" fill="#8b7cf6"/>
<circle cx="377.8" cy="132.2" r="4.5" fill="#8b7cf6"/>
<circle cx="497.7" cy="153.1" r="4.5" fill="#8b7cf6"/>
<circle cx="314.9" cy="71.4" r="4.5" fill="#8b7cf6"/>
<circle cx="158.7" cy="130.2" r="4.5" fill="#8b7cf6"/>
<circle cx="518.3" cy="127.3" r="4.5" fill="#8b7cf6"/>
<circle cx="583.4" cy="138.3" r="4.5" fill="#8b7cf6"/>
<circle cx="409.9" cy="104.4" r="4.5" fill="#8b7cf6"/>
<circle cx="562.5" cy="105.1" r="4.5" fill="#8b7cf6"/>
<circle cx="105.1" cy="131.2" r="4.5" fill="#8b7cf6"/>
<circle cx="449.4" cy="101.2" r="4.5" fill="#8b7cf6"/>
<circle cx="296.0" cy="126.4" r="4.5" fill="#8b7cf6"/>
<circle cx="82.8" cy="151.8" r="4.5" fill="#8b7cf6"/>
<circle cx="104.1" cy="119.3" r="4.5" fill="#8b7cf6"/>
<path d="M145.4 139.7 L150.0 148.2 L140.8 148.2 Z" fill="#c98500"/>
<path d="M116.8 133.5 L121.4 142.0 L112.2 142.0 Z" fill="#c98500"/>
<path d="M392.0 114.5 L396.6 123.0 L387.4 123.0 Z" fill="#c98500"/>
<path d="M232.9 176.3 L237.5 184.8 L228.3 184.8 Z" fill="#c98500"/>
<path d="M280.1 125.6 L284.7 134.1 L275.5 134.1 Z" fill="#c98500"/>
<path d="M173.0 182.4 L177.6 190.9 L168.4 190.9 Z" fill="#c98500"/>
<path d="M206.5 182.4 L211.1 190.9 L201.9 190.9 Z" fill="#c98500"/>
<path d="M71.9 150.7 L76.5 159.2 L67.3 159.2 Z" fill="#c98500"/>
<path d="M286.3 182.4 L290.9 190.9 L281.7 190.9 Z" fill="#c98500"/>
<path d="M372.1 166.0 L376.7 174.5 L367.5 174.5 Z" fill="#c98500"/>
<path d="M466.4 104.8 L471.0 113.3 L461.8 113.3 Z" fill="#c98500"/>
<path d="M582.8 128.7 L587.4 137.2 L578.2 137.2 Z" fill="#c98500"/>
<path d="M299.8 153.9 L304.4 162.4 L295.2 162.4 Z" fill="#c98500"/>
<path d="M106.1 158.0 L110.7 166.5 L101.5 166.5 Z" fill="#c98500"/>
<line x1="44.0" y1="196.0" x2="682.0" y2="196.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">SQUARE</text>
<rect x="118.6" y="23.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<text x="133.6" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">CIRCLE</text>
<rect x="193.2" y="23.0" width="9" height="9" rx="2" fill="#c98500"/>
<text x="208.2" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">TRIANGLE</text>
<text x="682.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">the shape is what tells the sets apart</text>
</svg>
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

```figure
<svg viewBox="0 0 700 226" width="100%" role="img" aria-label="A candlestick chart" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>A candlestick chart</title>
<line x1="44.0" y1="88.0" x2="682.0" y2="88.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="124.0" x2="682.0" y2="124.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="160.0" x2="682.0" y2="160.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="75.9" y1="113.7" x2="75.9" y2="161.7" stroke="#3cdc4e" stroke-width="1.5"/>
<rect x="60.0" y="124.0" width="31.9" height="24.0" rx="1.5" fill="#3cdc4e"/>
<line x1="139.7" y1="100.0" x2="139.7" y2="137.7" stroke="#f05050" stroke-width="1.5"/>
<rect x="123.7" y="124.0" width="31.9" height="6.9" rx="1.5" fill="#f05050"/>
<line x1="203.5" y1="106.9" x2="203.5" y2="154.9" stroke="#f05050" stroke-width="1.5"/>
<rect x="187.6" y="130.9" width="31.9" height="17.1" rx="1.5" fill="#f05050"/>
<line x1="267.3" y1="127.4" x2="267.3" y2="175.4" stroke="#f05050" stroke-width="1.5"/>
<rect x="251.3" y="148.0" width="31.9" height="20.6" rx="1.5" fill="#f05050"/>
<line x1="331.1" y1="137.7" x2="331.1" y2="185.7" stroke="#3cdc4e" stroke-width="1.5"/>
<rect x="315.1" y="144.6" width="31.9" height="24.0" rx="1.5" fill="#3cdc4e"/>
<line x1="394.9" y1="117.1" x2="394.9" y2="154.9" stroke="#3cdc4e" stroke-width="1.5"/>
<rect x="378.9" y="120.6" width="31.9" height="24.0" rx="1.5" fill="#3cdc4e"/>
<line x1="458.7" y1="89.7" x2="458.7" y2="130.9" stroke="#3cdc4e" stroke-width="1.5"/>
<rect x="442.7" y="100.0" width="31.9" height="20.6" rx="1.5" fill="#3cdc4e"/>
<line x1="522.5" y1="79.4" x2="522.5" y2="120.6" stroke="#f05050" stroke-width="1.5"/>
<rect x="506.6" y="100.0" width="31.9" height="10.3" rx="1.5" fill="#f05050"/>
<line x1="586.3" y1="86.3" x2="586.3" y2="134.3" stroke="#3cdc4e" stroke-width="1.5"/>
<rect x="570.3" y="93.1" width="31.9" height="17.1" rx="1.5" fill="#3cdc4e"/>
<line x1="650.1" y1="69.1" x2="650.1" y2="106.9" stroke="#3cdc4e" stroke-width="1.5"/>
<rect x="634.1" y="76.0" width="31.9" height="17.1" rx="1.5" fill="#3cdc4e"/>
<line x1="44.0" y1="196.0" x2="682.0" y2="196.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#3cdc4e"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">increasing</text>
<rect x="145.0" y="23.0" width="9" height="9" rx="2" fill="#f05050"/>
<text x="160.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">decreasing</text>
<text x="682.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">high, low, open, close</text>
</svg>
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

```figure
<svg viewBox="0 0 700 226" width="100%" role="img" aria-label="A bubble chart" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>A bubble chart</title>
<line x1="44.0" y1="88.0" x2="682.0" y2="88.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="124.0" x2="682.0" y2="124.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="160.0" x2="682.0" y2="160.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<circle cx="95.0" cy="147.0" r="8.0" fill="#00a9ab" fill-opacity="0.5" stroke="#00a9ab" stroke-width="1.5"/>
<circle cx="171.6" cy="106.7" r="13.0" fill="#8b7cf6" fill-opacity="0.5" stroke="#8b7cf6" stroke-width="1.5"/>
<circle cx="241.8" cy="132.6" r="6.0" fill="#c98500" fill-opacity="0.5" stroke="#c98500" stroke-width="1.5"/>
<circle cx="312.0" cy="89.4" r="16.0" fill="#00a9ab" fill-opacity="0.5" stroke="#00a9ab" stroke-width="1.5"/>
<circle cx="382.1" cy="121.1" r="10.0" fill="#8b7cf6" fill-opacity="0.5" stroke="#8b7cf6" stroke-width="1.5"/>
<circle cx="445.9" cy="152.8" r="7.0" fill="#c98500" fill-opacity="0.5" stroke="#c98500" stroke-width="1.5"/>
<circle cx="503.4" cy="101.0" r="12.0" fill="#00a9ab" fill-opacity="0.5" stroke="#00a9ab" stroke-width="1.5"/>
<circle cx="579.9" cy="126.9" r="17.0" fill="#8b7cf6" fill-opacity="0.5" stroke="#8b7cf6" stroke-width="1.5"/>
<circle cx="637.3" cy="95.2" r="9.0" fill="#c98500" fill-opacity="0.5" stroke="#c98500" stroke-width="1.5"/>
<line x1="44.0" y1="196.0" x2="682.0" y2="196.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">"Deals"</text>
<text x="682.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">a point plus a size, scaled to the biggest</text>
</svg>
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

```figure
<svg viewBox="0 0 640 300" width="100%" role="img" aria-label="A radar chart of the sample values" style="max-width:640px;height:auto;display:block;margin:0 auto 6px">
<title>A radar chart of the sample values</title>
<text x="40.0" y="30.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Entry i of every set sits on axis i</text>
<path d="M300.0 132.0 L322.5 145.0 L322.5 171.0 L300.0 184.0 L277.5 171.0 L277.5 145.0 Z" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M300.0 106.0 L345.0 132.0 L345.0 184.0 L300.0 210.0 L255.0 184.0 L255.0 132.0 Z" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M300.0 80.0 L367.5 119.0 L367.5 197.0 L300.0 236.0 L232.5 197.0 L232.5 119.0 Z" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M300.0 54.0 L390.1 106.0 L390.1 210.0 L300.0 262.0 L209.9 210.0 L209.9 106.0 Z" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="300.0" y1="158.0" x2="300.0" y2="54.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="300.0" y="33.0" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">Speed</text>
<line x1="300.0" y1="158.0" x2="390.1" y2="106.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="411.7" y="97.5" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="start">Power</text>
<line x1="300.0" y1="158.0" x2="390.1" y2="210.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="411.7" y="226.5" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="start">Range</text>
<line x1="300.0" y1="158.0" x2="300.0" y2="262.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="300.0" y="291.0" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">Agility</text>
<line x1="300.0" y1="158.0" x2="209.9" y2="210.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="188.3" y="226.5" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="end">Stealth</text>
<line x1="300.0" y1="158.0" x2="209.9" y2="106.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<text x="188.3" y="97.5" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="end">Armor</text>
<path d="M300.0 106.0 L376.6 113.8 L336.0 178.8 L300.0 251.6 L227.9 199.6 L259.5 134.6 Z" fill="#8b7cf6" fill-opacity="0.15" stroke="#8b7cf6" stroke-width="2.8"/>
<path d="M300.0 64.4 L354.0 126.8 L372.1 199.6 L300.0 230.8 L255.0 184.0 L223.4 113.8 Z" fill="#00a9ab" fill-opacity="0.15" stroke="#00a9ab" stroke-width="2.8"/>
<rect x="40.0" y="267.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<text x="55.0" y="276.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">Last week</text>
<rect x="134.4" y="267.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="149.4" y="276.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">This week</text>
</svg>
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

```figure
<svg viewBox="0 0 700 226" width="100%" role="img" aria-label="A combined chart of bars and a line" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>A combined chart of bars and a line</title>
<line x1="44.0" y1="88.0" x2="682.0" y2="88.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="124.0" x2="682.0" y2="124.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="44.0" y1="160.0" x2="682.0" y2="160.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M63.9 196.0 V149.2 A4 4 0 0 1 67.9 145.2 H99.8 A4 4 0 0 1 103.8 149.2 V196.0 Z" fill="#8b7cf6"/>
<path d="M143.7 196.0 V128.8 A4 4 0 0 1 147.7 124.8 H179.6 A4 4 0 0 1 183.6 128.8 V196.0 Z" fill="#8b7cf6"/>
<path d="M223.4 196.0 V139.0 A4 4 0 0 1 227.4 135.0 H259.3 A4 4 0 0 1 263.3 139.0 V196.0 Z" fill="#8b7cf6"/>
<path d="M303.2 196.0 V111.9 A4 4 0 0 1 307.2 107.9 H339.1 A4 4 0 0 1 343.1 111.9 V196.0 Z" fill="#8b7cf6"/>
<path d="M382.9 196.0 V122.1 A4 4 0 0 1 386.9 118.1 H418.8 A4 4 0 0 1 422.8 122.1 V196.0 Z" fill="#8b7cf6"/>
<path d="M462.7 196.0 V98.4 A4 4 0 0 1 466.7 94.4 H498.6 A4 4 0 0 1 502.6 98.4 V196.0 Z" fill="#8b7cf6"/>
<path d="M542.4 196.0 V108.5 A4 4 0 0 1 546.4 104.5 H578.3 A4 4 0 0 1 582.3 108.5 V196.0 Z" fill="#8b7cf6"/>
<path d="M622.2 196.0 V88.2 A4 4 0 0 1 626.2 84.2 H658.1 A4 4 0 0 1 662.1 88.2 V196.0 Z" fill="#8b7cf6"/>
<path d="M83.9 118.1 C115.8 118.1 131.7 107.9 163.6 107.9 C195.5 107.9 211.5 114.7 243.4 114.7 C275.3 114.7 291.2 87.6 323.1 87.6 C355.0 87.6 371.0 97.7 402.9 97.7 C434.8 97.7 450.7 74.0 482.6 74.0 C514.5 74.0 530.5 84.2 562.4 84.2 C594.3 84.2 610.2 63.9 642.1 63.9" fill="none" stroke="#00a9ab" stroke-width="2.5"/>
<circle cx="83.9" cy="118.1" r="3.5" fill="#00a9ab"/>
<circle cx="163.6" cy="107.9" r="3.5" fill="#00a9ab"/>
<circle cx="243.4" cy="114.7" r="3.5" fill="#00a9ab"/>
<circle cx="323.1" cy="87.6" r="3.5" fill="#00a9ab"/>
<circle cx="402.9" cy="97.7" r="3.5" fill="#00a9ab"/>
<circle cx="482.6" cy="74.0" r="3.5" fill="#00a9ab"/>
<circle cx="562.4" cy="84.2" r="3.5" fill="#00a9ab"/>
<circle cx="642.1" cy="63.9" r="3.5" fill="#00a9ab"/>
<line x1="44.0" y1="196.0" x2="682.0" y2="196.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<rect x="44.0" y="23.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<text x="59.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">barData</text>
<rect x="125.2" y="23.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<text x="140.2" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">lineData</text>
<text x="682.0" y="32.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="end">drawOrder puts the line on top</text>
</svg>
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
