# Animations

Building the chart up over time with animateX, animateY and animateXY, the easing curves that shape them, spinning round charts, and animating the viewport.

## Animate the entries

Three functions exist on every chart type. Each one returns immediately and redraws the chart on every frame, so no extra `invalidate()` is needed.

```kotlin
chart.animateX(1500)          // build up from left to right
chart.animateY(1500)          // grow from the bottom up
chart.animateXY(1500, 1500)   // both at once
```

| Function | Effect |
| --- | --- |
| `animateX(durationMillis, easing)` | Reveals the entries one after the other along the x axis |
| `animateY(durationMillis, easing)` | Scales the values up from zero |
| `animateXY(durationMillisX, durationMillisY, easingX, easingY)` | Runs both, each with its own duration and curve |

Durations are milliseconds. Call the animation after the data is set, usually right after `chart.data = ...`. Calling it again restarts the animation from the beginning.

On a pie or radar chart the same functions work: the x animation sweeps the slices into place and the y animation grows each slice or the web polygon.

## Easing

Every animation function takes an easing curve as its last parameter. The default is `Easing.Linear`, except `animateXY`, whose `easingY` follows `easingX`.

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

`spin` is independent of `animateX` and `animateY`, so a pie chart can grow and turn at the same time.

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

`state.animateX`, `state.animateY` and `state.animateXY` take the same durations and easing curves and do nothing before the chart view exists. The viewport functions `state.zoomIn`, `state.fitScreen` and `state.moveViewToX` are not animated; reach for `setup` or `update` and call the chart's own animated functions when you need those.
