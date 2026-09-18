# Troubleshooting

Concrete symptoms you may hit with a chart, what causes each one in the library, and what to change.

## Nothing is drawn

### The chart shows "No chart data available."

That text only appears while `chart.data` is null. `Chart.onDraw` draws `noDataText` at the center of the view and returns before anything else. So the chart never received data, or something called `chart.clear()`, which sets the data to null, drops the highlight and redraws. `noDataText`, `noDataTextColor`, `noDataTextTypeface` and `noDataTextAlignment` style that message, and an empty string draws nothing.

### The chart is blank but the no data text is gone

You assigned a data object that holds no entries, or sets that are empty. "Data is set" and "data has entries" are two different things, and only the first switches the message off. `chart.isEmpty` covers both.

An empty set is worse than no data. `DataSet.calcMinMax` leaves `yMin` at `Float.MAX_VALUE` and `yMax` at `-Float.MAX_VALUE` when there are no entries, so the axis range computed from it is infinite, `AxisRenderer.computeAxisValues` bails out with zero label entries, and you get a view with no labels, no grid and no data. Call `chart.clear()` instead and let the no data text do its job.

### The chart is a thin strip

`Chart.onMeasure` resolves to 50 dp when the parent does not impose a height, so `android:layout_height="wrap_content"` gives you a 50 dp chart. Give the chart a real height, or a weight inside a `LinearLayout`. In Compose the same applies to a `Modifier` without a height:

```kotlin
LineChart(
    data = lineData,
    modifier = Modifier.fillMaxWidth().height(220.dp),
)
```

### One data set is missing while the others draw

`isVisible` makes the renderers skip the set entirely. When only parts are missing, look at `isDrawValuesEnabled` for the value labels and, on a line set, `isDrawCirclesEnabled` for the points. All three default to true.

### Viewport calls seem to be ignored

`moveViewToX`, `centerViewTo` and the animated variants go through `addViewportJob`, which posts the job right away only when `viewPortHandler.hasChartDimens()` is true. Before the first layout they are parked in `chart.jobs` and run in `onSizeChanged`, so they do take effect, one frame later.

`setVisibleXRangeMaximum` and `setVisibleXRangeMinimum` are different: they divide `xAxis.axisRange` by your span immediately. Call them after the data is set, or the range is still the default and the limit is wrong.

## The values look wrong or jump around

### Points connect in the wrong order

A `DataSet` requires its entries sorted by x ascending. `getEntryIndex(xValue, closestToY, rounding)` is a binary search, and every x lookup, every highlight and every visible-range calculation goes through it. Unsorted entries do not throw; they return a neighbour that happens to be nearby, so the line zig-zags and taps land on the wrong point.

Sort before building the set, and insert in order afterwards:

```kotlin
val entries = readEntries().sortedWith(EntryXComparator())
val set = LineDataSet(entries, "Revenue")

set.addEntryOrdered(Entry(x, y))
```

`addEntryOrdered` appends when the new x is not smaller than the last entry's x, and otherwise inserts before the first entry with a larger x. `addEntry` always appends without checking, which is what breaks the order.

> A `DataSet` keeps an `ArrayList` you pass by reference and copies any other list. Sorting the `ArrayList` you handed over therefore also sorts the data set.

### Value labels disappear as the data grows

`DataRenderer.isDrawingValuesAllowed` draws labels only while `data.entryCount` is below `chart.maxVisibleCount` times the current x zoom. The default `maxVisibleCount` is 100, so labels stop at 100 entries and come back as you zoom in. Raise it if you really want them.

## Changes to the data do not show

### One call is enough

After changing entries or sets in place:

```kotlin
chart.notifyDataSetChanged()
```

That recomputes the data ranges, rebuilds the renderer buffers, recomputes both y axes and the x axis, rebuilds the legend, recalculates the offsets and redraws. It calls `data.notifyDataChanged()` for you, so there is nothing else to call and no separate `invalidate()`.

The one case that needs more is changing a set's `entries` list in place rather than through `addEntry` or `removeEntry`. `ChartData.calcMinMax` reads each set's cached range instead of rescanning its entries, so the set has to be told first:

```kotlin
set.entries.add(Entry(x, y))
set.notifyDataSetChanged()
chart.notifyDataSetChanged()
```

Assigning `set.entries = newEntries` does not need that, because the setter recomputes the range.

### In Compose the chart ignores the new data

`ChartView` applies the data with `if (chart.data !== data) chart.data = data`. That is an identity check. Recomposing with the **same** `LineData` instance, however much you changed inside it, assigns nothing and redraws nothing.

Either hand the composable a new instance, or keep the instance and say so:

```kotlin
state.notifyDataChanged()
```

That calls `notifyDataSetChanged()` on the attached chart and refreshes the state properties. See [Jetpack Compose](/mpandroidchart/docs/compose/).

## The x axis shows 0, 1, 2 instead of my labels

