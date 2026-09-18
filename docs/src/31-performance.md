# Performance with large data

What a chart actually spends its time on when it draws, which settings buy the most of it back, and how to measure instead of guess.

A chart with fifty thousand entries is not automatically slow. What decides the frame time is how much of that data is on screen and how much text and how many shapes the renderer has to put down for it. This chapter goes through those costs in the order they matter.

Two other chapters touch the same ground briefly: [Dynamic and realtime data](/mpandroidchart/docs/dynamic-data/) for a feed that never stops, and [Miscellaneous](/mpandroidchart/docs/miscellaneous/) for a short checklist. This is the long version.

## Only the entries in view are drawn

The renderers of the axis charts share a helper called `XBounds`. Before a data set is drawn, the renderer hands it the chart and the set, and it works out which entries are visible from the same two properties you can read yourself:

```kotlin
val low = chart.lowestVisibleX
val high = chart.highestVisibleX
```

It looks up the entry at `low` rounding down and the entry at `high` rounding up, so the two entries just outside the screen are included and the line does not stop at the edge. It stores their indices as `min` and `max`, and the distance between them multiplied by the x animation phase as `range`. Every loop in `LineChartRenderer` then runs from `min` to `min + range` instead of over the whole set.

So on a line chart the visible range decides the cost of a frame, not the total number of entries. Fifty thousand entries with two hundred of them on screen cost about what two hundred entries cost. Zooming out is the expensive direction, which is why capping it helps:

```kotlin
chart.setVisibleXRangeMaximum(200f)
chart.moveViewToX(0f)
```

Both are computed from the current x axis range, so they have to run after the data is set. In Compose that means the `update` lambda, not `setup`, because `setup` runs once before any data exists:

```kotlin
LineChart(
    data = lineData,
    modifier = Modifier.fillMaxWidth().height(260.dp),
    setup = {
        maxVisibleCount = 40
        isDrawGridBackgroundEnabled = false
    },
    update = {
        setVisibleXRangeMaximum(200f)
    },
)
```

[Modifying the viewport](/mpandroidchart/docs/viewport/) has the rest of the window settings, and [Compose](/mpandroidchart/docs/compose/) explains the two lambdas.

> Bars are the exception. `BarChartRenderer` feeds every entry of a data set into its `BarBuffer` and converts the whole buffer to pixels in one pass, then skips the bars outside the content rectangle while drawing. A bar chart therefore pays for its total entry count on every frame, and limiting the visible range helps it less than it helps a line.

## Value labels are the most expensive thing on screen

Every drawn label runs your value formatter and then `Canvas.drawText`. That is far more work per entry than a line segment, so the library has a brake built in. Before any value is drawn, the renderer checks whether

```text
data.entryCount < chart.maxVisibleCount * viewPortHandler.scaleX
```

and returns immediately when it does not hold. Three details are easy to get wrong:

- `entryCount` is the sum over every data set of the chart, not the number of entries in view.
- `maxVisibleCount` is 100 by default, so a chart holding 500 entries shows no labels at all until the user has zoomed past 5x.
- `scaleX` is the current horizontal zoom, 1 when fully zoomed out. `HorizontalBarChart` compares against `scaleY` instead, because its entries run down the screen.

Lower `maxVisibleCount` to make labels disappear sooner, raise it to keep them longer:

```kotlin
chart.maxVisibleCount = 40
```

When you never want labels, say so on the data set rather than relying on the count. Both of these default to true:

```kotlin
set.isDrawValuesEnabled = false
set.isDrawIconsEnabled = false
```

> Pie and radar charts return the entry count of their own data as `maxVisibleCount`, so the check always passes and labels are always drawn. On those charts the data set switches are the only way to turn them off.

## Circles, and why a large radius costs more

A line data set draws a circle at every visible entry unless you say otherwise:

```kotlin
set.isDrawCirclesEnabled = false
```

Circles are not drawn with `drawCircle` per point. `LineChartRenderer` keeps one cached bitmap per circle color of the data set and stamps that bitmap at each position. The cache is rebuilt only when the circle colors, the radius, the hole radius or the hole color change, so a set with one circle color holds exactly one bitmap and steady data costs nothing.

