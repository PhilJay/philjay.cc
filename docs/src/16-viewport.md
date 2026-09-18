# Modifying the viewport

Everything that decides which part of the data is on screen: zoom, scroll, the limits on both, the offsets around the content area, and how to read the current state back.

The viewport is the window your data is seen through. It has a zoom factor per axis and a position, and the chart keeps both inside limits you can set. All of this lives on `BarLineChartBase`, so it is available on `LineChart`, `BarChart`, `HorizontalBarChart`, `ScatterChart`, `CandleStickChart`, `BubbleChart` and `CombinedChart`. Pie and radar charts have no viewport.

> The visible range calls divide the current axis range, and the move, center and value based zoom calls convert values to pixels, so set `chart.data` before them. On a chart without data they do nothing useful.

## Restrict what is visible

These four set the zoom limits, expressed in values rather than in scale factors. They take effect the moment you call them and clamp the current zoom if it is already outside the new limits.

```kotlin
chart.setVisibleXRangeMaximum(20f)  // never show more than 20 x units at once
chart.setVisibleXRangeMinimum(5f)   // never show fewer than 5
chart.setVisibleXRange(5f, 20f)     // both at once
chart.setVisibleYRangeMaximum(100f, YAxis.AxisDependency.LEFT)
```

| Call | Meaning |
| --- | --- |
| `setVisibleXRangeMaximum(max)` | largest span of x values on screen, so the user cannot zoom out further |
| `setVisibleXRangeMinimum(min)` | smallest span of x values on screen, so the user cannot zoom in further |
| `setVisibleXRange(min, max)` | both x limits in one call |
| `setVisibleYRangeMaximum(max, axis)` | largest span of y values on screen, for one y axis |
| `setVisibleYRangeMinimum(min, axis)` | smallest span of y values on screen, for one y axis |
| `setVisibleYRange(min, max, axis)` | both y limits in one call |

Each of them divides the current axis range by the span you pass and stores the result as a scale limit. The limit is a number, not a rule: when the data grows afterwards, the axis range grows with it and the visible span no longer matches. Call the function again after changing the data.

These six clamp the viewport but do not redraw by themselves, so follow them with a move call, which does, or with `invalidate()`.

`setScaleMinima(scaleX, scaleY)` sets the same two lower limits directly as factors, where 1 means fully zoomed out. Factors below 1 are raised to 1.

> On a `HorizontalBarChart` the axes are swapped on screen, and so are these calls internally: `setVisibleXRangeMaximum` limits the vertical scale there. You still pass x values.

## Move the view

```kotlin
chart.moveViewToX(10f)                              // left edge at x = 10
chart.moveViewTo(10f, 50f, AxisDependency.LEFT)    // left edge at x = 10, y centered
chart.centerViewTo(10f, 50f, AxisDependency.LEFT)   // x = 10 and y = 50 both centered
chart.centerViewToY(50f, AxisDependency.LEFT)      // y centered, left edge at x = 0
```

`moveViewTo` puts the x value at the **left edge** of the content area, `centerViewTo` puts it in the **middle**. Both make most sense together with a visible range limit, because otherwise the whole data set is on screen and there is nothing to scroll to.

Two of them animate:

```kotlin
chart.moveViewToAnimated(10f, 50f, AxisDependency.LEFT, 500)
chart.centerViewToAnimated(10f, 50f, AxisDependency.LEFT, 500)
```

The duration is in milliseconds. All six redraw the chart themselves, so there is no `invalidate()` to add.

## Zoom

```kotlin
chart.zoomIn()                       // by 1.4 around the center of the content area
chart.zoomOut()                      // by 0.7 around the center
chart.zoomToCenter(2f, 1f)           // by the given factors around the center
chart.zoom(2f, 1f, dx, dy)           // around a point relative to the content area
chart.zoom(2f, 1f, 10f, 50f, AxisDependency.LEFT)  // zoom, then center on that point
chart.zoomAndCenterAnimated(2f, 1f, 10f, 50f, AxisDependency.LEFT, 500)
```

A factor of 1 is no change, above 1 zooms in, below 1 zooms out. The factors are relative to the current zoom, not absolute, except in `zoomAndCenterAnimated`, which animates towards the factors as an absolute target.

