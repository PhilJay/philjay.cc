# Highlighting values

How a value gets selected, how to select one from code, what the resulting Highlight object holds, and how to style the indicator that marks it.

## What a highlight is

A highlight is one selected value. It is not stored on the entry: the chart keeps a list of `Highlight` objects that say which data set and which x value are selected. From that list the chart draws the highlight indicator, draws the [marker](/mpandroidchart/docs/markers/), and calls the value selected listener.

A highlight appears in three ways: the user taps a value, the user drags across a chart that cannot pan, or your code calls `highlightValue(...)`.

## Highlighting by touch

Three properties decide what touch does.

| Property | Meaning | Default |
| --- | --- | --- |
| `chart.isHighlightPerTapEnabled` | A tap selects the nearest value | `true` |
| `chart.isHighlightPerDragEnabled` | Dragging moves the selection while the chart cannot pan | `true` |
| `chart.maxHighlightDistance` | Farthest distance in dp a touch may be from a value | `500` |

`isHighlightPerDragEnabled` only takes effect while the chart is fully zoomed out and has no drag offset, because otherwise the drag pans the content. It exists on the charts with axes; `isHighlightPerTapEnabled` exists on every chart type.

A single data set can opt out entirely:

```kotlin
dataSet.isHighlightEnabled = false   // touches never select a value of this set
```

> `maxHighlightDistance` and `isHighlightEnabled` are read by the highlighters of the charts with axes. Pie and radar charts select whatever entry lies under the touch angle as long as the touch is inside the chart radius, so neither setting changes anything there.

Tapping the value that is already selected clears the selection.

## Highlighting from code

The overload you reach for most takes an x value and a data set index:

```kotlin
chart.highlightValue(9f, 0)                      // entry at x = 9 in the first data set
chart.highlightValue(9f, 0, callListener = false)  // same, without notifying listeners
```

If several entries share that x value, pass the y value too and the nearest one is chosen:

```kotlin
chart.highlightValue(9f, 42f, 0)
```

The full signatures are:

```kotlin
fun highlightValue(
    x: Float,
    dataSetIndex: Int,
    dataIndex: Int = -1,
    stackIndex: Int = -1,
    callListener: Boolean = true,
)

fun highlightValue(
    x: Float,
    y: Float,
    dataSetIndex: Int,
    dataIndex: Int = -1,
    stackIndex: Int = -1,
    callListener: Boolean = true,
)
fun highlightValue(highlight: Highlight?, callListener: Boolean = true)
fun highlightValues(highs: List<Highlight>)
```

`stackIndex` picks one value inside a stacked bar entry; -1 means the whole bar. `dataIndex` is only for `CombinedChart` and names the data object inside the combined data, for example 0 for its line data and 1 for its bar data. A `dataSetIndex` that is outside the data clears the highlight instead of selecting something.

`highlightValues` sets several highlights at once. It takes the list as given, without checking that the entries exist, and never calls a listener.

> Every `highlightValue` overload defaults `callListener` to `true`, so a selection made from code reaches your listener unless you pass `callListener = false`. `highlightValues` never calls a listener.

## Clearing a highlight

```kotlin
chart.highlightValue(null)                        // clear and call onNothingSelected
chart.highlightValue(null, callListener = false)  // clear without notifying
chart.highlightValues(emptyList())                // clear, never calls a listener
```

`chart.clear()` removes the data and the highlight together.

## Reading the current highlight

```kotlin
val current: List<Highlight> = chart.highlighted

if (chart.valuesToHighlight()) {
    val h = current.first()
    val entry = chart.data?.getEntryForHighlight(h)
}
```

`highlighted` is empty, never null, when nothing is selected.

> In version 3.x `getHighlighted()` returned an array that could be null. It is a read-only `List` now, and an empty list means nothing is selected.

## The Highlight class

`Highlight` answers both questions: which value is selected, and where it sits on screen. Be aware which of its fields are in value space and which are in pixels.

| Field | Space | Meaning |
| --- | --- | --- |
| `x` | value | x value of the entry. On pie and radar charts this is the entry index |
| `y` | value | y value of the entry, `NaN` when the highlight was built from x alone |
| `xPx`, `yPx` | pixels | position of the entry, filled in by the highlighter from a touch |
| `drawX`, `drawY` | pixels | position where the indicator was last drawn, written by the renderer |
| `dataSetIndex` | | index of the data set the entry belongs to |
| `dataIndex` | | index of the data object in a `CombinedChart`, -1 otherwise |
| `stackIndex` | | index inside a stacked bar entry, -1 when not stacked |
| `axis` | | the y axis the entry is plotted against, null when unknown |
| `isStacked` | | true when `stackIndex` is 0 or more |

The marker is placed at `drawX` and `drawY`, not at `xPx` and `yPx`, because the renderer may shift the point, for instance to the top center of a bar or into a pie slice.

You can build a `Highlight` yourself and pass it to the chart. The constructor that takes values needs the y value as well; pass `Float.NaN` to accept any y:

```kotlin
val highlight = Highlight(50f, Float.NaN, dataSetIndex = 0)
chart.highlightValue(highlight, callListener = false)
```

