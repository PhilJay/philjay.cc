# Animations

Building the chart up with animateX, animateY and animateXY, knowing when an animation ends, moving values to new data with animateValue and animateDataChange, the easing curves, spinning round charts, and animating the viewport.

## Animate the entries

Three functions exist on every chart type. Each one returns immediately and redraws the chart on every frame, so no extra `invalidate()` is needed.

```kotlin
chart.animateX(1500)          // build up from left to right
chart.animateY(1500)          // grow from the bottom up
chart.animateXY(1500, 1500)   // both at once
```

| Function | Effect |
| --- | --- |
| `animateX(durationMillis, easing, onEnd)` | Reveals the entries one after the other along the x axis |
| `animateY(durationMillis, easing, onEnd)` | Scales the values up from zero |
| `animateXY(durationMillisX, durationMillisY, easingX, easingY, onEnd)` | Runs both, each with its own duration and curve |

Durations are milliseconds, and a negative one counts as 0. Call the animation after the data is set, usually right after `chart.data = ...`.

The x and y animations run side by side, but only one of each at a time. Starting `animateX` while an x animation runs cancels the running one and starts again from the beginning, so a button that is tapped twice does not leave two animations fighting over the chart. `animateXY` cancels both.

On a pie or radar chart the same functions work: the x animation sweeps the slices into place and the y animation grows each slice or the web polygon.

## Know when an animation ends

`animateX`, `animateY`, `animateXY`, `spin`, `animateValue` and `animateDataChange` take an optional `onEnd` lambda as their last parameter, so it fits after the call:

```kotlin
chart.animateX(800) {
    chart.highlightValue(lastX, 0)
}

chart.animateY(600, Easing.EaseOutCubic) { replayButton.isEnabled = true }
```

`onEnd` runs once, on the main thread, however the animation ends: when it finishes, when `stopAnimations()` ends it, when the chart leaves the window, and when a new animation of the same kind cancels it. For `animateXY` it runs after both the x and the y part have ended.

Two members tell you about and control what is running:

| Member | What it does |
| --- | --- |
| `chart.isAnimating` | True while any animation runs: x, y, a spin, a value or a data change |
| `chart.stopAnimations()` | Ends every one of these animations at once at its final state and runs each `onEnd` |

```kotlin
override fun onPause() {
    super.onPause()
    chart.stopAnimations()   // show the finished chart, not a half drawn one
}
```

A chart that is removed from the window, for example a row scrolling out of a list or a closed screen, ends its animations the same way. A running animation never keeps a removed chart alive.

## Animate one value

`animateValue` moves the y value of a single entry to a new value. The axis ranges follow on every frame, so a bar that grows past the top pushes the axis up as it goes.

```kotlin
chart.onValueSelected { entry, _ ->
    chart.animateValue(entry, toY = entry.y + 10f, durationMillis = 600, easing = Easing.EaseInOutCubic)
}
```

The entry itself ends with `y` set to the new value, so there is nothing to rebuild afterwards. It works for line, bar, scatter, bubble, pie and radar entries. Starting a second animation of the same entry continues from where the first one is, and assigning `chart.data` ends it with the entry at its target.

`animateValue` throws `IllegalArgumentException` for an entry that is not part of the chart data, for a stacked `BarEntry` and for a `CandleEntry`. Animate those with `animateDataChange`.

## Animate a data change

`animateDataChange` sets new data and moves every entry from the value it replaces to its own value:

```kotlin
fun showTotals(totals: List<Float>) {
    val set = BarDataSet(totals.mapIndexed { i, total -> BarEntry(i.toFloat(), total) }, "Sales")
    chart.animateDataChange(BarData(set), durationMillis = 500, easing = Easing.EaseInOutCubic)
}
```

It is the animated form of `chart.data = newData`. Pass a new data object each time, not the current one changed in place.

- Entries are paired by data set index and entry index, not by x value. The first entry of the first set moves from the old first entry of the first set, and so on.
- Entries past the old end grow from 0. Entries past the new end are gone at once.
- Only values move. An entry whose x changed jumps to its new x.
- A stacked bar moves each stack value, a candle its open, high, low and close, a bubble its y and its size, and a pie slice its value.
- The axis ranges follow on every frame, and a highlight stays on its x value.