`zoomIn`, `zoomOut`, `zoomToCenter` and the pixel overload of `zoom` apply at once. The value overload of `zoom` and `zoomAndCenterAnimated` need the value to pixel matrices, so they run as viewport jobs.

The `x` and `y` of the pixel overload are not view pixels: `x` counts from the left edge of the content area and `y` from its bottom edge. `(chart.chartTouchListener as BarLineChartTouchListener).getTrans(px, py)` turns a touch position into them.

Two calls undo zooming, and they differ in one detail:

| Call | What it does |
| --- | --- |
| `resetZoom()` | scales back to 1 around the center, keeping the scale limits, so a chart with `setVisibleXRangeMaximum(20f)` returns to that 20 unit window. The position is only clamped to the new limits, which without a scale minimum means the left edge |
| `fitScreen()` | the same, and also drops the lower scale limits back to 1, so the whole data set fills the content area |

Use `resetZoom()` when the limits should survive and `fitScreen()` when you want a clean slate.

## Offsets around the content area

The content area is the chart minus the space taken by the axis labels, the legend and the extra offsets. Normally the chart works that space out on every layout.

```kotlin
chart.setExtraOffsets(0f, 16f, 0f, 16f)   // dp, added to the calculated offsets
chart.minOffset = 15f                    // dp, smallest offset on any side, the default
```

`setExtraOffsets` is the safe way to make room. It leaves the automatic calculation intact and only adds to it.

`setViewPortOffsets` replaces the calculation entirely:

```kotlin
chart.setViewPortOffsets(0f, 0f, 0f, 0f)   // pixels, edge to edge
```

From then on the axis labels and the legend no longer get space reserved for them, which is why the example app uses it on charts whose x axis is off or drawn inside the content area with `XAxisPosition.TOP_INSIDE`. The values are pixels, not dp, and they are applied on the next pass of the UI loop rather than immediately. `chart.resetViewPortOffsets()` gives the automatic calculation back.

## Immediate calls and viewport jobs

A viewport call that works in value space needs the value to pixel matrices, and those only exist once the chart has been measured. Those calls are queued as **viewport jobs**: posted right away when the chart already has a size, and otherwise stored until the first layout, then run.

| Runs at once | Runs as a viewport job |
| --- | --- |
| `zoomIn`, `zoomOut`, `zoomToCenter` | `zoom(scaleX, scaleY, xValue, yValue, axis)` |
| `zoom(scaleX, scaleY, x, y)` relative to the content area | `zoomAndCenterAnimated` |
| `resetZoom`, `fitScreen` | `moveViewToX`, `moveViewTo`, `moveViewToAnimated` |
| `setVisibleXRange...`, `setVisibleYRange...`, `setScaleMinima` | `centerViewTo`, `centerViewToY`, `centerViewToAnimated` |

That is why you can set the viewport in `onCreate`, before the chart has ever been drawn, and it still lands correctly. `chart.clearAllViewportJobs()` drops the queue if something has changed in the meantime.

## Read the current viewport

| Property | Returns |
| --- | --- |
| `chart.lowestVisibleX` | x value at the left edge, never below the axis minimum |
| `chart.highestVisibleX` | x value at the right edge, never above the axis maximum |
| `chart.visibleXRange` | the span between the two |
| `chart.zoomX` | horizontal zoom factor, 1 when fully zoomed out |
| `chart.zoomY` | vertical zoom factor |
| `chart.isFullyZoomedOut` | true while both factors are 1 and no scale minimum above 1 is set, so a chart with `setVisibleXRangeMaximum` never reports true |

These are the ones to read in a scroll or gesture listener, for example to load more data when the user reaches the edge:

```kotlin
chart.gestureListeners.add(object : OnChartGestureListener {
    override fun onChartTranslate(me: MotionEvent, dX: Float, dY: Float) {
        if (chart.highestVisibleX >= chart.xAxis.axisMaximum) loadMore()
    }
})
```

For anything below this level, such as the content rectangle in pixels or the touch matrix itself, go to [the ViewPortHandler](/mpandroidchart/docs/viewporthandler/).

## Where to go next

- [Interaction with the chart](/mpandroidchart/docs/interaction/) for the gestures that move the viewport by touch.
- [Dynamic and realtime data](/mpandroidchart/docs/dynamic-data/) for the scrolling window on a live feed.
- [The ViewPortHandler](/mpandroidchart/docs/viewporthandler/) for the object behind all of it.
