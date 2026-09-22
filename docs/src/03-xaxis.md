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

```figure
<svg viewBox="0 0 760 208" width="100%" role="img" aria-label="Where the x axis labels are drawn for each position" style="max-width:760px;height:auto;display:block;margin:0 auto 6px">
<title>Where the x axis labels are drawn for each position</title>
<rect x="2.0" y="52.0" width="124.0" height="96.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M2.0 115.4 L22.7 98.5 L43.3 109.2 L64.0 83.1 L84.7 96.2 L105.3 72.4 L126.0 89.2" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<text x="33.0" y="44.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">5</text>
<text x="64.0" y="44.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">10</text>
<text x="95.0" y="44.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">15</text>
<text x="64.0" y="186.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">TOP</text>
<rect x="160.0" y="52.0" width="124.0" height="96.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M160.0 115.4 L180.7 98.5 L201.3 109.2 L222.0 83.1 L242.7 96.2 L263.3 72.4 L284.0 89.2" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<text x="191.0" y="163.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">5</text>
<text x="222.0" y="163.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">10</text>
<text x="253.0" y="163.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">15</text>
<text x="222.0" y="186.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">BOTTOM</text>
<rect x="318.0" y="52.0" width="124.0" height="96.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M318.0 115.4 L338.7 98.5 L359.3 109.2 L380.0 83.1 L400.7 96.2 L421.3 72.4 L442.0 89.2" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<text x="349.0" y="44.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">5</text>
<text x="349.0" y="163.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">5</text>
<text x="380.0" y="44.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">10</text>
<text x="380.0" y="163.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">10</text>
<text x="411.0" y="44.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">15</text>
<text x="411.0" y="163.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">15</text>
<text x="380.0" y="186.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">BOTH_SIDED</text>
<rect x="476.0" y="52.0" width="124.0" height="96.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M476.0 115.4 L496.7 98.5 L517.3 109.2 L538.0 83.1 L558.7 96.2 L579.3 72.4 L600.0 89.2" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<text x="507.0" y="66.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">5</text>
<text x="538.0" y="66.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">10</text>
<text x="569.0" y="66.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">15</text>
<text x="538.0" y="186.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">TOP_INSIDE</text>
<rect x="634.0" y="52.0" width="124.0" height="96.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M634.0 115.4 L654.7 98.5 L675.3 109.2 L696.0 83.1 L716.7 96.2 L737.3 72.4 L758.0 89.2" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<text x="665.0" y="142.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">5</text>
<text x="696.0" y="142.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">10</text>
<text x="727.0" y="142.0" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">15</text>
<text x="696.0" y="186.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">BOTTOM_INSIDE</text>
<text x="64.0" y="24.0" fill="#00a9ab" font-size="11" text-anchor="middle">the default</text>
</svg>
```

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
