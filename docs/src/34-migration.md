# Migrating from 3.x

What to change in an app written against MPAndroidChart 3.x when you move it to the Kotlin rewrite.

## What stays the same

Version 4.0 is a rewrite of the same library, not a new one. Every class, package and interface kept its name, so `com.github.mikephil.charting.charts.LineChart`, `LineDataSet`, `XAxis`, `Legend`, `MarkerView` and `ViewPortHandler` are still where they were, and your imports and XML layouts survive untouched.

The work is in the call sites. Getters and setters became properties, arrays became lists, entries gained a type parameter, and a handful of members were renamed or dropped. Everything below is one of those changes.

## Build requirements and dependency

3.1.0 built against `minSdk 14` and `compileSdk 28`. Version 4.0 needs a newer toolchain:

| | |
| --- | --- |
| `minSdk` | 23 |
| `compileSdk` | 37 |
| Java | 17 |

The artifact is split in two, so the old `com.github.PhilJay:MPAndroidChart:v3.1.0` becomes one or two new coordinates:

```kotlin
dependencies {
    implementation("com.github.PhilJay.MPAndroidChart:MPChartLib:v4.0.0-beta01")

    // only if you use Jetpack Compose
    implementation("com.github.PhilJay.MPAndroidChart:MPChartCompose:v4.0.0-beta01")
}
```

JitPack is still the repository. The [getting started chapter](/mpandroidchart/docs/getting-started/) has the full setup.

## Getters and setters are properties

Every getter and setter pair is now a property. Functions that take real parameters, such as `animateX` or `setVisibleXRangeMaximum`, kept their names.

```java
chart.setDragEnabled(true);
chart.getAxisLeft().setAxisMaximum(100f);
chart.getXAxis().setLabelCount(5);
```

```kotlin
val chart = LineChart(this)
chart.isDragEnabled = true
chart.axisLeft.axisMaximum = 100f
chart.xAxis.labelCount = 5
```

These are the ones you will hit most often.

| 3.x call | 4.0 property | Default |
| --- | --- | --- |
| `setDragEnabled` | `isDragEnabled` | true |
| `setScaleEnabled` | `isScaleEnabled` | true |
| `setPinchZoom` | `isPinchZoomEnabled` | false |
| `setDoubleTapToZoomEnabled` | `isDoubleTapToZoomEnabled` | true |
| `setHighlightPerTapEnabled` | `isHighlightPerTapEnabled` | true |
| `setTouchEnabled` | `isTouchEnabled` | true |
| `setDrawGridBackground` | `isDrawGridBackgroundEnabled` | false |
| `getAxisMinimum` | `axisMinimum` | from the data |
| `getAxisMaximum` | `axisMaximum` | from the data |
| `setLabelCount(n)` | `labelCount` | 6 |
| `setTextSize` | `textSize` | 10, clamped to 6..24 |
| `setTextColor` | `textColor` | black |
| `setEnabled` | `isEnabled` | true |
| `setDrawValues` | `isDrawValuesEnabled` | true |
| `setHighlightEnabled` | `isHighlightEnabled` | true |
| `setValueTextSize` | `valueTextSize` | 7 |
| `setLineWidth` | `lineWidth` | 1, clamped to 0..10 |

The last four are on the data set, the six before them on an axis or another text component, the rest on the chart.

Boolean flags are named after their getter, not their setter, so a flag you set with `setDrawFoo(true)` reads `isDrawFooEnabled = true` now. The exceptions are the ones that were never `Enabled` in 3.x either, such as `YAxis.isInverted` and `BaseDataSet.isVisible`.

## Entries carry a payload

`Entry` is now `Entry<out D>`, where `D` is the type of the optional object you attach to a point. In 3.x that object was an untyped `Object` you had to cast on the way out.

```java
Entry e = new Entry(1f, 42f, order);
Order same = (Order) e.getData();
```

```kotlin
val e = Entry(1f, 42f, data = order)
val theOrder: Order? = e.data
```

