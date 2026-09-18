# Interaction with the chart

Every touch gesture a chart understands, how to switch each one off, and the listeners that tell you what the user did.

## Switch gestures on and off

All interaction runs through one flag on every chart type:

```kotlin
chart.isTouchEnabled = false   // the chart ignores touch completely
```

With touch enabled, each gesture has its own property. The drag and scale properties live on the charts with axes (`LineChart`, `BarChart`, `HorizontalBarChart`, `ScatterChart`, `CandleStickChart`, `BubbleChart`, `CombinedChart`).

| Property | Meaning | Default |
| --- | --- | --- |
| `isTouchEnabled` | All touch interaction, on every chart type | `true` |
| `isDragXEnabled` | Pan horizontally | `true` |
| `isDragYEnabled` | Pan vertically | `true` |
| `isDragEnabled` | Reads true when either axis can be dragged, writes both | `true` |
| `isScaleXEnabled` | Zoom the x axis by gesture | `true` |
| `isScaleYEnabled` | Zoom the y axis by gesture | `true` |
| `isScaleEnabled` | Reads true when either axis can be scaled, writes both | `true` |
| `isPinchZoomEnabled` | A pinch scales both axes together | `false` |
| `isDoubleTapToZoomEnabled` | A double tap zooms in | `true` |
| `isHighlightPerTapEnabled` | A tap selects the nearest value, on every chart type | `true` |
| `isHighlightPerDragEnabled` | Dragging moves the selection while the chart cannot pan | `true` |
| `isRotationEnabled` | Rotate a pie or radar chart by dragging | `true` |

A chart that should only show data, with no gestures at all, is the common case. The example app's design charts do exactly this:

```kotlin
chart.isScaleEnabled = false
chart.isDragEnabled = false
chart.isDoubleTapToZoomEnabled = false
```

## Dragging and zooming

Dragging pans the content once the chart is zoomed in. A single finger has to travel about 3 dp before the touch counts as a drag rather than a tap.

Zooming works in one of two ways. With `isPinchZoomEnabled` false, which is the default, a two finger gesture that is mostly horizontal zooms the x axis and a mostly vertical one zooms the y axis, so you can stretch one axis without the other. Set it to true and a pinch scales both axes by the same factor.

```kotlin
chart.isPinchZoomEnabled = true
```

A double tap zooms in by a factor of 1.4 around the tapped position, on each axis that has scaling enabled.

Two extra properties let the content be dragged a little past its bounds, which feels softer at the edges:

```kotlin
chart.dragOffsetX = 20f   // dp of overscroll left and right
chart.dragOffsetY = 20f   // dp of overscroll top and bottom
```

Both default to 0. They also matter for highlighting per drag: the chart only moves the selection instead of panning when it is fully zoomed out *and* has no drag offset.

Zooming and scrolling from code, including limits on how far the user may zoom, is covered in [Modifying the viewport](/mpandroidchart/docs/viewport/).

## Fling and deceleration

Lifting the finger after a fast drag keeps the chart scrolling and slows it down.

| Property | Meaning | Default |
| --- | --- | --- |
| `isDragDecelerationEnabled` | Keep scrolling after the finger lifts | `true` |
| `dragDecelerationFrictionCoef` | How slowly the scroll loses speed | `0.9` |

The friction coefficient is multiplied into the velocity on every frame. 0 stops the chart at once, values near 1 let it coast for a long time. Assigned values are clamped into 0 until 0.999.

```kotlin
chart.dragDecelerationFrictionCoef = 0.95f
```

Pie and radar charts use the same two properties for their rotation, so a flick keeps the chart spinning.

## Rotating pie and radar charts

`PieChart` and `RadarChart` are rotated by dragging instead of panned.

```kotlin
chart.isRotationEnabled = true
chart.rotationAngle = 0f     // where the first slice starts
```

Angles are degrees, 0 at 3 o'clock, increasing clockwise. `rotationAngle` normalizes what you assign into 0 until 360; `rawRotationAngle` keeps the value you passed. The default is 270, which puts the first slice at the top.

To turn the chart from code, see `spin()` in [Animations](/mpandroidchart/docs/animations/).

## React to a selected value

The shortest form takes a lambda:

```kotlin
chart.onValueSelected { entry, highlight ->
    Log.i("selected", "${entry.x} / ${entry.y} in set ${highlight.dataSetIndex}")
}
```

