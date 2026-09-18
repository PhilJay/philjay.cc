# Dynamic and realtime data

How to add and remove entries and data sets while a chart is on screen, what to call afterwards, and how to keep a fast feed drawing smoothly.

Nothing about a chart is fixed once you have set its data. You can push entries into a data set, append or drop whole data sets, and clear everything. One call tells the chart about it.

## Add an entry

There are two places to add from. Going through the data object is the usual one, because it knows which data set you mean and widens its own cached ranges at the same time.

```kotlin
val data = chart.data ?: return
data.addEntry(Entry(x, y), 0)   // into the data set at index 0
chart.notifyDataSetChanged()
```

Going through the data set works too, and is what you do when you already hold a reference to it.

```kotlin
set.addEntry(Entry(x, y))       // appends at the end
set.addEntryOrdered(Entry(x, y)) // inserts so the entries stay sorted by x
chart.notifyDataSetChanged()
```

`addEntry` appends without looking at the x value. Entries must stay sorted by x ascending, because every lookup on a data set is a binary search over x. Use `addEntryOrdered` whenever the new x is not the largest one.

A whole new series is one call:

```kotlin
val set = LineDataSet(mutableListOf<Entry<Any?>>(), "Live").apply {
    color = Color.BLUE
    lineWidth = 2f
    isDrawCirclesEnabled = false
    isDrawValuesEnabled = false
}

data.addDataSet(set)
chart.notifyDataSetChanged()
```

## Remove data

On a data set:

| Call | Removes |
| --- | --- |
| `removeFirst()` | the entry at index 0 |
| `removeLast()` | the entry at the end |
| `removeEntry(e)` | that exact entry, matched by reference |
| `removeEntry(index)` | the entry at a list index |
| `removeEntryByXValue(x)` | the entry whose x is nearest to `x` |
| `clear()` | every entry, keeping the data set |

`removeFirst`, `removeLast`, `removeEntry(e)` and `removeEntryByXValue` return `false` when there was nothing to remove. `removeEntry(index)` throws `IndexOutOfBoundsException` for an index outside the entries, and `clear()` returns nothing.

On the data object:

| Call | Removes |
| --- | --- |
| `removeEntry(e, dataSetIndex)` | that entry from the data set at the index |
| `removeEntry(xValue, dataSetIndex)` | the entry nearest to `xValue` in that data set |
| `removeDataSet(set)` | that data set |
| `removeDataSet(index)` | the data set at the index |
| `clearValues()` | every data set, keeping the data object |

> On a data set, `removeEntry(index)` takes a list index and `removeEntryByXValue(x)` takes a value. On the data object the float overload `removeEntry(xValue, dataSetIndex)` is the one that takes a value.

## What to call afterwards

One call on the chart:

```kotlin
chart.notifyDataSetChanged()
```

It recomputes the data ranges, rebuilds the renderer buffers, recalculates both y axes and the x axis, rebuilds the legend, recalculates the offsets and redraws. There is no separate `invalidate()` to make.

The one case that needs a second call is changing a data set's entry list in place, without going through `addEntry` or `removeEntry`:

```kotlin
set.entries.add(Entry(x, y))     // the list is modified directly
set.notifyDataSetChanged()       // the set recomputes its own x and y range
chart.notifyDataSetChanged()
```

Assigning a new list does not need that, because the setter recomputes the range for you:

```kotlin
set.entries = newEntries
chart.notifyDataSetChanged()
```

> Version 3.x needed `notifyDataSetChanged()` on the data set, `notifyDataChanged()` on the data object, `notifyDataSetChanged()` on the chart and then `invalidate()`. The chart call now does all four steps.

## Keep a scrolling window

A live chart normally shows the last n values and scrolls as new ones arrive. Two calls do that.

```kotlin
chart.setVisibleXRangeMaximum(120f)             // at most 120 x units on screen
chart.moveViewToX(data.entryCount.toFloat())    // left edge at the newest value
```

`setVisibleXRangeMaximum` works out a minimum zoom factor from the x axis range *at the moment you call it*. When the data keeps growing, that factor no longer matches, and the visible window slowly widens. So call it again after every batch of new entries rather than once at setup. Both calls need data to be set first.

`moveViewToX` runs as a viewport job and redraws by itself, so nothing follows it. [Modifying the viewport](/mpandroidchart/docs/viewport/) covers the rest of these calls.

## The realtime pattern

This is the loop the example app's `RealtimeLineChartActivity` uses, one entry per tick:

```kotlin
private fun addEntry() {
    val data = chart.data ?: return
    val set = data.getDataSetByIndex(0) ?: createSet().also { data.addDataSet(it) }

    data.addEntry(Entry(set.entryCount.toFloat(), nextReading()), 0)

    chart.notifyDataSetChanged()
    chart.setVisibleXRangeMaximum(120f)
    chart.moveViewToX(data.entryCount.toFloat())
}
```

Set the chart up once with an empty `LineData` so that `chart.data` is never null, and give the y axis a fixed range so the chart does not rescale on every reading:

```kotlin
chart.data = LineData()
chart.axisLeft.axisMinimum = 0f
chart.axisLeft.axisMaximum = 100f
chart.axisRight.isEnabled = false
```

Call `addEntry` on the UI thread. A background producer should hand its readings over with `runOnUiThread` or a coroutine on the main dispatcher; the chart is a `View` and does not synchronise its data.

## Clear the chart

| Call | Effect |
| --- | --- |
| `chart.clear()` | drops the data object, clears the highlight and shows the no data text |
| `chart.clearValues()` | removes every data set but keeps the data object |
| `data.clearValues()` | the same, without the redraw |
| `set.clear()` | empties one data set |

`chart.clear()` is the one to use when a screen is reused for a different source. `chart.clearValues()` keeps a live chart alive with an empty data object, ready for the next entry.

## Large or fast data

The renderer already draws only the entries inside the visible x range, so a large data set costs mostly memory, not draw time. [Performance with large data](/mpandroidchart/docs/performance/) goes through all of it; the short list of what costs draw time:

- **Circles.** `isDrawCirclesEnabled = false` on a line data set removes one draw call per point.
- **Value labels.** `isDrawValuesEnabled = false`. Labels are skipped automatically once the entry count reaches `chart.maxVisibleCount` (default 100) times the current zoom, but turning them off saves the check.
- **Curves.** `LineDataSet.Mode.LINEAR` is cheaper than `CUBIC_BEZIER`.
- **Line width.** Thin lines draw faster; the value is clamped to 0 to 10 dp.
- **Dashed lines.** A dashed line goes onto the offscreen bitmap and is composed onto the chart, which costs an extra pass per frame.

For a feed that never stops, cap the entry count instead of letting it grow:

```kotlin
if (set.entryCount > 500) set.removeFirst()
```

If every frame matters, do not let the chart recompute the axes. `isAutoScaleMinMaxEnabled = false` is the default, and fixed `axisMinimum` and `axisMaximum` values on the y axis keep `notifyDataSetChanged` from reflowing the labels and the offsets.

## Where to go next

- [Modifying the viewport](/mpandroidchart/docs/viewport/) for the scrolling window in detail.
- [The ChartData class](/mpandroidchart/docs/chartdata/) and [the DataSet class](/mpandroidchart/docs/dataset/) for everything these two classes hold.
- [Setting data](/mpandroidchart/docs/setting-data/) for the entry and data set types of each chart.
