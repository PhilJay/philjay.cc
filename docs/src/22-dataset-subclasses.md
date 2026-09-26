# DataSet subclasses

What each chart type's data set adds on top of the shared settings, from line modes and bar corners to candle colors and pie value lines.

Everything in [The DataSet class](/mpandroidchart/docs/dataset/) works on all of them. This chapter only lists what is new per class. Three intermediate classes sit in between and are shared by several chart types, so they come first.

## Highlight settings shared by several types

`BarLineScatterCandleBubbleDataSet` is the base of every set that lives on an x and a y axis, so bar, line, scatter, candle and bubble. It adds one property:

| Property | Meaning | Default |
| --- | --- | --- |
| `highlightColor` | color of the highlight indicator | light orange, `rgb(255, 187, 115)` |

`BarDataSet` overrides that default with black.

`LineScatterCandleRadarDataSet` adds the crosshair lines drawn through a highlighted entry, for line, scatter, candle and radar sets:

| Property | Meaning | Default |
| --- | --- | --- |
| `isVerticalHighlightIndicatorEnabled` | draw the vertical line | `true` |
| `isHorizontalHighlightIndicatorEnabled` | draw the horizontal line | `true` |
| `verticalHighlightIndicatorSpan` | how far the vertical line reaches: `FULL`, `TO_ENTRY` or `FROM_ENTRY` | `FULL` |
| `horizontalHighlightIndicatorSpan` | the same for the horizontal line | `FULL` |
| `highlightLineWidth` | width of both lines in dp | `0.5f` |
| `dashPathEffectHighlight` | dash pattern, read only | `null`, solid |

```kotlin
set.setDrawHighlightIndicators(false)      // both at once
set.enableDashedHighlightLine(8f, 8f, 0f)  // dash length, gap, phase, all in px
set.disableDashedHighlightLine()
```

`isDashedHighlightLineEnabled` tells you whether a pattern is set.

## Line and radar fill

`LineRadarDataSet` is the base of `LineDataSet` and `RadarDataSet`: a stroked line with an optional filled area under it.

| Property | Meaning | Default |
| --- | --- | --- |
| `lineWidth` | stroke width in dp, clamped to 0 to 10 | `1f` |
| `isDrawFilledEnabled` | fill the area between the line and the axis | `false` |
| `fillColor` | color of the filled area | `rgb(140, 234, 255)` |
| `fillAlpha` | opacity of the filled area, 0 to 255 | `85` |
| `fillDrawable` | drawable painted into the area instead of the color | `null` |

```kotlin
set.lineWidth = 3f
set.isDrawFilledEnabled = true
set.fillColor = Color.BLUE
set.fillAlpha = 90
```

Assigning `fillColor` clears `fillDrawable`, so whichever you set last is the one that is drawn. Filling clips the canvas to a path and costs more than drawing the line alone. Where the fill stops is decided by the [fill formatter](/mpandroidchart/docs/fillformatter/).

> The old documentation gives the minimum line width as 0.2. It is 0, which draws the thinnest line the device can.

## LineDataSet

The mode decides how the points are connected.

| `LineDataSet.Mode` | Draws |
| --- | --- |
| `LINEAR` (the default) | straight segments from point to point |
| `STEPPED` | horizontal steps, the y changes at each entry |
| `CUBIC_BEZIER` | a smooth curve through the points, bent by `cubicIntensity` |
| `HORIZONTAL_BEZIER` | a smooth curve with horizontal control points, so it never overshoots in y |

```kotlin
set.mode = LineDataSet.Mode.CUBIC_BEZIER
set.cubicIntensity = 0.18f   // clamped to 0.05 (almost straight) to 1, default 0.2
```

> A cubic line is one path with one color. Only `LINEAR` and `STEPPED` draw a segment per entry and use the whole `colors` list.

Circles at the entries:

| Property | Meaning | Default |
| --- | --- | --- |
| `isDrawCirclesEnabled` | draw a circle at every entry | `true` |
| `circleRadius` | radius in dp, values below 1 are ignored and logged | `4f` |
| `circleColors` | circle colors, cycled per entry | one `rgb(140, 234, 255)` |
| `circleColor` | first circle color; assigning replaces the whole list | |
| `isDrawCircleHoleEnabled` | punch a hole into each circle | `true` |
| `circleHoleRadius` | hole radius in dp, values below 0.5 are ignored and logged | `2f` |
| `circleHoleColor` | hole color, `ColorTemplate.COLOR_NONE` leaves the hole transparent | white |

