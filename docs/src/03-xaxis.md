# The x axis

Where the horizontal axis sits, how its labels are drawn, and the recipes for names, dates and edge padding.

`XAxis` is the horizontal axis of the line, bar, scatter, candle, bubble and combined charts, and the ring of labels around a radar chart. Its values are the x values of your entries, not their positions in the list.

```kotlin
val xAxis = chart.xAxis
```

Everything on [the axis](/mpandroidchart/docs/axis/) applies here too: enabling parts, label count, granularity, range, grid lines and limit lines. This page covers what only the x axis has.

## Position

`position` decides where the labels go.

| Value | Where the labels are drawn |
| --- | --- |
| `TOP` | Above the content area. The default. |
| `BOTTOM` | Below the content area. |
| `BOTH_SIDED` | Above and below. |
| `TOP_INSIDE` | Inside the content area, along its top edge. |
| `BOTTOM_INSIDE` | Inside the content area, along its bottom edge. |

```kotlin
chart.xAxis.position = XAxis.XAxisPosition.BOTTOM
```

The default is `TOP`, which is rarely what you want, so this is usually the first line you write for the x axis. The inside positions cost no offset, so the chart keeps its full height, which is handy for a chart that fills a card edge to edge.

## Rotating labels

Long labels collide. Rotate them instead of shortening them.

```kotlin
chart.xAxis.labelRotationAngle = -45f
```

The angle is in degrees and positive values turn clockwise. The chart measures the rotated size and reserves the space it needs, so nothing is cut off at the bottom.

## Avoiding first and last clipping

The first and the last label sit at the edges of the content area and stick out over it by half their width. Turning this on pulls them back in.

```kotlin
chart.xAxis.isAvoidFirstLastClippingEnabled = true
```

The first label always moves inwards by half its width. The last one moves only when it is wider than twice the right offset and would reach past the right edge. The default is `false`.

## Centering labels

By default a label sits exactly on its value, on the grid line. Centering draws each label halfway between two grid lines instead, which is what a grouped bar chart wants: the group name belongs between the group's boundaries, not on them.

```kotlin
chart.xAxis.isCenterAxisLabelsEnabled = true
chart.xAxis.granularity = 1f
```

Reading the property gives `false` while the axis has no computed entries, so it also tells you whether centering is currently in effect.

## The measured label size

The renderer measures the longest label on every pass and writes the result onto the axis. You can read it, for example to line up something else with the labels, but you cannot assign it.

| Property | Meaning |
| --- | --- |
| `labelWidth` | Width of the widest label in pixels. |
| `labelHeight` | Height of the labels in pixels. |
| `labelRotatedWidth` | Width of the label bounds after rotation. |
| `labelRotatedHeight` | Height of the label bounds after rotation. |

The bottom or top offset the chart reserves is `labelRotatedHeight` in pixels plus `yOffset` converted from dp, so a large rotation angle costs vertical space.

## Labels from a list of names

The most common case: your entries are at x = 0, 1, 2, and you want a name under each one. `IndexAxisValueFormatter` takes the label at the rounded x value.

```kotlin
val months = listOf("Jan", "Feb", "Mar", "Apr", "May", "Jun")

chart.xAxis.apply {
    valueFormatter = IndexAxisValueFormatter(months)
    granularity = 1f
    labelCount = months.size
}
```

Granularity of 1 matters here. Without it, zooming in produces values like 2.4 and 2.6: from a fraction of 0.5 the formatter returns an empty string, and below that it returns the label of the rounded down index, which then sits at a tick it does not belong to.

## Dates and times

Keep the x value a number and format it in the axis. A timestamp in hours since the epoch works well, because the numbers stay small enough for a `Float`.

```kotlin
val format = SimpleDateFormat("dd MMM HH:mm", Locale.getDefault())

chart.xAxis.apply {
    granularity = 1f
    isCenterAxisLabelsEnabled = true
    valueFormatter = IAxisValueFormatter { value, _ ->
        format.format(Date(TimeUnit.HOURS.toMillis(value.toLong())))
    }
}
```

Build the `SimpleDateFormat` once, outside the lambda. The formatter runs for every label on every frame.

## One label per entry

Ask for as many labels as you have entries and stop the axis from inventing values between them.

```kotlin
chart.xAxis.apply {
    labelCount = entries.size
    granularity = 1f
}
```

`labelCount` is clamped to 25, so for longer series ask for fewer labels and let the formatter return an empty string for the values you want to skip.

## Padding at the edges

A line chart draws its first point exactly on the left edge and its last point on the right edge. A bar chart instead leaves half a slot at each side, because `BarChart`, `ScatterChart` and `CandleStickChart` set `spaceMin` and `spaceMax` to `0.5` on the x axis. For a line chart you pick the look you want by fixing the range. The example app shows both in its chart showcase.

Half a slot at each side, the way bars sit:

```kotlin
chart.xAxis.apply {
    axisMinimum = -0.5f
    axisMaximum = pointCount - 0.5f
    granularity = 1f
    labelCount = pointCount
}
```

Full width, the line touching both edges:

```kotlin
chart.xAxis.apply {
    axisMinimum = 0f
    axisMaximum = (pointCount - 1).toFloat()
    granularity = 1f
    labelCount = pointCount
    isAvoidFirstLastClippingEnabled = true
}
chart.setExtraOffsets(6f, 8f, 6f, 4f)
```

The second one needs the clipping guard, because the outer labels now sit right on the edges. A few pixels of extra offset keep the line itself from being cut in half by the view bounds.

> On a bar chart, `chart.isFitBarsEnabled = true` is a third option. It widens the range by half a bar width on each side on the next `notifyDataSetChanged()`, so the outer bars are fully visible whatever bar width you use.

## Other chart types

The `HorizontalBarChart` draws its x axis vertically, along the bars. You still address it as `chart.xAxis` and the entries still carry x values, only the drawing is rotated: `TOP` puts the labels on the right of the chart and `BOTTOM` on the left.

The radar chart uses the x axis for the labels around the web, one per entry index. `labelRotationAngle`, the text settings and the formatter work there. Positions, centering and limit lines do not.

## Next

- [The y axis](/mpandroidchart/docs/yaxis/) for the value side.
- [Formatting values](/mpandroidchart/docs/formatters/) for the formatters used above.
- [The axis](/mpandroidchart/docs/axis/) for the settings both axes share.
