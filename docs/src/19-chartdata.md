# The ChartData class

The base class behind LineData, BarData and the rest: the list of data sets, the cached ranges over them, and the lookups and broadcast styling every data object shares.

## What it holds

`ChartData` is a list of data sets plus four numbers describing the extent of everything in them. A chart reads those numbers to size its axes, so they have to be right before anything is drawn.

```kotlin
val data: LineData = chart.data ?: return

data.dataSetCount   // number of series
data.entryCount     // number of values over all series
data.dataSets       // the series themselves, in drawing order
```

`dataSets` is a mutable list, and the sets in it keep their own entries and styling. It is ordered: the first set is drawn first and ends up at the bottom.

Two more convenience lists come off it:

```kotlin
data.dataSetLabels        // every set's label, in set order
data.colors               // every set's colors, set by set, in one flat list
data.maxEntryCountSet     // the set with the most entries, or null
```

## The cached ranges

Four properties describe the data as a whole. They are read only from the outside.

| Property | Meaning | Value with no data |
| --- | --- | --- |
| `xMin` | Smallest x over all sets | `Float.MAX_VALUE` |
| `xMax` | Largest x over all sets | `-Float.MAX_VALUE` |
| `yMin` | Smallest y over all sets, both axes | `Float.MAX_VALUE` |
| `yMax` | Largest y over all sets, both axes | `-Float.MAX_VALUE` |

The per axis ranges are functions, because a set belongs to one y axis through its `axisDependency`:

```kotlin
val bottom = data.getYMin(YAxis.AxisDependency.LEFT)
val top = data.getYMax(YAxis.AxisDependency.LEFT)
```

When no set uses the axis you ask for, you get the other axis' value instead, so both axes end up showing the same range.

These are caches, not live values. They are computed once when the data object is constructed, and again whenever you go through `ChartData`:

- `addDataSet` and `addEntry` widen the ranges to include what you added, which is cheap.
- `removeDataSet`, `removeEntry` and `clearValues` recompute them from scratch.
- `notifyDataChanged` recomputes them from scratch.

Changing a set's entries in place does none of that, which is the one case you have to handle yourself.

## notifyDataChanged and notifyDataSetChanged

`ChartData.notifyDataChanged()` recomputes the cached ranges from the ranges the sets report. It does not ask the sets to recompute theirs, and it does not redraw anything.

So after editing a set's entries directly, the full sequence is three steps:

```kotlin
set.entries.add(Entry(9f, 42f))
set.notifyDataSetChanged()      // the set recomputes its own range
chart.notifyDataSetChanged()   // the data recomputes, the chart redraws
```

`chart.notifyDataSetChanged()` calls `data.notifyDataChanged()` for you, then recalculates the axis ranges, the legend and the offsets and invalidates the view. In everyday code it is the only one of the three you call, because the safe ways of changing data do the rest:

```kotlin
data.addEntry(Entry(9f, 42f), dataSetIndex = 0)
chart.notifyDataSetChanged()
```

> In version 3.x you called `notifyDataSetChanged()` on the set, `notifyDataChanged()` on the data, `notifyDataSetChanged()` on the chart and then `invalidate()`. The chart's call now covers the last three.

There is one more, used by charts that auto scale the y axis to what is visible:

```kotlin
data.calcMinMaxY(fromX, toX)
```

It tells every set to recompute its y range from the entries in that x window only, then recomputes the cached ranges from them.

## Adding and removing data sets

```kotlin
data.addDataSet(LineDataSet(entries, "Costs"))
data.removeDataSet(set)
data.removeDataSet(index = 1)
data.clearValues()
```

`addDataSet` appends and widens the ranges. A null set is ignored.

Both `removeDataSet` overloads return `true` when something was removed and recompute the ranges. They return `false` for a null set, a set that is not part of this data, or an index outside the list. `clearValues` removes every set and resets the ranges.

You can also touch `dataSets` directly, but then nothing recomputes:

```kotlin
data.dataSets.add(0, background)   // now drawn first
data.notifyDataChanged()
```

## Adding and removing entries

```kotlin
data.addEntry(Entry(9f, 42f), 0)
data.removeEntry(entry, 0)
data.removeEntry(xValue = 9f, dataSetIndex = 0)
```

