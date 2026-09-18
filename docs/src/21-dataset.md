# The DataSet class

The styling and behaviour every data set shares, from the legend label to the entry lookups and the cached value ranges.

A data set is one series: the entries that belong together plus the settings for drawing them. `LineDataSet`, `BarDataSet`, `PieDataSet` and the rest all inherit what this chapter describes, so anything here works on any of them.

## Where it sits

Three levels carry the shared behaviour.

- `IDataSet<T>` is the interface. Renderers and highlighters only ever read this, never a concrete class. See [Custom data sets](/mpandroidchart/docs/custom-datasets/).
- `BaseDataSet<T>` implements the styling: colors, value labels, legend form, axis, visibility. It leaves entry storage open.
- `DataSet<T>` adds the entry list, the cached ranges and the lookups.

Each chart type then has its own subclass with its own properties, described in [DataSet subclasses](/mpandroidchart/docs/dataset-subclasses/).

## Naming, visibility and axis

```kotlin
val set = LineDataSet(entries, "Revenue")
set.label = "Revenue 2024"
set.isVisible = false
set.axisDependency = YAxis.AxisDependency.RIGHT
```

| Property | Meaning | Default |
| --- | --- | --- |
| `label` | name in the legend, and the key for `data.getDataSetByLabel(...)` | the constructor argument |
| `isVisible` | whether the set is drawn | `true` |
| `axisDependency` | which y axis the set is plotted against | `LEFT` |

> A hidden set is not drawn but still counts towards the axis ranges, so hiding a set does not rescale the chart.

## Value labels

The numbers drawn next to the entries are styled on the set.

```kotlin
set.isDrawValuesEnabled = true
set.valueTextSize = 10f
set.valueTextColor = Color.DKGRAY
set.valueTypeface = tfLight
set.valueFormatter = MyValueFormatter()
```

| Property | Meaning | Default |
| --- | --- | --- |
| `isDrawValuesEnabled` | draw the labels at all | `true` |
| `valueTextSize` | text size in dp | `7f` |
| `valueTextColor` | first of `valueTextColors` when read, replaces the whole list when written | black |
| `valueTextColors` | one color per entry, cycled like `colors` | one black |
| `valueTypeface` | typeface, `null` for the default | `null` |
| `valueFormatter` | turns a value into the label text | the chart's default |

Until you assign a formatter, `needsFormatter` stays true and the chart hands the set its own default formatter, which picks a digit count from the value range. See [Formatters](/mpandroidchart/docs/formatters/).

To style every set at once, call the same things on the data object: `data.setValueTextSize(10f)`, `data.setValueTextColor(...)`, `data.setDrawValues(false)`.

> Values are also left out when more entries are visible than the chart's `maxVisibleCount` allows, no matter what the set says.

## Icons

An entry can carry a `Drawable` that is drawn at its position.

```kotlin
val star = ContextCompat.getDrawable(this, R.drawable.star)
val entries = listOf(Entry(0f, 4f, icon = star))
set.isDrawIconsEnabled = true
set.iconsOffset = MPPointF(0f, -12f)
```

`iconsOffset` is in dp and moves every icon of the set. On pie and radar charts x moves the icon along the value direction and y towards or away from the center. Like values, icons are skipped once `maxVisibleCount` is exceeded.

## The legend form

By default every set is drawn in the legend with the legend's own form. These four properties override it for one set only.

| Property | Meaning | Default |
| --- | --- | --- |
| `form` | shape of the form | `LegendForm.DEFAULT`, the legend's form |
| `formSize` | size in dp | `Float.NaN`, the legend's size |
| `formLineWidth` | stroke width in dp for a line form | `Float.NaN`, the legend's width |
| `formLineDashEffect` | dash pattern for a line form | `null`, the legend's dash effect |

```kotlin
set.form = Legend.LegendForm.LINE
set.formLineWidth = 2f
set.formLineDashEffect = DashPathEffect(floatArrayOf(10f, 5f), 0f)
```

More in [The legend](/mpandroidchart/docs/legend/).

## Highlighting

`isHighlightEnabled` decides whether entries of this set can be selected, by touch or by `chart.highlightValue(...)`. It defaults to true.

```kotlin
set.isHighlightEnabled = false
```

The look of the highlight is set per subclass: indicator lines on line, scatter, candle and radar sets, an overlay on bars, a shift on pie slices. See [Highlighting](/mpandroidchart/docs/highlighting/).