`setCircleColors(vararg colors: Int)` and `setCircleColors(colorResIds, context)` fill the list, `resetCircleColors()` empties it.

Dashed lines:

```kotlin
set.enableDashedLine(10f, 5f, 0f)  // dash length, gap, phase, all in px
set.disableDashedLine()
```

`isDashedLineEnabled` reports the state and `dashPathEffect` gives you the effect itself. A dashed line is rendered onto the chart's internal bitmap rather than straight onto the canvas.

Fill and highlight:

| Property | Meaning | Default |
| --- | --- | --- |
| `fillFormatter` | decides the y value the fill reaches down to | `DefaultFillFormatter()` |
| `isDrawHighlightCircleEnabled` | draw a ring on the highlighted entry | `false` |
| `highlightCircleRadius` | radius of that ring in dp | `5f` |

The ring is drawn in three layers: a halo in `highlightColor` at 70 alpha, a disc in `circleHoleColor`, and a stroke in the set's `color`.

## BarDataSet

```kotlin
val set = BarDataSet(entries, "Orders")
set.barCornerRadius = 7f
set.barBorderWidth = 1f
set.barBorderColor = Color.BLACK
set.highlightAlpha = 0
```

| Property | Meaning | Default |
| --- | --- | --- |
| `barCornerRadius` | corner radius in dp, 0 for sharp corners | `0f` |
| `barBorderWidth` | border around each bar in dp, 0 for none | `0f` |
| `barBorderColor` | color of that border | black |
| `barShadowColor` | color of the shadow bar behind each bar | `rgb(215, 215, 215)` |
| `highlightAlpha` | opacity of the overlay on a selected bar, 0 to 255 | `120` |
| `stackLabels` | legend labels for the stack positions | empty |
| `fills` | gradient fills used instead of `colors`, cycled per bar | `null` |

`barCornerRadius` is new in version 4. The radius is capped at half the bar's width and height, so a short bar keeps a sane shape. On a stacked bar only the top corners of the last stack segment are rounded, which keeps the stack looking like one bar.

Bar shadows are switched on at the chart, with `chart.isDrawBarShadowEnabled = true`, and then use each set's `barShadowColor`.

Stacking is decided by the entries: a `BarEntry` with `stackValues` is a stacked bar. Three read-only properties describe it, the last of them on `BarDataSet` rather than on the interface:

| Property | Meaning |
| --- | --- |
| `stackSize` | largest number of stack values in any entry, 1 for plain bars |
| `isStacked` | true when `stackSize` is above 1 |
| `entryCountStacks` | number of entries counting every stack value separately |

For fills, see [Setting colors](/mpandroidchart/docs/colors/). `setGradientColor(startColor, endColor)` is the shortcut for one gradient on every bar.

## ScatterDataSet

```kotlin
val set = ScatterDataSet(entries, "DS 2")
set.setScatterShape(ScatterChart.ScatterShape.CIRCLE)
set.scatterShapeSize = 8f
set.scatterShapeHoleRadius = 2f
set.scatterShapeHoleColor = ColorTemplate.COLORFUL_COLORS[3]
```

| Property | Meaning | Default |
| --- | --- | --- |
| `scatterShapeSize` | size of each shape in dp | `7.5f` |
| `shapeRenderer` | the object that draws the shape | `SquareShapeRenderer()` |
| `scatterShapeHoleRadius` | radius of the hole in dp, 0 for none | `0f` |
| `scatterShapeHoleColor` | hole color, `COLOR_NONE` leaves it transparent | `COLOR_NONE` |

`setScatterShape(shape)` swaps in the built-in renderer for `SQUARE`, `CIRCLE`, `TRIANGLE`, `CROSS`, `X`, `CHEVRON_UP` or `CHEVRON_DOWN`. Only square, circle and triangle draw a hole.

For a shape of your own, implement `IShapeRenderer` and assign it to `shapeRenderer` directly. `ScatterDataSet.getRendererForShape(shape)` returns a fresh built-in renderer if you want to wrap one.

## CandleDataSet

A candle set colors the body by direction. All four colors start at `ColorTemplate.COLOR_NONE`, which means the renderer falls back to the entry's color from `colors`.

