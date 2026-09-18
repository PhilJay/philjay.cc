# Custom data sets

How to write your own data set class, what the renderers actually read from it, and how far you can go before you have to touch a renderer.

Renderers and highlighters never see `LineDataSet` or `BarDataSet`. They only ever read an interface. That is the whole trick: give a chart something that answers those interface calls and it draws it, whatever the class behind it is.

## The interface hierarchy

Four interfaces build on each other, and each chart type has its own leaf.

| Interface | Adds | Implemented by |
| --- | --- | --- |
| `IDataSet<T>` | entries, colors, value labels, legend form, visibility | every data set |
| `IBarLineScatterCandleBubbleDataSet<T>` | `highlightColor` | the sets on an x and y axis |
| `ILineScatterCandleRadarDataSet<T>` | the highlight crosshair lines | line, scatter, candle, radar |
| `ILineRadarDataSet<T>` | line width and the filled area | line, radar |

The leaves are `ILineDataSet`, `IBarDataSet`, `IScatterDataSet`, `ICandleDataSet`, `IBubbleDataSet`, `IRadarDataSet` and `IPieDataSet`. `IPieDataSet` extends `IDataSet` directly, because a pie has no axes.

The data objects are typed on those interfaces, not on the classes:

```kotlin
open class LineData : BarLineScatterCandleBubbleData<ILineDataSet<*>>
open class BarData : BarLineScatterCandleBubbleData<IBarDataSet<*>>
```

So anything implementing `ILineDataSet<*>` goes into a `LineData` and is drawn like any other line.

## What the renderers read

Renderers take the interface as their parameter, for example `BarChartRenderer.drawDataSet(c, dataSet: IBarDataSet<*>, index)` and `LineChartRenderer.drawLinear(c, dataSet: ILineDataSet<*>)`. The highlighters do the same with `IDataSet` and `IBarDataSet`.

Two things follow.

First, anything the interface exposes is yours to compute. `getColor(index)` does not have to read a list, `entryCount` does not have to be a list size, `getEntryForIndex(index)` can build an entry on the fly.

Second, anything the interface does not expose is out of reach. You cannot add a new visual feature this way, only change the answers the renderer gets. For a new feature you subclass the renderer and set it on the chart instead.

It also pays to know how the renderer uses an answer. A line, for instance, is only drawn segment by segment with `getColor(j)` when `colors.size > 1`; with a single color it takes `color` once for the whole line. A custom `getColor` therefore needs the list to have at least two entries, whatever it returns.

## Subclassing a concrete set

This is the shortest route and covers most cases. You inherit everything and override the one thing you want to decide yourself.

Here is a line set that colors each segment by whether the value is above a threshold:

```kotlin
class ThresholdLineDataSet(
    entries: List<Entry<Nothing>>,
    label: String,
    private val threshold: Float,
    private val above: Int = Color.RED,
    private val below: Int = Color.GREEN,
) : LineDataSet<Nothing>(entries, label) {

    init {
        colors = listOf(above, below) // two colors, so the renderer draws per segment
    }

    override fun getColor(index: Int): Int =
        if (getEntryForIndex(index).y >= threshold) above else below
}
```

It goes into the chart unchanged:

```kotlin
chart.data = LineData(ThresholdLineDataSet(entries, "Load", threshold = 80f))
```

`copy()` is worth a thought. The inherited one returns a plain `LineDataSet`, so override it if your code relies on the copy keeping its class:

```kotlin
override fun copy(): DataSet<Entry<Nothing>> {
    val copies = entries.map { it.copy() }
    val copied = ThresholdLineDataSet(copies, label, threshold, above, below)
    copy(copied)
    return copied
}
```

## Building on DataSet

When you want your own properties as well, extend the abstract class one level above the concrete set and implement the chart's interface yourself. You keep the entry list, the lookups and the cached ranges, and only fill in the leaf interface.