## Reading entries

The entries live in `entries`, a `MutableList`. The list you hand to the constructor is kept by reference when it is an `ArrayList` and copied otherwise; a list you assign later is always kept by reference. Either way, assigning recomputes the ranges.

```kotlin
set.entries = newEntries
chart.notifyDataSetChanged()
```

| Call | Returns |
| --- | --- |
| `entryCount` | number of entries |
| `getEntryForIndex(index)` | the entry at that list position, throws when the index is out of range |
| `getEntryForXValue(x, closestToY, rounding)` | the entry at or nearest to that x, or `null` when the set is empty |
| `getEntryIndex(x, closestToY, rounding)` | the same as an index, or -1 when the set is empty |
| `getEntriesForXValue(x)` | every entry whose x matches exactly, empty when there is none |
| `getEntryIndex(entry)` | the list position of that exact entry object, or -1 |
| `getIndexInEntries(xIndex)` | the first entry with exactly that x, by scanning, or -1 |
| `contains(entry)` | true if that exact entry object is in the set |

`contains` and `getIndexInEntries` walk the whole list, so keep them out of tight loops. The x value lookups use binary search instead, which is fast but requires the entries to be sorted by x ascending.

## Rounding when there is no exact match

`getEntryForXValue` and `getEntryIndex` almost never get an x that an entry has exactly, so they take two extra arguments, both with defaults.

`rounding` decides which neighbour wins:

| `DataSet.Rounding` | Picks |
| --- | --- |
| `CLOSEST` (the default) | the entry whose x is nearest; on a tie the larger x |
| `UP` | the same, but moves one entry up when the nearest x is below the requested one, unless it is already the last |
| `DOWN` | the same, but moves one entry down when the nearest x is above the requested one, unless it is already the first |

`closestToY` only matters when several entries share the found x value. Pass a y and the one closest to it is returned; leave it at `Float.NaN` and the first of them wins.

```kotlin
val entry = set.getEntryForXValue(12.4f)                                   // nearest
val below = set.getEntryForXValue(12.4f, Float.NaN, DataSet.Rounding.DOWN)
```

## Adding and removing entries

```kotlin
set.addEntry(Entry(10f, 42f))         // appends, no order check
set.addEntryOrdered(Entry(4.5f, 18f)) // inserts so the entries stay sorted by x
set.removeFirst()
set.removeLast()
set.removeEntry(entry)
set.removeEntry(index)
set.removeEntryByXValue(12.4f)
set.clear()
```

`addEntry` is the fast one: it appends and only widens the cached ranges. Use it when your data arrives in x order. `addEntryOrdered` appends too when the new x is not smaller than the last one, and otherwise binary searches for the insert position, so the lookups keep working.

Removing an entry recomputes the whole range, which costs a pass over the entries. `removeEntryByXValue` removes the entry nearest to the x you pass, not only an exact match.

> `removeEntry(index)` throws `IndexOutOfBoundsException` for an index outside the list rather than returning false. Check the index yourself.

## The cached ranges

A set caches `xMin`, `xMax`, `yMin` and `yMax` so the chart does not walk the entries on every frame. An empty set reports `Float.MAX_VALUE` for the minimums and `-Float.MAX_VALUE` for the maximums.

The cache is refreshed for you when you assign `entries`, add an entry or remove one. It is not refreshed when you change something inside the list, for example the y of an entry you are holding. Then call it yourself:

```kotlin
entry.y = 17f
set.notifyDataSetChanged()   // recomputes this set's ranges
chart.notifyDataSetChanged() // recomputes the axes and redraws
```

`chart.notifyDataSetChanged()` builds the axis ranges from the sets' cached ranges, so the set has to be up to date first. `calcMinMax()` does the same work as `notifyDataSetChanged()` on the set; `calcMinMaxY(fromX, toX)` recomputes only the y range over a slice of the x range, which is what charts with `isAutoScaleMinMaxEnabled` use.

## Copying a set

`copy()` returns a new set of the same class.

```kotlin
val faded = set.copy()
faded.color = Color.LTGRAY
```

The entries are copied one by one with `Entry.copy()`, so changing an entry in the copy does not change the original. The icon and the entry payload are shared, not duplicated. The label and the styling are carried over, and `colors`, `valueTextColors` and the value formatter are shared rather than duplicated. Only `PieDataSet` leaves its own properties behind, noted in [DataSet subclasses](/mpandroidchart/docs/dataset-subclasses/).
