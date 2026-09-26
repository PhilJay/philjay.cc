# ChartData subclasses

What each data class adds on top of ChartData, from the bar width to the five slots of a combined chart.

## What they have in common

Every chart type has its own data class. Most of them add nothing but the set type they accept, which is what makes the compiler stop you from putting a `LineDataSet` into a bar chart. Four of them add real behaviour, and two behave differently enough from the base class to be worth reading before you use them.

All of them except `PieData` take sets the same three ways: an empty constructor, a vararg of sets, and a list. An `ArrayList` you hand over is kept by reference, any other list is copied. `PieData` holds a single set, so it takes `PieData()` or `PieData(set)`.

`BarLineScatterCandleBubbleData` sits between `ChartData` and the data classes of the charts that have an x and a y axis. It adds nothing either; it exists so that a combined chart can treat them alike. `PieData` and `RadarData` extend `ChartData` directly.

## LineData

Holds one or more `ILineDataSet`, one per line. It adds nothing of its own.

```kotlin
chart.data = LineData(revenue, costs)
```

## BarData

Holds one or more `IBarDataSet`, and owns the two things that are shared by all bars of a chart.

`barWidth` is the width of every bar in x value units, not pixels. It defaults to `0.85`, which leaves a gap of 0.15 between bars that are one x apart.

```kotlin
chart.data = BarData(set).apply { barWidth = 0.55f }
```

`groupBars(fromX, groupSpace, barSpace)` lays the sets out side by side by rewriting the x of their entries. Group *i* is entry *i* of every set, so the position in the list decides the grouping and the x values you gave are lost. Groups are laid out for the set with the most entries, starting at `fromX`. It throws `IllegalStateException` when the data holds fewer than two sets.

`getGroupWidth(groupSpace, barSpace)` returns the x range one group takes:

```kotlin
setCount * (barWidth + barSpace) + groupSpace
```

Use it to set the x axis range so all groups fit:

```kotlin
chart.xAxis.axisMinimum = fromX
chart.xAxis.axisMaximum = fromX + data.getGroupWidth(groupSpace, barSpace) * groupCount
```

`BarData.groupBars` recomputes the cached ranges but does not redraw. `BarChart.groupBars`, which takes the same three arguments, calls it and then `notifyDataSetChanged()` for you. Prefer the one on the chart unless the bars are inside a combined chart.

[Setting data](/mpandroidchart/docs/setting-data/) walks through a full grouped example.

## ScatterData

Holds one or more `IScatterDataSet` and adds one read only property:

```kotlin
val biggest = data.greatestShapeSize
```

`greatestShapeSize` is the largest `scatterShapeSize` in dp over all sets, or `0` when there are none. Nothing in the library reads it; it is there for you to size offsets or a legend form by the biggest shape on screen.

## CandleData

Holds one or more `ICandleDataSet`. It adds nothing of its own.

## BubbleData

Holds one or more `IBubbleDataSet` and adds one broadcast setter, in the style of the ones on `ChartData`:

```kotlin
data.setHighlightCircleWidth(1.5f)
```

It assigns that stroke width in dp to the highlight circle of every set.

## RadarData

Holds one or more `IRadarDataSet`, one polygon each. All sets should have the same number of entries, because entry *i* of every set sits on axis *i* of the web.

The text around the web comes from the x axis, not from the data. Name the axes with a formatter:

```kotlin
val labels = listOf("Speed", "Power", "Range", "Agility")
chart.xAxis.valueFormatter = IndexAxisValueFormatter(labels)
```

`RadarData` also overrides `getEntryForHighlight`. A radar highlight carries the entry index in `Highlight.x`, not an x value, so the lookup goes straight to `getEntryForIndex`. It returns null when the set index is out of range, and throws `IndexOutOfBoundsException` when the entry index is.

## PieData

The odd one out: a pie holds exactly one data set, whose entries are the slices.

```kotlin
val data = PieData(set)
data.dataSet = anotherSet     // replaces the set and recomputes the ranges
```

`yValueSum` is the total of all slice values, the whole pie. The chart itself draws each slice as a share of the sum of the absolute values, which is the same number unless a value is negative.

```kotlin
val share = entry.y / data.yValueSum
```

Because there is always exactly one set, the lookups are narrowed:

- `getDataSetByIndex(0)` returns the set, and any other index returns null.
- `getDataSetByLabel` returns the set if its label matches, and null if not.
- `getEntryForHighlight` reads `Highlight.x` as the slice index, like the radar chart does.

`dataSet` is nullable and reads null while no set has been assigned, which only the empty constructor or assigning null can cause. The lookups then return null, `yValueSum` returns 0, and a pie chart given such data draws no slices and does not fail. Read the set with `pieData.dataSet?.sliceSpace`.

The legend of a pie chart is built from the entry labels. A set label that is not blank is appended after them as an entry without a form, so give the set a blank label to keep it out of the legend.

## CombinedData

Holds up to one of each of the other five data objects and draws them together in a `CombinedChart`.

```kotlin
chart.data = CombinedData().apply {
    barData = BarData(barSet).apply { barWidth = 0.5f }
    lineData = LineData(lineSet)
}
```

| Slot | Type |
| --- | --- |
| `lineData` | `LineData` |
| `barData` | `BarData` |
| `scatterData` | `ScatterData` |
| `candleData` | `CandleData` |
| `bubbleData` | `BubbleData` |

Each slot is null until you fill it, and assigning one recomputes every range.

`allData` is the slots that are filled, always in the order line, bar, scatter, candle, bubble, whatever order you assigned them in. A position in that list is what `Highlight.dataIndex` means, and what `getDataByIndex(index)` takes. That index is the one thing a combined chart adds to highlighting, because a set index alone is no longer unique.

```kotlin
chart.onValueSelected { _, highlight ->
    val data = chart.data ?: return@onValueSelected
    val part = data.getDataByIndex(highlight.dataIndex)
    val set = data.getDataSetByHighlight(highlight)
}
```

`getDataByIndex` throws `IndexOutOfBoundsException` for an index that is not below the size of `allData`. `getDataSetByHighlight` and `getEntryForHighlight` check both indices and return null instead. `chart.highlightValue(x, dataSetIndex)` leaves `dataIndex` at -1, so pass the `dataIndex` when you highlight on a combined chart from code. `getDataIndex(data)` gives you the position of a child data object, or -1.

Note that the draw order on screen is not `allData` order. It comes from `chart.drawOrder`, which defaults to bar, bubble, line, candle, scatter.

### What is not supported

The inherited `dataSets` list is rebuilt from the children on every recalculation, so anything you put there directly is dropped on the next `notifyDataChanged`. Work through the child data objects instead.

| Call | Behaviour |
| --- | --- |
| `addDataSet` | Adds to `dataSets`, which is then discarded. Add to a child instead |
| `removeDataSet(index)` | Logs an error and returns false |
| `removeEntry(entry, index)` | Logs an error and returns false |
| `removeEntry(xValue, index)` | Logs an error and returns false |

`removeDataSet(set)` is the one removal that does work. It finds the first child data object holding that set and removes it there, but it only recomputes that child's ranges. Call `notifyDataChanged()` afterwards, or `chart.notifyDataSetChanged()`, which covers it.

## Where to go next

- [The ChartData class](/mpandroidchart/docs/chartdata/) for everything these classes inherit.
- [Setting data](/mpandroidchart/docs/setting-data/) for a complete example of each chart type.
- [DataSet subclasses](/mpandroidchart/docs/dataset-subclasses/) for the styling each series type offers.