When you pass no payload, `Entry(1f, 42f)` calls a factory function of the same name and gives you an `Entry<Nothing>`. `Nothing` is a subtype of everything, so those entries still fit anywhere a typed entry is expected, and their `data` is always null. The payload is read-only, so build a new entry instead of changing it.

Stacked bars changed shape along with this. The float array became a list, and `getYVals` became `stackValues`:

```java
BarEntry bar = new BarEntry(0f, new float[] { 10f, 20f, 30f });
float[] parts = bar.getYVals();
```

```kotlin
val bar = BarEntry(0f, listOf(10f, 20f, 30f))
val parts = bar.stackValues
```

Assigning `stackValues` recomputes `y` as their sum, along with `positiveSum`, `negativeSum` and `ranges`. `getBelowSum` was renamed to `getSumBelow`.

## Arrays became lists

Anywhere 3.x took or returned an array, 4.0 uses a `List`. That covers data set colors, the `ColorTemplate` palettes, stack labels, the labels a data object reports, the values of `IndexAxisValueFormatter`, and a combined chart's draw order.

```java
set.setColors(ColorTemplate.MATERIAL_COLORS);
set.setStackLabels(new String[] { "Births", "Divorces" });
chart.getXAxis().setValueFormatter(
        new IndexAxisValueFormatter(new String[] { "Mon", "Tue" }));
```

```kotlin
val set = BarDataSet(entries, "Statistics")
set.colors = ColorTemplate.MATERIAL_COLORS
set.stackLabels = listOf("Births", "Divorces")
chart.xAxis.valueFormatter = IndexAxisValueFormatter(listOf("Mon", "Tue"))
```

`setColors(vararg colors: Int)` is still there for a handful of literal colors, so the spread operator is no longer needed. Gradient bars moved too: 3.x had `setGradientColors(List<Fill>)`, 4.0 has the `fills` property, and `setGradientColor(start, end)` still fills every bar with one gradient.

```kotlin
val bars = BarDataSet(entries, "Revenue")
bars.fills = mutableListOf(Fill(Color.RED, Color.YELLOW))

val combined = CombinedChart(this)
combined.drawOrder = listOf(DrawOrder.BAR, DrawOrder.LINE)
```

## One call refreshes the chart

3.x needed three calls to show changed data. `chart.notifyDataSetChanged()` now does all of it: it calls `notifyDataChanged` on the data, recomputes the axes, the legend and the offsets, and redraws.

```java
data.notifyDataChanged();
chart.notifyDataSetChanged();
chart.invalidate();
```

```kotlin
chart.notifyDataSetChanged()
```

Assigning `chart.data` already calls it, so a fresh data object needs nothing after the assignment.

> This applies to changes made in place, such as adding an entry or editing a value. Replacing the whole data object is still an assignment to `chart.data`.

## Formatters and listeners are fun interfaces

`IValueFormatter` and `IAxisValueFormatter` kept their names and their single method, but they are `fun interface` declarations now and their arguments are non-null. A lambda is enough.

```java
axis.setValueFormatter(new IAxisValueFormatter() {
    public String getFormattedValue(float value, AxisBase axis) {
        return ((int) value) + " %";
    }
});
```

```kotlin
chart.axisLeft.valueFormatter = IAxisValueFormatter { value, _ ->
    "${value.toInt()} %"
}
chart.data?.setValueFormatter { value, _, _, _ -> value.toInt().toString() }
```

`IFillFormatter` works the same way. `OnChartValueSelectedListener` has two methods, so it is a normal interface, but the chart offers a lambda shortcut that replaces it:

```kotlin
chart.onValueSelected { entry, highlight ->
    Log.i("Selected", "${entry.y} in set ${highlight.dataSetIndex}")
}
```

Pass `onNothingSelected` as the first argument when you need the cleared case too. If several parts of your app want to listen, add to `chart.valueSelectedListeners` instead of replacing `chart.onChartValueSelectedListener`.

## The paint constants are gone

`setPaint(paint, PAINT_INFO)` and `getPaint(which)` are removed together with the `PAINT_` constants. Each paint is its own property.