| Property | Meaning | Default |
| --- | --- | --- |
| `increasingColor` | body color when close is above open | `COLOR_NONE` |
| `decreasingColor` | body color when close is below open | `COLOR_NONE` |
| `neutralColor` | body color when open equals close | `COLOR_NONE` |
| `increasingPaintStyle` | filled or outlined increasing bodies | `Paint.Style.STROKE` |
| `decreasingPaintStyle` | filled or outlined decreasing bodies | `Paint.Style.FILL` |
| `showCandleBar` | draw bodies, or only the open and close ticks | `true` |
| `barSpace` | space left free on each side of a body, as a fraction of the x step, clamped to 0 to 0.45 | `0.1f` |
| `shadowWidth` | stroke width of the high to low line in dp | `1.5f` |
| `shadowColor` | color of that line | `COLOR_NONE` |
| `shadowColorSameAsCandle` | draw the line in its candle's body color | `false` |

```kotlin
set.increasingColor = Color.rgb(122, 242, 84)
set.increasingPaintStyle = Paint.Style.STROKE
set.decreasingColor = Color.RED
set.decreasingPaintStyle = Paint.Style.FILL
set.shadowColor = Color.DKGRAY
set.shadowWidth = 0.7f
```

The y range of a candle set comes from the entries' `low` and `high`, not from their y.

## BubbleDataSet

| Property | Meaning | Default |
| --- | --- | --- |
| `isNormalizeSizeEnabled` | scale bubbles relative to `maxSize` so the largest fills the reference size; off uses the entry size as a direct factor | `true` |
| `highlightCircleWidth` | stroke width of the ring around a highlighted bubble in dp | `1f` |
| `maxSize` | largest entry size in the set, read only | recomputed with the ranges |

`maxSize` is recomputed from scratch whenever the full ranges are, so it shrinks again after an entry is removed or after `notifyDataSetChanged()`. Adding a single entry can only widen it.

## RadarDataSet

A radar set is a `LineRadarDataSet`, so it has the line width and the fill settings above. On top it configures the ring on a highlighted entry.

| Property | Meaning | Default |
| --- | --- | --- |
| `isDrawHighlightCircleEnabled` | draw the ring at all | `false` |
| `highlightCircleFillColor` | fill of the ring, `COLOR_NONE` for no fill | white |
| `highlightCircleStrokeColor` | stroke of the ring, `COLOR_NONE` uses the set's first color | `COLOR_NONE` |
| `highlightCircleStrokeAlpha` | opacity of the stroke, 0 to 255 | `76` |
| `highlightCircleInnerRadius` | inner radius in dp | `3f` |
| `highlightCircleOuterRadius` | outer radius in dp | `4f` |
| `highlightCircleStrokeWidth` | stroke width in dp | `2f` |

## PieDataSet

A `PieData` holds exactly one pie set. Only the y range is tracked, because pie entries have no x.

| Property | Meaning | Default |
| --- | --- | --- |
| `sliceSpace` | gap between slices in dp, clamped to 0 to 20 | `0f` |
| `isAutomaticallyDisableSliceSpacingEnabled` | drop the gap when the smallest slice would be narrower than it | `false` |
| `selectionShift` | how far a highlighted slice is pushed out, in dp | `9f` |
| `highlightColor` | color of a highlighted slice, `null` keeps the slice color | `null` |

Labels and values can sit inside the slice or outside it, each on its own:

```kotlin
set.xValuePosition = PieDataSet.ValuePosition.OUTSIDE_SLICE
set.yValuePosition = PieDataSet.ValuePosition.OUTSIDE_SLICE
```

`xValuePosition` places the entry label, `yValuePosition` the value. Both default to `INSIDE_SLICE`. Once something sits outside, a connector line is drawn to it:

| Property | Meaning | Default |
| --- | --- | --- |
| `valueLineColor` | color of the connector | black |
| `isUseValueColorForLineEnabled` | draw it in the slice color instead | `false` |
| `valueLineWidth` | stroke width in dp | `1f` |
| `valueLinePart1OffsetPercentage` | where the line starts, as a percentage of the radius | `75f` |
| `valueLinePart1Length` | length of the outward part, as a fraction of the radius | `0.3f` |
| `valueLinePart2Length` | length of the horizontal part, as a fraction of the radius | `0.4f` |
| `isValueLineVariableLength` | shorten the line for slices near the horizontal center | `true` |

> `copy()` on a pie set carries over the inherited styling only. None of the properties in this section are copied.
