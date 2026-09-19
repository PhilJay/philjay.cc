# The ViewPortHandler

The object behind every chart that knows the chart size, the rectangle the data is drawn in, and the zoom and drag state, with the limits that keep all three sane.

Every chart owns one `ViewPortHandler`. The chart functions described in [modifying the viewport](/mpandroidchart/docs/viewport/) are a safe layer on top of it: they work in values, take care of the limits and redraw afterwards. The handler itself works in pixels and matrices, and is what you read when you need to know exactly where something is on screen.

```kotlin
val handler = chart.viewPortHandler
```

The property is read only. A chart creates its handler in `init` and keeps it for its lifetime, so you query it and set limits on it, but you never replace it.

## The chart size and the content rectangle

Two different rectangles matter.

The **chart size** is the view: `chartWidth` and `chartHeight` in pixels, set by the chart from `onSizeChanged`.

The **content rectangle** is the part of it the data is actually drawn in, the chart size minus the space taken by the axis labels, the legend, the extra offsets and `minOffset`. Everything the renderers clip to is this rectangle.

| Property | Meaning |
| --- | --- |
| `chartWidth`, `chartHeight` | size of the whole view in pixels |
| `contentRect` | the drawing area as a `RectF` |
| `contentLeft`, `contentTop`, `contentRight`, `contentBottom` | its edges in pixels |
| `contentWidth`, `contentHeight` | its size |
| `contentCenter` | its center as an `MPPointF` |
| `offsetLeft`, `offsetTop`, `offsetRight`, `offsetBottom` | the gap between each view edge and the rectangle |
| `smallestContentExtension` | the smaller of content width and height |
| `hasChartDimens()` | true once the view has a non zero size |

`hasChartDimens()` is the check the chart itself uses to decide whether a viewport call can run now or has to wait for the first layout.

## The touch matrix

`matrixTouch` is a single `android.graphics.Matrix` holding the current zoom and scroll. Its scale and translation are mirrored into four read only properties, which is what you normally read instead of picking the matrix apart:

| Property | Meaning |
| --- | --- |
| `scaleX`, `scaleY` | current zoom factor per axis, 1 when fully zoomed out |
| `transX`, `transY` | current scroll offset in pixels |

The functions that change the viewport do not change the matrix in place. They build a new matrix from `matrixTouch` with the change applied and hand it back, and `refresh` is what makes it current:

```kotlin
val center = handler.contentCenter
val next = handler.zoomIn(center.x, center.y)
handler.refresh(next, chart, true)   // clamps to the limits, then redraws
```

`refresh` copies the matrix into `matrixTouch`, clamps it there with `limitTransAndScale` and writes the clamped values back into the matrix you passed, so a matrix that would put the data outside its bounds is corrected rather than accepted. Most of these also come in an `outputMatrix` form that writes into a matrix you own instead of allocating one, which is what the charts use in their draw path. `setZoom(scaleX, scaleY, x, y)` is the one that does not.

`zoomIn`, `zoomOut`, `zoom`, `setZoom`, `fitScreen` and `translate` all follow this build then refresh shape. `centerViewPort(pts, view)` is the exception: it translates, refreshes and redraws in one call.

## Scale and translation limits

The limits are the reason the chart cannot be dragged into empty space.

| Property | Default | Meaning |
| --- | --- | --- |
| `minScaleX`, `minScaleY` | 1 | how far out the chart may zoom |
| `maxScaleX`, `maxScaleY` | `Float.MAX_VALUE` | how far in the chart may zoom |
| `dragOffsetX`, `dragOffsetY` | 0 | extra distance in dp the content may be dragged past its bounds |

The scale limits are set through six functions, each of which clamps the current matrix right away:

```kotlin
handler.setMinimumScaleX(2f)     // values below 1 are raised to 1
handler.setMaximumScaleX(0f)     // 0 removes the limit
handler.setMinMaxScaleX(2f, 8f)
handler.setMinimumScaleY(2f)
handler.setMaximumScaleY(10f)
handler.setMinMaxScaleY(2f, 10f)
```

These are exactly what `chart.setVisibleXRangeMaximum` and its siblings call after converting a span of values into a scale factor, so prefer the chart functions unless you already think in factors.

The translation limit follows from the scale: the content may be moved between `-contentWidth * (scaleX - 1)` and 0 horizontally, widened on both sides by `dragOffsetX`. `hasNoDragOffset` is true while neither offset is set.

Four properties tell you whether there is room left to move:

```kotlin
handler.canZoomInMoreX    // scaleX < maxScaleX
handler.canZoomOutMoreX   // scaleX > minScaleX
handler.canZoomInMoreY
handler.canZoomOutMoreY
```

`isFullyZoomedOut`, with its `isFullyZoomedOutX` and `isFullyZoomedOutY` halves, is true only when the chart sits at scale 1 *and* no minimum above 1 is set.

## Bounds checks

Renderers use these to skip anything that would be drawn outside the content rectangle. All of them take pixels.

| Call | True when |
| --- | --- |
| `isInBounds(x, y)` | the point is inside the content rectangle |
| `isInBoundsX(x)` | the x is inside it horizontally |
| `isInBoundsY(y)` | the y is inside it vertically |
| `isInBoundsLeft(x)` | the x is not more than 1 pixel left of the rectangle |
| `isInBoundsRight(x)` | the x is not more than 1 pixel right of it |
| `isInBoundsTop(y)` | the y is not above it |
| `isInBoundsBottom(y)` | the y is not below it |

The one pixel tolerance on the left and right sides keeps a point that lands exactly on the edge from being dropped by a rounding error. A custom renderer should use the same checks so its drawing clips like the built in ones.

## Turning values into pixels

The handler works in pixels, and your data is in values. The bridge is `Transformer`, one per y axis:

```kotlin
val transformer = chart.getTransformer(YAxis.AxisDependency.LEFT)

val pixel = transformer.getPixelForValues(10f, 50f)    // value to pixel
val value = transformer.getValuesByTouchPoint(x, y)    // pixel to value
```

A transformer applies three matrices in order: a value matrix that scales values to unzoomed pixel distances, the handler's `matrixTouch` with the current zoom and drag, and an offset matrix that moves the result into the content rectangle and flips the y direction. `valueToPixelMatrix` is the three combined and `pixelToValueMatrix` its inverse. Both return a buffer that is overwritten on the next access, so read from them and do not keep the reference.

For single points there are shortcuts on the chart itself, which pick the right transformer for you:

```kotlin
chart.getPixelForValues(10f, 50f, YAxis.AxisDependency.LEFT)
chart.getValuesByTouchPoint(x, y, YAxis.AxisDependency.LEFT)
chart.getPosition(entry, YAxis.AxisDependency.LEFT)
```

> A `HorizontalBarChart` installs a `HorizontalViewPortHandler`, which behaves exactly like the base class. What differs is the chart above it: its `setVisibleXRange` functions set the y scale limits and the other way round, because its axes are swapped on screen.

## Where to go next

- [Modifying the viewport](/mpandroidchart/docs/viewport/) for the safe, value based layer on top of this.
- [Custom data sets](/mpandroidchart/docs/custom-datasets/) if you are here because you are writing a renderer.
- The [API reference](https://jitpack.io/com/github/PhilJay/MPAndroidChart/MPChartLib/v4.0.0-beta01/javadoc/) for every overload.