Some changes cannot be animated, and then the new data is set at once, exactly like `chart.data = newData`, and `onEnd` runs right away: when the chart had no data yet, when you pass the data that is already on the chart, and when the shape differs, meaning another data class, another number of data sets, or another data set class at the same index.

A new `animateDataChange` ends the running one first and starts from the values on screen at that moment, so rapid updates stay smooth. `animateValue` on an entry that a data change is still moving takes over just that entry. When the animation ends in any way, including `stopAnimations()` and assigning `chart.data`, the new entries hold exactly their own values.

The example app has an "Animated data changes" screen with buttons that randomize, add and remove bars, and a tap that animates one bar. Its "All animations" screen runs every animation on a line, bar or donut chart, with any easing curve and duration, and shows `isAnimating`, `stopAnimations()` and every `onEnd` call live.

## Easing

Every animation function on this page takes an optional easing curve. The default is `Easing.Linear`, except `animateXY`, whose `easingY` follows `easingX`.

```kotlin
chart.animateY(1400, Easing.EaseOutBack)
chart.animateXY(1400, 1400, Easing.EaseInOutQuad)
chart.animateXY(1200, 800, easingX = Easing.EaseOutCubic, easingY = Easing.EaseInQuad)
```

The `Easing` object holds 28 curves. `EaseIn` starts slow, `EaseOut` ends slow, `EaseInOut` does both.

| Family | Curves |
| --- | --- |
| None | `Linear` |
| Polynomial | `EaseInQuad`, `EaseOutQuad`, `EaseInOutQuad`, `EaseInCubic`, `EaseOutCubic`, `EaseInOutCubic`, `EaseInQuart`, `EaseOutQuart`, `EaseInOutQuart` |
| Trigonometric | `EaseInSine`, `EaseOutSine`, `EaseInOutSine` |
| Exponential | `EaseInExpo`, `EaseOutExpo`, `EaseInOutExpo` |
| Circular | `EaseInCirc`, `EaseOutCirc`, `EaseInOutCirc` |
| Overshooting | `EaseInBack`, `EaseOutBack`, `EaseInOutBack`, `EaseInElastic`, `EaseOutElastic`, `EaseInOutElastic` |
| Bouncing | `EaseInBounce`, `EaseOutBounce`, `EaseInOutBounce` |

The elastic, back and bounce curves overshoot on the way, so values briefly go below 0 or above the target. That looks good on a bar or pie chart and odd on a line chart with a fixed axis range.

`EasingFunction` is a functional interface that extends `TimeInterpolator`, so a custom curve is one lambda:

```kotlin
val overshootTwice = Easing.EasingFunction { t -> t * t * (3f * t - 2f) }

chart.animateY(1000, overshootTwice)
```

`EasingFunction` adds nothing to Android's `TimeInterpolator`, but the animation functions ask for an `EasingFunction`, so wrap an existing interpolator: `Easing.EasingFunction { AccelerateInterpolator().getInterpolation(it) }`.

## How the phases drive the drawing

Behind the functions sits one `ChartAnimator` per chart, reachable as `chart.animator`. It holds two values:

| Property | Meaning | Default |
| --- | --- | --- |
| `phaseX` | Share of the entries that is drawn, 0 to 1 | `1` |
| `phaseY` | Factor the drawn values are multiplied by, 0 to 1 | `1` |

`animateX` runs `phaseX` from 0 to 1, `animateY` runs `phaseY`, and `animateXY` runs both. The renderers read them on every draw: a line renderer multiplies each y value by `phaseY` and draws the first `phaseX` share of the entries currently in view, a pie renderer scales its slice angles, a bar renderer scales the bar height. Values assigned to either phase are clamped into 0 until 1.

You can set a phase directly to freeze the chart in a partly drawn state, which is occasionally useful for a screenshot or a custom transition:

```kotlin
chart.animator.phaseY = 0.5f   // every value drawn at half height
chart.invalidate()
```

Markers follow the same rule: an entry that the x animation has not reached yet gets no marker.

## Spin a pie or radar chart

`PieChart` and `RadarChart` can rotate their whole content. `spin` animates the rotation angle and redraws on every step.