| 3.x constant | 4.0 property |
| --- | --- |
| `PAINT_INFO` | `infoPaint` |
| `PAINT_DESCRIPTION` | `descriptionPaint` |
| `PAINT_GRID_BACKGROUND` | `gridBackgroundPaint` |
| `PAINT_LEGEND_LABEL` | `legendLabelPaint` |
| `PAINT_HOLE` | `holePaint` |
| `PAINT_CENTER_TEXT` | `centerTextPaint` |

```kotlin
val pie = PieChart(this)
pie.holePaint.color = Color.WHITE
pie.infoPaint.textAlign = Paint.Align.CENTER
```

The last two live on `PieChart`, `gridBackgroundPaint` on every chart that extends `BarLineChartBase`, the rest on every chart.

## Renamed and removed members

- `getScaleX()` is `zoomX`, `getScaleY()` is `zoomY`. Both are read-only. The rename frees the name for `View.scaleX`, which now means what Android means by it.
- `legend.setCustom(entries)` is an assignment to `legend.entries`, which sets `isLegendCustom`. `resetCustom()` still turns it off.
- `setLabelCount(count, force)` is two properties: `labelCount` and `isForceLabelsEnabled`.
- `setMarkerView` is `marker`, and the marker picks up the chart when you assign it, so the old `marker.chartView = chart` line can go.
- `saveToPath` is gone. `saveToGallery` writes through the MediaStore and needs no storage permission on Android 10 and newer. `toBitmap()` gives you the pixels if you want to write them yourself.
- `DataSet.getValues()` and `setValues()` are the `entries` property.
- Members deprecated in 3.x were removed outright: `setAxisMinValue` and `setAxisMaxValue` (use `axisMinimum` and `axisMaximum`), `YAxis.setStartAtZero(true)` (use `axisMinimum = 0f`), `LineDataSet.setCircleSize` (use `circleRadius`), `setDrawMarkerViews` (use `isDrawMarkersEnabled`) and `PieChart.setDrawSliceText` (use `isDrawEntryLabelsEnabled`).

Highlighting one value of a stack needs a named argument, because the third positional parameter is `dataIndex`, the index of a data object inside a combined chart:

```kotlin
val bars = BarChart(this)
bars.highlightValue(x = 3f, dataSetIndex = 0, stackIndex = 1)
```

## Sizes in dp stay in dp

3.x converted dp to pixels inside the setter, so `getLineWidth()` returned something other than what you had set and the number depended on the device. 4.0 stores dp and converts when drawing, so `lineWidth = 2.5f` reads back as `2.5f`. This matters wherever you read a size back, scale it, or save and restore it.

## Compose

The Compose module is new, so there is nothing to migrate, but it is the shortest path off `findViewById`. Each chart has a composable of the same name that takes the same data objects, plus a `rememberChartState()` that reports the selection and the viewport back to Compose:

```kotlin
LineChart(
    data = lineData,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    state = rememberChartState(),
    setup = { description.isEnabled = false },
)
```

The [Compose chapter](/mpandroidchart/docs/compose/) covers state, selection, markers and the `setup` and `update` lambdas.

## Checklist

1. Raise `minSdk` to 23, `compileSdk` to 37 and the Java target to 17, then swap the dependency for `MPChartLib` and, if you need it, `MPChartCompose`.
2. Let the compiler find the getters and setters. Most become properties with the same stem, booleans become `isXxxEnabled`.
3. Turn arrays into lists: colors, stack labels, formatter values, draw orders.
4. Give entries a payload type where you used to cast `getData()`, and replace `BarEntry` float arrays with lists.
5. Delete `data.notifyDataChanged()` and `invalidate()` after `notifyDataSetChanged()`.
6. Turn formatter and listener anonymous classes into lambdas.
7. Replace `setPaint(...)` with the named paint property.
8. Fix the renames: `zoomX`, `legend.entries`, `labelCount` with `isForceLabelsEnabled`, `marker`, `entries` on the data set.
9. Check every place you read a dp size back, now that it is no longer converted to pixels.