The radius still matters, twice over. Each cached bitmap is `circleRadius * 2.1` pixels square, and each stamp blends that many pixels onto the canvas. Doubling `circleRadius` roughly quadruples both. The default is 4 dp, and values below 1 are refused with a message in logcat.

Turning the hole off with `set.isDrawCircleHoleEnabled = false` saves a second draw inside each cached bitmap, but that happens once per cache fill, not per frame, so it changes almost nothing.

## Curve mode and the offscreen bitmap

`LineDataSet.Mode.LINEAR` and `STEPPED` fill one reused float array with the visible segments and hand the whole thing to a single `Canvas.drawLines` call. `CUBIC_BEZIER` and `HORIZONTAL_BEZIER` build a `Path` with one `cubicTo` per segment, transform it and draw it, which is more work per entry and cannot be batched the same way.

```kotlin
set.mode = LineDataSet.Mode.LINEAR
```

A linear line with more than one color loses the batching, because each segment is drawn in its own call so it can have its own color. Keep `color` as a single color when you want the cheap path.

The two curve modes and any dashed line draw onto an offscreen bitmap the size of the chart, which the renderer composes onto the canvas at the end of the pass. A plain solid linear line goes straight onto the chart canvas instead. The bitmap is `ARGB_8888` and is recreated whenever the chart changes size; `bitmapConfig` on `LineChartRenderer` changes the format and releases the current bitmap so the next draw makes a new one.

Dashing is the cheapest thing on this list to give up. `set.disableDashedLine()` removes the path effect and takes the line off the bitmap pass.

## Hardware acceleration

One property switches the view between a hardware and a software layer:

```kotlin
chart.isHardwareAccelerationEnabled = true
```

That is all it does. It reads `layerType == LAYER_TYPE_HARDWARE` and writes `setLayerType(LAYER_TYPE_HARDWARE)` or `setLayerType(LAYER_TYPE_SOFTWARE)`, and nothing else in the library sets a layer. A fresh chart has no layer at all, so the property reads false even though the window is already hardware accelerated.

The one case where it earns its keep is a chart whose content does not change while the chart itself moves: a hardware layer renders the view into a texture once and reuses it while you scroll, fade or translate it. A chart that invalidates on every frame, which is what a live feed or a running animation does, redraws into that texture anyway and only pays for it. Setting it to false is the escape hatch for the rare case where a large translucent data set draws wrong on the GPU. Measure both on a real device before you keep either.

## Clipping

Two switches control what gets cut off at the edge of the content area.

| Property | Default | What it does |
| --- | --- | --- |
| `isClipDataToContentEnabled` | `true` | Clips the data, the grid lines and the highlights to the content rectangle |
| `isClipValuesToContentEnabled` | `false` | Clips the value labels as well |

Clipping data is on because it is what you want almost always. Turn it off when a thick line or a large shape near the edge is being cut in half:

```kotlin
chart.isClipDataToContentEnabled = false
```

Clipping values costs one extra canvas save, clip and restore per frame, which is nothing next to drawing the labels themselves. Turn it on for looks rather than for speed, because with the default the label on the first or last entry can bleed over the axis.

## Thin the data before you draw it

When a series has more points than the screen has pixels, most of them cannot be seen. `Approximator` reduces a polyline with the Douglas-Peucker algorithm: a point closer than a tolerance to the straight line between its neighbours is dropped, and the first and last point are always kept.

The function takes a flat `FloatArray` of `x0, y0, x1, y1, ...` and a tolerance, and returns a new `FloatArray` in the same layout:

```kotlin
val points = FloatArray(entries.size * 2)
for (i in entries.indices) {
    points[i * 2] = entries[i].x
    points[i * 2 + 1] = entries[i].y
}

val reduced = Approximator().reduceWithDouglasPeucker(points, 2f)

val thinned = ArrayList<Entry<Any?>>(reduced.size / 2)
for (i in reduced.indices step 2) {
    thinned.add(Entry(reduced[i], reduced[i + 1]))
}

chart.data = LineData(LineDataSet(thinned, "Thinned"))
```