x values are values, not indices. An entry at `Entry(0f, 42f)` sits at x = 0, and the axis prints that number unless a formatter turns it into something else.

```kotlin
chart.xAxis.apply {
    valueFormatter = IndexAxisValueFormatter(months)
    granularity = 1f
    labelCount = months.size
}
```

### Labels disappear or land on the wrong tick

`IndexAxisValueFormatter.getFormattedValue` rounds the value to an index and then rejects it when `value.roundToInt()` differs from `value.toInt()`. In practice: a fraction below 0.5 gives you the label of the truncated index, and a fraction of 0.5 or above gives an empty string.

Without granularity the axis is free to pick an interval smaller than 1 as you zoom in, so label values become 2.4 and 2.6. The first prints "Mar" at a tick that is not March, the second prints nothing. Setting `granularity = 1f` keeps the interval at 1 or above and also sets `isGranularityEnabled` to true, so label values stay whole. More in [the x axis](/mpandroidchart/docs/xaxis/).

## Labels and data are cut off at the edges

### The first and last label overlap the view edge

The x axis renderer skips labels whose pixel position falls outside the content area, and draws the rest centered on their tick, so half of the outermost label hangs over the edge.

```kotlin
chart.xAxis.isAvoidFirstLastClippingEnabled = true
```

That shifts the first label right by half its width, and the last label left by half its width, but only when the last label is wider than twice the right offset and would really spill past the view. It is off by default.

### The line or the outer bars are clipped

Extra space around the content area is the direct fix. `chart.setExtraOffsets(6f, 8f, 6f, 4f)` takes dp and applies on the next offset calculation.

Padding in value space is the other option. `axisMinimum` and `axisMaximum` fix the range; `spaceMin` and `spaceMax` are subtracted from and added to the computed range instead, so they survive new data. `BarChart`, `ScatterChart` and `CandleStickChart` already set both to 0.5 on the x axis, which is why bar charts leave half a slot at each side and line charts do not.

### There is a "Description Label" in the corner

`Description.text` defaults to that string and the component is enabled, so every chart draws it at the bottom right until you turn it off with `chart.description.isEnabled = false`. See [the description](/mpandroidchart/docs/description/).

## The chart is drawn under the status bar or the action bar

This is not the library. From `targetSdk` 35 the window is edge to edge and your app receives the insets, so a chart that fills the screen slides under the system bars.

The example app pads the root view of every activity. `DemoBase.setContentView` calls one extension on the view it just set, and `MainActivity` does the same after inflating its binding:

```kotlin
fun View.padForWindowInsets() {
    ViewCompat.setOnApplyWindowInsetsListener(this) { view, insets ->
        val bars = insets.getInsets(
            WindowInsetsCompat.Type.systemBars() or
                WindowInsetsCompat.Type.displayCutout(),
        )
        view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
        WindowInsetsCompat.CONSUMED
    }
}
```

Returning `CONSUMED` stops the insets from being dispatched again to children, so nothing is padded twice. In Compose, put the same padding on the container with `Modifier.windowInsetsPadding(WindowInsets.systemBars)` rather than on the chart.

## Gestures do not work

### Nothing reacts to touch at all

`BarLineChartBase.onTouchEvent` returns false when `chartTouchListener` is not built yet, when `data` is null, or when `isTouchEnabled` is false. No data means no gestures at all, which is easy to miss while you are still loading.

If taps still highlight but pan and zoom do nothing, the touch listener is bailing out: it stops handling the event when `isDragEnabled` is false **and** both `isScaleXEnabled` and `isScaleYEnabled` are false. The tap detector runs before that check, which is why the highlight survives.

Pie and radar charts only check `isTouchEnabled`, and their rotation has its own switch, `isRotationEnabled`.

### The chart fights a scrolling parent

The chart already calls `disableScroll()` when a drag or a zoom begins and `enableScroll()` on `ACTION_UP`, which is `requestDisallowInterceptTouchEvent` on the parent. When your own touch handling gets in the way, call the same pair yourself. A vertical parent and a horizontal chart usually agree once you turn the conflicting axis off with `chart.isDragYEnabled = false`. [Interaction](/mpandroidchart/docs/interaction/) and [charts in lists](/mpandroidchart/docs/lists-and-scrolling/) cover the rest.

### A small drag does nothing

A touch becomes a drag only once the finger has moved further than `dragTriggerDist`, which the charts create their listener with at 3 dp. Raise it when a chart inside a scrolling parent steals taps:

```kotlin
val listener = chart.chartTouchListener as BarLineChartTouchListener
listener.dragTriggerDist = 12f
```

## Highlighting selects the wrong thing, or nothing

### Nothing is selected

Four things have to line up. `chart.isHighlightPerTapEnabled` must be true, the data set must have `isHighlightEnabled` true, the touch must be within `chart.maxHighlightDistance` of a value, and `data.getEntryForHighlight` has to find the entry. The distance is measured in dp and defaults to 500, which is generous; lower it when a tap in empty space should select nothing.