A stacked bar value has its own constructor:

```kotlin
val highlight = Highlight(x = 3f, dataSetIndex = 0, stackIndex = 1)
```

`h.equalTo(other)` compares the data set index, x value, stack index and data index, ignoring the y value and the pixel positions. The chart uses it to notice that you tapped the already selected value.

> Version 3.x had a two argument constructor `Highlight(x, dataSetIndex)`. It is gone; pass the y value or `Float.NaN`.

## Styling the indicator

The indicator is drawn per data set, so different series can look different.

Line, scatter, candle and radar sets draw crosshair lines:

| Property | Meaning | Default |
| --- | --- | --- |
| `highlightColor` | Color of the lines | orange, `rgb(255, 187, 115)` |
| `highlightLineWidth` | Line width in dp | `0.5` |
| `isVerticalHighlightIndicatorEnabled` | Draw the vertical line | `true` |
| `isHorizontalHighlightIndicatorEnabled` | Draw the horizontal line | `true` |
| `verticalHighlightIndicatorSpan` | How far the vertical line reaches | `HighlightLineSpan.FULL` |
| `horizontalHighlightIndicatorSpan` | How far the horizontal line reaches | `HighlightLineSpan.FULL` |

```kotlin
set.highlightColor = Color.WHITE
set.highlightLineWidth = 1f
set.isHorizontalHighlightIndicatorEnabled = false
set.enableDashedHighlightLine(8f, 8f, 0f)   // dash length, gap, phase, in px
```

A span of `FULL` draws the line from one edge of the chart to the other. `TO_ENTRY` stops it at the entry, coming from the bottom for the vertical line and from the left for the horizontal one, and `FROM_ENTRY` draws the other half.

```kotlin
set.verticalHighlightIndicatorSpan = HighlightLineSpan.TO_ENTRY
```

`setDrawHighlightIndicators(false)` turns both lines off in one call, `disableDashedHighlightLine()` makes them solid again, and `isDashedHighlightLineEnabled` tells you which they are.

A line data set can also mark the selected point with a ring:

```kotlin
set.isDrawHighlightCircleEnabled = true   // default false
set.highlightCircleRadius = 6f            // dp, default 5
set.circleHoleColor = cardBackground
```

The ring is drawn in the line color with a soft halo behind it in `highlightColor` and a center in `circleHoleColor`. This is what the showcase charts in the example app use together with a dashed vertical line.

Bar, pie and radar sets style the selection differently:

| Set | Property | Meaning | Default |
| --- | --- | --- | --- |
| `BarDataSet` | `highlightColor` | Color of the overlay drawn over the bar | black |
| `BarDataSet` | `highlightAlpha` | Opacity of that overlay, 0 to 255 | `120` |
| `PieDataSet` | `highlightColor` | Color of the selected slice, null keeps the slice color | `null` |
| `PieDataSet` | `selectionShift` | How far in dp the slice moves outwards | `9` |
| `RadarDataSet` | `isDrawHighlightCircleEnabled` | Draw a ring at the selected entry | `false` |
| `RadarDataSet` | `highlightCircleInnerRadius` | Inner radius in dp | `3` |
| `RadarDataSet` | `highlightCircleOuterRadius` | Outer radius in dp | `4` |
| `RadarDataSet` | `highlightCircleFillColor` | Fill of the ring | white |
| `RadarDataSet` | `highlightCircleStrokeColor` | Stroke of the ring, `COLOR_NONE` uses the set color | `COLOR_NONE` |
| `RadarDataSet` | `highlightCircleStrokeWidth` | Stroke width in dp | `2` |
| `RadarDataSet` | `highlightCircleStrokeAlpha` | Stroke opacity, 0 to 255 | `76` |

Setting `highlightAlpha` to 0 hides the bar overlay, which is useful when a marker already shows the selection.

## Whole bars and stacked values

By default a tap on a stacked bar selects the one value you hit, and `Highlight.stackIndex` says which. Turn that off to select the whole bar:

```kotlin
barChart.isHighlightFullBarEnabled = true
```

The highlight then comes back with `stackIndex` -1 and the indicator covers the full bar. The default is `false` on `BarChart` and `true` on `CombinedChart`, where a bar usually sits behind other series.

## Replacing the highlighter

The chart turns a touch position into a `Highlight` through its highlighter. It is a functional interface with one method, so a lambda is enough for small changes:

```kotlin
val nearest = ChartHighlighter(chart)

chart.highlighter = IHighlighter { x, y ->
    // return a Highlight, or null for no selection
    nearest.getHighlight(x, y)?.takeIf { it.dataSetIndex == 0 }
}
```

The bundled implementations are `ChartHighlighter` for the charts with axes, `BarHighlighter` and `HorizontalBarHighlighter` for bars, `CombinedHighlighter`, `PieHighlighter` and `RadarHighlighter`. Extend the one that matches your chart when you want to keep most of its behaviour.

> In version 3.x a custom highlighter had to extend `ChartHighlighter`. It only has to implement `IHighlighter` now.