A second lambda handles the case where the selection is cleared:

```kotlin
chart.onValueSelected(
    onNothingSelected = { detailView.isVisible = false },
) { entry, _ ->
    detailView.isVisible = true
    detailView.text = entry.y.toString()
}
```

Both forms replace `chart.onChartValueSelectedListener`. Implement the interface yourself when one class handles several charts:

```kotlin
class ReportActivity : AppCompatActivity(), OnChartValueSelectedListener {

    override fun onValueSelected(e: Entry<*>, h: Highlight) { }

    override fun onNothingSelected() { }
}

chart.onChartValueSelectedListener = this
```

`onNothingSelected` fires when the user taps empty space, taps the selected value again, or the highlighted entry is no longer in the data. Calls to `chart.highlightValue(...)` report here as well unless you pass `callListener = false`. What the `Highlight` contains is described in [Highlighting values](/mpandroidchart/docs/highlighting/).

## React to gestures

`OnChartGestureListener` reports the raw gestures. Every method has an empty default body, so implement only the ones you need.

| Callback | When it fires |
| --- | --- |
| `onChartGestureStart` | A finger touches the chart |
| `onChartGestureEnd` | The touch ends or is cancelled |
| `onChartSingleTapped` | Single tap, before the tap highlight is applied |
| `onChartDoubleTapped` | Double tap, before the double tap zoom is applied |
| `onChartLongPressed` | Long press |
| `onChartFling` | Fast swipe, with the velocity in pixels per second |
| `onChartScale` | Pinch or double tap zoom, with the scale factor per axis |
| `onChartTranslate` | Drag, including the deceleration after a fling |

```kotlin
chart.onChartGestureListener = object : OnChartGestureListener {

    override fun onChartTranslate(me: MotionEvent, dX: Float, dY: Float) {
        syncOtherChart(chart.lowestVisibleX, chart.highestVisibleX)
    }

    override fun onChartScale(me: MotionEvent, scaleX: Float, scaleY: Float) {
        syncOtherChart(chart.lowestVisibleX, chart.highestVisibleX)
    }
}
```

The start and end callbacks also receive the gesture that was recognised, as a `ChartTouchListener.ChartGesture`: `NONE`, `DRAG`, `X_ZOOM`, `Y_ZOOM`, `PINCH_ZOOM`, `ROTATE`, `SINGLE_TAP`, `DOUBLE_TAP`, `LONG_PRESS` or `FLING`.

## Several listeners on one chart

`onChartValueSelectedListener` and `onChartGestureListener` each hold a single listener, so assigning a second one replaces the first. When something else has to observe the chart without taking that slot away from your app, add it to one of the two lists instead:

```kotlin
chart.valueSelectedListeners += analyticsListener
chart.gestureListeners += analyticsListener
```

The single listener is called first, then the list entries in order. This is how the Compose module observes a chart while your own listener keeps working.

## Charts inside a scrolling parent

A chart that is dragged inside a `ScrollView` or a `RecyclerView` fights the parent for the gesture. [Charts in lists and scrolling screens](/mpandroidchart/docs/lists-and-scrolling/) covers the whole situation. The chart already asks the parent to stop intercepting while a drag or zoom is running, and you can do the same from your own touch handling:

```kotlin
chart.disableScroll()   // the gesture stays with the chart
chart.enableScroll()    // the parent may intercept again
```

## Interaction in Compose

The Compose charts report the same events through `ChartState`, so you read the selection as state instead of registering a listener:

```kotlin
val state = rememberChartState()

LineChart(
    data = lineData,
    state = state,
    modifier = Modifier.fillMaxWidth().height(220.dp),
)

val selected = state.selectedEntry
Text(if (selected == null) "Tap a point" else "Selected ${selected.y}")
```

`state.selectedHighlight`, `state.lowestVisibleX`, `state.highestVisibleX`, `state.zoomX`, `state.zoomY` and `state.rotationAngle` follow the user in the same way. To drive the chart from Compose, call `state.highlight(x)`, `state.clearHighlight()`, `state.zoomIn()`, `state.fitScreen()` or `state.moveViewToX(value)`. Everything else about the module is in [Jetpack Compose](/mpandroidchart/docs/compose/).
