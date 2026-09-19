# Performance with large data

What a chart spends its time on when it draws, which settings buy the most of it back, and how to measure instead of guess.

A chart with fifty thousand entries is not automatically slow. What decides the frame time is how much of that data is on screen, and how much text and how many shapes the renderer has to put down for it.

## Only the entries in view are drawn

Before a data set is drawn, the renderers work out which entries are visible from the same two properties you can read yourself:

```kotlin
val low = chart.lowestVisibleX
val high = chart.highestVisibleX
```

The entries just outside the screen are included so the line does not stop at the edge, and the renderers walk only that stretch. So the visible range decides the cost of a frame, not the total. Fifty thousand entries with two hundred on screen cost about what two hundred cost. Zooming out is the expensive direction, which is why capping it helps:

```kotlin
chart.setVisibleXRangeMaximum(200f)
chart.moveViewToX(0f)
```

Both are computed from the current x axis range, so they have to run after the data is set. In Compose that means the `update` lambda, not `setup`, which runs once before any data exists. [Modifying the viewport](/mpandroidchart/docs/viewport/) has the rest of the window settings and [Compose](/mpandroidchart/docs/compose/) explains the two lambdas.

> A bar chart works the same way: only the visible entries are fed into its `BarBuffer`. What is still sized from the total entry count is the buffer itself, which costs memory rather than frame time.

## Measured draw times

Measured on an Android emulator, API 36, arm64, on an Apple Silicon Mac, using the example app's performance screens. The whole data set is on screen in every row, and the figure is the chart's own draw rather than the whole frame. Draws per second is 1000 divided by the draw time.

| Entries on screen | Line | Bar |
| --- | --- | --- |
| 1,000 | 0.4 ms | 0.5 ms |
| 10,000 | 1.2 ms | 1.6 ms |
| 50,000 | 8.9 ms | 11.2 ms |
| 100,000 | 18.4 ms | 25.8 ms |
| 500,000 | 133.4 ms | not measured |

Decimation is the interesting one, at 100,000 entries with each pair toggled back to back:

| 100,000 entries | Off | On |
| --- | --- | --- |
| Plain line, one color | 13.4 ms | 24.8 ms |
| Bars | 16.0 ms | 23.4 ms |
| Line with a color per segment | 266.5 ms | 23.3 ms |

All three read about 23 ms with decimation on, because that is the reduction pass itself over 100,000 entries. What differs is the other column: a plain line is one batched call the GPU rasterises cheaply, a bar chart is one call per bar, and a color per segment is one call per segment. Dropping points only pays when the per entry draw call is expensive.

### What to expect on a phone

None of this has been measured on real hardware. The work is mostly CPU, and the emulator runs its guest close to native on an Apple Silicon core while drawing with the host machine's GPU, so expect a recent high-end phone to be roughly 2 to 3 times slower and a mid-range phone 3 to 5 times slower. A 60 Hz frame is 16.67 ms, and a chart realistically gets about half of it.

| For a plain line | Points on screen at 60 fps |
| --- | --- |
| Emulator, measured | about 90,000 |
| High-end phone, estimated | 30,000 to 45,000 |
| Mid-range phone, estimated | 18,000 to 30,000 |

Bars cost about 1.4 times a line at the same count, and circles or value labels reduce all of it sharply.

## Value labels are the most expensive thing on screen

Every drawn label runs your value formatter and then `Canvas.drawText`, far more work per entry than a line segment, so the library has a brake built in. Values are drawn only while

```text
data.entryCount < chart.maxVisibleCount * viewPortHandler.scaleX
```

Three details are easy to get wrong:

- `entryCount` is the sum over every data set of the chart, not the number of entries in view.
- `maxVisibleCount` is 100 by default, so a chart holding 500 entries shows no labels at all until the user has zoomed past 5x.
- `scaleX` is the current horizontal zoom, 1 when fully zoomed out. `HorizontalBarChart` compares against `scaleY` instead.

When you never want labels, say so on the data set rather than relying on the count. Both of these default to true:

```kotlin
set.isDrawValuesEnabled = false
set.isDrawIconsEnabled = false
```

> Pie and radar charts report their own entry count as `maxVisibleCount`, so the check always passes and labels are always drawn. There the data set switches are the only way to turn them off.