```kotlin
chart.spin(
    durationMillis = 2000,
    fromAngle = chart.rotationAngle,
    toAngle = chart.rotationAngle + 360f,
    easing = Easing.EaseInOutCubic,
)
```

Angles are degrees, 0 at 3 o'clock, increasing clockwise. The start angle is applied at once, so passing the current `rotationAngle` makes the spin continue from where the chart stands. An end angle outside 0 until 360 keeps spinning through full turns, which is how the example above turns exactly once.

`spin` is independent of `animateX` and `animateY`, so a pie chart can grow and turn at the same time. A second `spin` cancels the running one. Like the other animations it takes an `onEnd` lambda, and `stopAnimations()` ends it at `toAngle`.

## Animate the viewport

Scrolling and zooming have animated counterparts on the charts with axes. They run as viewport jobs, which means they wait until the chart has a size before they start, so it is safe to call them straight after setting the data.

```kotlin
val left = YAxis.AxisDependency.LEFT

chart.moveViewToAnimated(xValue = 120f, yValue = 50f, axis = left, duration = 800)
chart.centerViewToAnimated(xValue = 120f, yValue = 50f, axis = left, duration = 800)

chart.zoomAndCenterAnimated(
    scaleX = 4f,
    scaleY = 1f,
    xValue = 120f,
    yValue = 50f,
    axis = left,
    duration = 800,
)
```

| Function | Effect |
| --- | --- |
| `moveViewToAnimated` | Scrolls so `xValue` sits at the left edge and `yValue` is vertically centered |
| `centerViewToAnimated` | Scrolls so the given position is at the center of the content area |
| `zoomAndCenterAnimated` | Zooms to the given factors while moving that position into the center |

Durations are milliseconds and of type `Long` here. A scale factor of 1 means fully zoomed out on that axis. The non animated `moveViewToX`, `moveViewTo`, `centerViewTo`, `zoom` and `fitScreen` are described in [Modifying the viewport](/mpandroidchart/docs/viewport/).

## Animations in Compose

`ChartState` forwards the three entry animations, so you start them from a `LaunchedEffect` instead of after setting the data:

```kotlin
val state = rememberChartState()

LaunchedEffect(lineData) { state.animateX(600) }

LineChart(
    data = lineData,
    state = state,
    modifier = Modifier.fillMaxWidth().height(220.dp),
)
```

`state.animateX`, `state.animateY` and `state.animateXY` take the same durations and easing curves, without `onEnd`, and do nothing before the chart view exists.

To animate from one data object to the next, set `animateChanges = true` on the chart composable. Every new `data` instance then moves in from the values shown before, over 300 ms, the way `animateDataChange` does it:

```kotlin
val data = remember(totals) {
    BarData(BarDataSet(totals.mapIndexed { i, total -> BarEntry(i.toFloat(), total) }, "Sales"))
}

BarChart(
    data = data,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    animateChanges = true,
)
```

It is off by default, and every chart composable has it, right after `marker`. The first data and data of another shape are set without animating. For another duration or curve, or an `onEnd`, call `state.animateDataChange(newData, durationMillis, easing, onEnd)` yourself, for example from a button, and hand the same instance to the composable, so the next recomposition finds it on the chart already and leaves it alone:

```kotlin
var data by remember { mutableStateOf(initialData) }

Button(onClick = {
    val next = buildData()
    data = next
    state.animateDataChange(next, 800, Easing.EaseInOutCubic)
}) { Text("Next") }
```

It updates `selectedEntry` and `selectedHighlight` when it ends.

The viewport functions `state.zoomIn`, `state.fitScreen` and `state.moveViewToX` are not animated; reach for `setup` or `update` and call the chart's own animated functions when you need those.

## From Java

`animateX`, `animateY`, `animateXY` and `spin` generate the shorter overloads for Java, so `chart.animateX(600)` compiles there as it is. `onEnd` is a Kotlin function type, so a Java lambda returns `Unit.INSTANCE`:

```java
chart.animateX(600, Easing.INSTANCE.getEaseOutCubic(), () -> {
    button.setEnabled(true);
    return Unit.INSTANCE;
});
```

`animateValue` and `animateDataChange` take every parameter from Java. [Calling the library from Java](/mpandroidchart/docs/java-interop/) has the general rules.