The tolerance is in the same unit as the points you pass in, so feed it value space coordinates and think in values, or pixels and think in pixels. Fewer than two points throws `ArrayIndexOutOfBoundsException`.

> Nothing in the library calls `Approximator` for you. It is a tool you reach for yourself, ideally once on a background thread while the data is being built, not on every frame.

## Do not allocate while drawing

The renderers run inside `onDraw`, and the library goes out of its way not to allocate there. `BarBuffer` and its horizontal variant keep one float array per data set and refill it in place. `MPPointF`, `MPPointD` and `FSize` come from shared `ObjectPool` instances instead of being created per call. [Miscellaneous](/mpandroidchart/docs/miscellaneous/) covers the pools and how to use one for your own type.

Those arrays are sized from the total entry count, not the visible one, and they are grown once rather than reallocated per frame. A bar buffer holds four floats per bar, and the line renderer's segment buffer grows to eight floats per entry, so fifty thousand points on a single colored line reserve about 1.6 MB for as long as the set is assigned. That is the real cost of a large total count on a line chart: memory, not frame time.

None of that helps if your own code allocates on the way past. Two places are worth checking:

- **Formatters.** `getFormattedValue` is called for every drawn label on every frame. Build the `NumberFormat` or `SimpleDateFormat` once as a property of the formatter, never inside the function, and avoid string concatenation where a cached array of labels would do. [Formatters](/mpandroidchart/docs/formatters/) shows the shape.
- **Markers.** `refreshContent` runs before every marker draw, so for a marker that follows a drag it runs per frame. Keep the views and the text buffers, change only their content. [Markers](/mpandroidchart/docs/markers/) has the details.

Building the data itself is plain object work with no view involved, so do it on a background thread. Only assigning `chart.data` and calling `chart.notifyDataSetChanged()` have to happen on the main thread.

## Measure, do not guess

Every chart can write its internals to logcat under the tag `MPAndroidChart`:

```kotlin
chart.isLogEnabled = true
```

On the axis charts the useful line is the one printed at the end of each draw:

```text
Drawtime: 6 ms, average: 7 ms, cycles: 42
```

`drawtime` is the current frame, `average` is the running mean since the chart was created, and `cycles` counts the draws. `chart.resetTracking()` zeroes the total and the cycle count, which is what you call right before the interaction you actually want to time. The example app's PerformanceLineChart does exactly that every time the seek bar changes the entry count.

Two caveats. Logging itself costs time on every draw, so the numbers are a comparison between settings, not an absolute. And the draw time does not include `notifyDataSetChanged`, which is where axis recalculation and offset work happens. For anything beyond a rough comparison, record a trace with the Android Studio profiler and look at where the time actually goes.

## The settings that pay off most

| Setting | What it buys |
| --- | --- |
| `set.isDrawValuesEnabled = false` | Removes the text pass, usually the largest single cost |
| `set.isDrawCirclesEnabled = false` | Removes one bitmap stamp per visible point |
| `set.mode = LineDataSet.Mode.LINEAR` | One batched draw call instead of a path with a segment per entry |
| `chart.setVisibleXRangeMaximum(n)` | Caps how many entries can be in view at once, on line charts |
| `chart.maxVisibleCount = n` | Moves the zoom level at which labels start being drawn |
| `set.disableDashedLine()` | Takes the line off the offscreen bitmap pass |
| Leaving `isDrawFilledEnabled` off | A filled line rebuilds a path in chunks of 128 entries every frame |
| Cap the entry count | Keeps memory and the axis recalculation in `notifyDataSetChanged` bounded |

None of these is worth applying blindly. Turn on `isLogEnabled`, note the average, change one thing, and compare.

## Where to go next

- [Dynamic and realtime data](/mpandroidchart/docs/dynamic-data/) for adding and dropping entries while the chart is on screen.
- [Modifying the viewport](/mpandroidchart/docs/viewport/) for the zoom and scroll limits that decide the visible range.
- [Custom renderers](/mpandroidchart/docs/custom-renderers/) if you want to change what a draw pass does.
- [Miscellaneous](/mpandroidchart/docs/miscellaneous/) for the object pools and the logging switch.