### A tap selects a neighbour

The highlighter converts the touch to an x value, collects the closest entry in every set, prefers the y axis whose candidates sit nearer to the touch, and then takes the smallest pixel distance. On a bar chart only the horizontal distance counts, so a tap anywhere above or below a bar selects it.

Unsorted entries break this, because the closest-entry step is the same binary search as above.

### A drag pans instead of moving the highlight

`isHighlightPerDragEnabled` is true by default, but the touch listener only takes that branch when the chart cannot pan at all: `chart.isFullyZoomedOut` must be true and `hasNoDragOffset` must be true. Calling `setVisibleXRangeMaximum` sets a minimum x scale above 1, and `isFullyZoomedOutX` is false whenever the minimum scale is above 1. So a chart with a limited visible range always pans and never highlights by drag.

### A stacked bar selects the wrong part

`BarHighlighter` looks at the touched y value, finds the stack range that contains it and stores that position in `Highlight.stackIndex`. To select the whole bar instead, set `chart.isHighlightFullBarEnabled = true`; `getHighlightByTouchPoint` then rebuilds the highlight with a stack index of -1. It defaults to false on `BarChart` and true on `CombinedChart`.

### A combined chart highlights nothing from code

`CombinedData.getEntryForHighlight` first looks up the child data object at `Highlight.dataIndex`, and returns null when that index is outside `allData`. `dataIndex` defaults to -1, so the usual call selects nothing:

```kotlin
chart.highlightValue(x = 3f, dataSetIndex = 0, dataIndex = 1)
```

`allData` is ordered line, bar, scatter, candle, bubble, skipping the kinds you did not set, and that position is the index you pass.

## Markers do not appear

`Chart.drawMarkers` returns early unless all three hold: `chart.marker` is not null, `chart.isDrawMarkersEnabled` is true, and `valuesToHighlight()` is true. Per highlight it also skips entries the running `animateX` has not reached yet, and any position outside the content area, so a marker for a value scrolled out of view is not drawn.

A `MarkerView` has an offset of (0, 0), which puts its top left corner on the value, so it looks missing under your finger. Shift it with `setOffset(-width / 2f, -height.toFloat())` to sit above the point. If you override `refreshContent`, call `super.refreshContent(e, highlight)` so the view is measured again.

A Compose marker appears one frame after the highlight. `ComposeMarker.draw` skips the frame while the content for a newly highlighted entry has not composed yet; the `SideEffect` in its `ComposeView` then invalidates the chart and the next frame draws it. More in [markers](/mpandroidchart/docs/markers/).

## The release build differs from the debug build

Start by ruling R8 out: build the release variant once with `isMinifyEnabled = false`. If the problem stays, it is not minification. The library needs no keep rules of its own. Version 4 drives every animation through a `ValueAnimator` and an update listener, so no member is ever looked up by name, and the chart views carry `@Keep` so a chart named in a layout file survives. The causes that are left are in your code: a marker or chart subclass that appears only in XML, a drawable resolved by name that resource shrinking removed, or another library reflecting on your entry payload. [R8 and ProGuard](/mpandroidchart/docs/proguard/) works through each of them.

## Exceptions the library throws

They are few, and each points at one mistake:

- `IllegalStateException` from `groupBars`: no data on the chart yet, or fewer than two bar data sets to group.
- `IllegalStateException` from `ChartState.attach`: one `ChartState` given to a second chart. Call `rememberChartState()` once per chart.
- `IllegalStateException` from `color` or `getColor`: the set's `colors` list is empty.
- `IllegalArgumentException` from `ObjectPool.recycle`: the same pooled instance recycled twice.
- `ParcelFormatException` from `Entry.writeToParcel`: the entry payload is not `Parcelable`.

[Miscellaneous](/mpandroidchart/docs/miscellaneous/) has the full table with the throwing class for each.

## Getting a useful report out of the library

Every chart can narrate what it does under the logcat tag `MPAndroidChart`:

```kotlin
chart.isLogEnabled = true
```

It reports `Chart.init()`, `Data is set.`, `OnSizeChanged()` with the dimensions it accepted or refused, `Preparing...` or `Preparing... DATA NOT SET.` on each `notifyDataSetChanged`, the x axis range each time the value to pixel matrix is prepared, the computed offsets with the resulting content rectangle, and the highlight on every selection. That sequence answers most of the symptoms above: if you never see `Setting chart dimens`, the chart has no size; if you see `DATA NOT SET`, the data never arrived.

Line, bar, scatter, candle, bubble and combined charts add a timing line per frame:

```text
Drawtime: 6 ms, average: 7 ms, cycles: 42
```

`chart.resetTracking()` zeroes the total and the cycle count, which is what you want right before measuring one specific interaction rather than the whole session. Logging costs time on every draw, so keep it off in release builds. [Performance](/mpandroidchart/docs/performance/) uses these numbers.