## Circles, and why a large radius costs more

A line data set draws a circle at every visible entry unless you say otherwise:

```kotlin
set.isDrawCirclesEnabled = false
```

Circles are stamped from one cached bitmap per circle color, rebuilt only when the colors or the radii change, so steady data costs nothing extra. The radius matters twice over: each bitmap is `circleRadius * 2.1` pixels square, and each stamp blends that many pixels onto the canvas, so doubling it roughly quadruples both. The default is 4 dp, and values below 1 are refused.

## Curve mode and the offscreen bitmap

`LineDataSet.Mode.LINEAR` and `STEPPED` fill one reused float array with the visible segments and hand the whole thing to a single `Canvas.drawLines` call. `CUBIC_BEZIER` and `HORIZONTAL_BEZIER` build a `Path` with one `cubicTo` per segment, which is more work per entry and cannot be batched the same way.

```kotlin
set.mode = LineDataSet.Mode.LINEAR
```

A linear line with more than one color also loses the batching, because each segment is drawn in its own call so it can carry its own color.

Both curve modes and any dashed line draw onto an offscreen bitmap the size of the chart, which the renderer composes onto the canvas at the end of the pass; a plain solid linear line goes straight onto the chart canvas instead. Dashing is the cheapest thing here to give up, with `set.disableDashedLine()`.

## Hardware acceleration

One property switches the view between a hardware and a software layer:

```kotlin
chart.isHardwareAccelerationEnabled = true
```

That is all it does. A fresh chart has no layer at all, so the property reads false even though the window is already hardware accelerated.

Worth keeping apart from that property is whether the drawing reaches the GPU, because a chart drawn to a hardware accelerated window and one drawn to a software `Canvas` behave nothing alike. A window is hardware accelerated by default: the draw is recorded into a display list and the GPU rasterises it, so one batched call is nearly free however many points it covers. On a software canvas, which is what `toBitmap()` and a software layer give you, the CPU fills every pixel itself. That is exactly why reducing the point count can fail to help.

A hardware layer earns its keep only for a chart whose content does not change while the chart itself moves, because the view is rendered into a texture once and reused while you scroll or fade it. A chart that invalidates on every frame redraws into that texture anyway and only pays for it.

## Clipping

| Property | Default | What it does |
| --- | --- | --- |
| `isClipDataToContentEnabled` | `true` | Clips the data, the grid lines and the highlights to the content rectangle |
| `isClipValuesToContentEnabled` | `false` | Clips the value labels as well |

Turn the first off when a thick line or a large shape near the edge is being cut in half. The second costs one canvas save and restore per frame, which is nothing next to drawing the labels themselves, so turn it on for looks rather than for speed.

## Thin the data before you draw it

When a series has more points than the screen has pixels, most of them cannot be seen. Every chart with an x axis can leave those out while it draws, and does so by default:

```kotlin
chart.isDecimationEnabled = false
```

While it is on, the renderers keep the first, the lowest, the highest and the last entry of each pixel column and skip the rest, so peaks and troughs survive and the shape stays the same. On a line chart it also leaves out the circles another circle would have covered. Your data is untouched; this happens on the way to the canvas.

Whether it is worth its own cost depends entirely on what one entry costs to draw, and the numbers above say it plainly. A line with a color per segment goes from 266.5 ms to 23.3 ms, because every segment there is a draw call of its own. A plain line goes the other way, from 13.4 ms to 24.8 ms, and so does a bar chart, from 16.0 ms to 23.4 ms, because the reduction pass costs more than the drawing it saves. Leave it on for a line with more than one color, and turn it off for a plain line or a bar chart.

`Approximator` is the other way to thin a series, once while you build the data rather than on every draw. It takes a flat `FloatArray` of `x0, y0, x1, y1, ...` and a tolerance, reduces it with the Douglas-Peucker algorithm, and returns the same layout:

```kotlin
val reduced = Approximator().reduceWithDouglasPeucker(points, 2f)
```

The tolerance is in the same unit as the points you pass in. Nothing in the library calls it for you, so run it on a background thread while the data is being built.

## Do not allocate while drawing