```kotlin
class MyBarDataSet<D>(entries: List<BarEntry<D>>, label: String) :
    BarLineScatterCandleBubbleDataSet<BarEntry<D>>(entries, label), IBarDataSet<D> {

    override val fills: List<Fill>? = null
    override fun getFill(index: Int): Fill = error("no fills")
    override val isStacked = false
    override val stackSize = 1
    override val stackLabels: List<String> = emptyList()
    override val barShadowColor = Color.LTGRAY
    override val barBorderWidth = 0f
    override val barBorderColor = Color.BLACK
    override val barCornerRadius = 8f
    override val highlightAlpha = 120

    override fun copy(): DataSet<BarEntry<D>> =
        MyBarDataSet(entries.map { it.copy() }, label).also { copy(it) }
}
```

The same pattern works for the other chart types: pick `LineScatterCandleRadarDataSet`, `LineRadarDataSet` or plain `DataSet` as the base, depending on how much of the shared styling you want to inherit.

## Building on BaseDataSet

Go one level lower and you get the styling but no entry storage, which is the point: the entries can come from wherever you like, a domain object list, a ring buffer, a cursor.

`BaseDataSet` already answers everything about colors, value labels, the legend form, visibility and the axis, plus `contains`, `getIndexInEntries`, `removeFirst`, `removeLast`, `removeEntry(index)` and `removeEntryByXValue`, all of which it builds on `getEntryForIndex`, `entryCount` and, for `removeEntryByXValue`, your `getEntryForXValue` and `removeEntry(entry)`. What is left for you:

- the ranges `xMin`, `xMax`, `yMin`, `yMax`, and `calcMinMax()` and `calcMinMaxY(fromX, toX)` that refresh them
- `entryCount` and `getEntryForIndex(index)`
- the lookups `getEntryForXValue`, `getEntryIndex(xValue, closestToY, rounding)`, `getEntryIndex(entry)` and `getEntriesForXValue`
- the mutations `addEntry`, `addEntryOrdered`, `removeEntry(entry)` and `clear`

```kotlin
class SalesDataSet(private val sales: List<Sale>, label: String) :
    BaseDataSet<BarEntry<Sale>>(label), IBarDataSet<Sale> {

    override val entryCount get() = sales.size
    override val xMin get() = 0f
    override val xMax get() = (sales.size - 1).toFloat()
    override val yMin get() = sales.minOf { it.amount }
    override val yMax get() = sales.maxOf { it.amount }

    override fun getEntryForIndex(index: Int) =
        BarEntry(index.toFloat(), sales[index].amount, data = sales[index])

    // the remaining lookups and mutations, and the bar styling of IBarDataSet:
    // fills, getFill, isStacked, stackSize, stackLabels, barShadowColor,
    // barBorderWidth, barBorderColor, barCornerRadius, highlightAlpha, highlightColor
}
```

A read-only set can throw from the mutations, or ignore them, as long as nothing in your code calls them. The chart itself never does.

> The entries you hand out are expected in ascending x order, and the lookups are expected to be cheap. The chart calls `getEntryForIndex` for every visible entry on every frame, so do not allocate more than you have to and do not scan the whole list there.

## Plugging it in

Nothing special is needed. Put the set in the matching data object and assign it:

```kotlin
chart.data = BarData(SalesDataSet(sales, "Sales"))
```

Mixed lists work too, since they are lists of the interface:

```kotlin
chart.data = LineData(
    ThresholdLineDataSet(entries, "Load", 80f),
    LineDataSet(other, "Baseline"),
)
```

If your set computes its values from something that changes, call `chart.notifyDataSetChanged()` after the change so the axes and the offsets are recalculated, and remember that the chart reads your cached ranges rather than recomputing them from the entries. Details in [The DataSet class](/mpandroidchart/docs/dataset/).

A custom data set changes what is drawn. To change how it is drawn, carry on to [Custom renderers](/mpandroidchart/docs/custom-renderers/).