`addEntry` appends to the set at that index and widens the ranges. It does not keep the entries sorted by x, so for an entry that belongs in the middle use `set.addEntryOrdered` and call `notifyDataChanged` yourself.

`removeEntry(xValue, dataSetIndex)` removes the entry whose x is *closest* to the value you give. It does not have to match exactly, so pass an x you know is in the set.

## Finding things

```kotlin
data.getDataSetByIndex(0)                 // null when the index is out of range
data.getDataSetByLabel("Costs", true)     // null when no label matches
data.getIndexOfDataSet(set)               // -1 when the set is not in this data
data.contains(set)                        // true when it is
```

`getDataSetByLabel` takes a second argument that decides whether the comparison ignores case. It scans the list, so it is linear in the number of sets.

Two lookups start from something the user picked. In a value selected listener you get a `Highlight`, and this turns it back into your data:

```kotlin
chart.onValueSelected { entry, highlight ->
    val set = chart.data?.getDataSetByIndex(highlight.dataSetIndex)
    val same = chart.data?.getEntryForHighlight(highlight)
}
```

`getEntryForHighlight` returns the entry in the set at `Highlight.dataSetIndex` whose x is closest to the highlight's x, and among entries with the same x the one whose y is closest. It returns null when the set index is too high or the set is empty.

`getDataSetForEntry` goes the other way, from an entry to the set that holds it:

```kotlin
val owner = data.getDataSetForEntry(entry)
```

It looks each set up by x and y and compares with `Entry.equalTo`, which matches x and y within a small epsilon and requires the same payload instance. It returns null for a null entry or when no set has a match.

## Styling every set at once

These functions loop over the sets and assign the same value to each. They are a shortcut for the common case where all the series should look alike, and they overwrite whatever a single set had.

| Call | Effect |
| --- | --- |
| `setValueTextColor(color)` | One value label color for every set |
| `setValueTextColors(colors)` | The same list of value label colors for every set |
| `setValueTextSize(size)` | Value label size in dp for every set |
| `setValueTypeface(tf)` | Value label typeface for every set; null uses the default |
| `setValueFormatter(f)` | The same `IValueFormatter` on every set |
| `setDrawValues(enabled)` | Value labels on or off for every set |

```kotlin
chart.data = PieData(set).apply {
    setValueFormatter(PercentFormatter())
    setValueTextSize(11f)
    setValueTextColor(Color.WHITE)
}
```

Assigning a data object hands the chart's default formatter to every set that has none of its own. A set you gave a formatter to, through `setValueFormatter` here or on the set itself, is left alone, so it does not matter whether you call it before or after assigning the data.

## isHighlightEnabled

This one is a property rather than a pair of calls, and it reads and writes differently.

```kotlin
data.isHighlightEnabled = false          // switches it off on every set
val allOn = data.isHighlightEnabled      // true only when every set allows it
```

Reading it is an "all" over the sets, so a data object with no sets reads `true`. Writing it applies the value to each set. Highlighting stays off for a set you switch off individually afterwards.

## Errors on a bad index

The data object is forgiving in some places and not in others, which is worth knowing before you pass an index you have not checked.

| Call | Bad index | Result |
| --- | --- | --- |
| `getDataSetByIndex` | Out of range or negative | Returns null |
| `removeDataSet(index)` | Out of range or negative | Returns false |
| `addEntry` | Out of range or negative | Logs an error, adds nothing |
| `removeEntry(entry, index)` | Too high | Returns false |
| `removeEntry(entry, index)` | Negative | Throws `IndexOutOfBoundsException` |
| `removeEntry(xValue, index)` | Too high | Returns false |
| `removeEntry(xValue, index)` | Negative | Throws `IndexOutOfBoundsException` |

`PieData` and `CombinedData` override some of these and throw where the base class returns null. [ChartData subclasses](/mpandroidchart/docs/chartdata-subclasses/) lists what each one changes.

## Where to go next

- [ChartData subclasses](/mpandroidchart/docs/chartdata-subclasses/) for the additions each data class makes.
- [Setting data](/mpandroidchart/docs/setting-data/) for building the data object in the first place.
- [Dynamic data](/mpandroidchart/docs/dynamic-data/) for adding and removing values while the chart is on screen.
- [The DataSet class](/mpandroidchart/docs/dataset/) for the other half of the data model.