The renderers run inside `onDraw`, and the library goes out of its way not to allocate there: the buffers are refilled in place, and `MPPointF`, `MPPointD` and `FSize` come from shared `ObjectPool` instances.

Those buffers are sized from the total entry count rather than the visible one, so fifty thousand points on a single colored line reserve about 1.6 MB for as long as the set is assigned. That is the real cost of a large total count: memory, not frame time.

Your own code is the other half:

- **Formatters.** `getFormattedValue` is called for every drawn label on every frame. Build the `NumberFormat` or `SimpleDateFormat` once as a property of the formatter, never inside the function. [Formatters](/mpandroidchart/docs/formatters/) shows the shape.
- **Markers.** `refreshContent` runs before every marker draw, so for a marker that follows a drag it runs per frame. Keep the views and change only their content. [Markers](/mpandroidchart/docs/markers/) has the details.

Building the data is plain object work with no view involved, so do it on a background thread. Only assigning `chart.data` and calling `chart.notifyDataSetChanged()` have to happen on the main thread.

## Measure, do not guess

Every chart can write its internals to logcat under the tag `MPAndroidChart`:

```kotlin
chart.isLogEnabled = true
```

On the axis charts the useful line is printed at the end of each draw:

```text
Drawtime: 6 ms, average: 7 ms, cycles: 42
```

`chart.resetTracking()` zeroes the total and the cycle count, which is what you call right before the interaction you actually want to time.

The example app has two screens built for exactly this, Line chart performance and Bar chart performance. Each shows what the chart's own draw cost, the worst frame of the last second, and how many entries are on screen, with switches for the entry count, decimation, value labels and the label limit, plus the line shape, circles, fill and a color per segment on one and stacking, rounded corners and bar shadows on the other. The tables above come from them.

Two caveats. Logging itself costs time on every draw, so the numbers are a comparison between settings rather than an absolute. And the draw time does not include `notifyDataSetChanged`, which is where the axis recalculation happens. For anything beyond a rough comparison, record a trace with the Android Studio profiler.

## The settings that pay off most

Roughly in order of what they buy, with the measured figures where there are any. All of them are emulator numbers.

| Setting | What it buys |
| --- | --- |
| `chart.setVisibleXRangeMaximum(n)` | The biggest lever there is. Cost follows the points on screen, not the points you hold: 10,000 on screen draws in 1.2 ms where 100,000 takes 18.4 ms. A million point set scrolls perfectly well at a sensible zoom. |
| A single `color` on a line set | 18.4 ms against 266.5 ms at 100,000 entries. One color is one batched draw call; a color per segment is a call per segment. |
| `set.isDrawValuesEnabled = false` | Removes the text pass. `chart.maxVisibleCount` decides the zoom at which labels start appearing, so raising it costs you the same way. |
| `set.isDrawCirclesEnabled = false` | Removes one bitmap stamp per visible point. |
| `chart.isDecimationEnabled = false` | 13.4 ms against 24.8 ms on a plain line, 16.0 against 23.4 on bars. Leave it on for a line with a color per segment, where it is 23.3 against 266.5. |
| `set.mode = LineDataSet.Mode.LINEAR` | One batched call instead of a path with a segment per entry. |
| `set.disableDashedLine()` | Takes the line off the offscreen bitmap pass. |
| Leaving `isDrawFilledEnabled` off | A filled line rebuilds a path in chunks of 128 entries every frame. |
| `chart.isDrawBarShadowEnabled = false` | One fewer rectangle per bar. |
| Batching appends | A live feed that calls `notifyDataSetChanged()` per entry pays about 0.4 ms each time. Append what arrived, then notify once. |

None of these is worth applying blindly. Turn on `isLogEnabled`, note the average, change one thing, and compare.

## Where to go next

- [Dynamic and realtime data](/mpandroidchart/docs/dynamic-data/) for adding and dropping entries while the chart is on screen.
- [Modifying the viewport](/mpandroidchart/docs/viewport/) for the zoom and scroll limits that decide the visible range.
- [Custom renderers](/mpandroidchart/docs/custom-renderers/) if you want to change what a draw pass does.
- [Miscellaneous](/mpandroidchart/docs/miscellaneous/) for the object pools and the logging switch.
