# Accessibility

What a screen reader can and cannot get from a chart, and the things you can do about it.

## What a chart exposes today

A chart is a single `ViewGroup` that paints everything onto a canvas. The axis labels, the value labels, the legend and the description are drawn text, not child views. A marker is drawn the same way: a `MarkerView` is inflated but never added to the chart, and a Compose marker lives in an invisible child view that the chart draws itself.

So a screen reader finds one element where you see a chart, and nothing inside it.

The library adds nothing on top of that. Nothing in the sources sets a content description, builds an accessibility node tree, marks the chart focusable or sends an announcement. The chart also never calls `performClick()`, so a tap on a value produces no accessibility click event. Everything below is you doing the work, not a feature being switched on.

## Write a description worth hearing

The useful description is a summary, not a reading of the data. Nobody wants to hear sixty numbers. Name what is being shown, how many points there are, the range, and the shape:

```kotlin
fun describe(data: LineData): String {
    val set = data.getDataSetByIndex(0) ?: return "Chart with no data"
    if (set.entryCount == 0) return "${set.label}, line chart, no points"
    val first = set.getEntryForIndex(0).y
    val last = set.getEntryForIndex(set.entryCount - 1).y
    val trend = when {
        last > first -> "rising"
        last < first -> "falling"
        else -> "flat"
    }
    return "${set.label}, line chart, ${set.entryCount} points, " +
        "$trend from ${first.toInt()} to ${last.toInt()}, " +
        "lowest ${set.yMin.toInt()}, highest ${set.yMax.toInt()}"
}
```

Say the chart type, because "line chart" tells someone how to read the rest. With several series, name each one and give it its own range instead of merging them into one number.

## Set it from Compose

Every chart composable takes a `contentDescription`. Null, the default, adds nothing at all.

```kotlin
val data = remember(entries) { lineDataFor(entries) }

LineChart(
    data = data,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    contentDescription = remember(data) { describe(data) },
)
```

The wrapper puts the text into a `semantics` modifier on the chart and also assigns it to the view's `contentDescription`. It is part of the update path, so a new description is applied on the next recomposition. Remember it keyed on the data, as above, and it changes exactly when the numbers change and never on an unrelated recomposition.

## Set it from a view

`contentDescription` is the ordinary `View` property, so set it wherever you set the data:

```kotlin
chart.data = lineData
chart.contentDescription = describe(lineData)
```

A selection is a change the user made, so say it out loud. The value selected listener is the place:

```kotlin
chart.onValueSelected(
    onNothingSelected = { chart.announceForAccessibility("Selection cleared") },
) { entry, highlight ->
    val label = chart.data?.getDataSetByIndex(highlight.dataSetIndex)?.label
    chart.announceForAccessibility("$label, ${entry.x}: ${entry.y}")
}
```

`announceForAccessibility` speaks the text once and leaves nothing behind, which fits a selection. Do not use it for the whole summary, that belongs in `contentDescription`.

## Give the numbers another way

A summary is an improvement, not equal access. If the chart carries information someone needs, put that information somewhere reachable as well: a table or a list of rows next to the chart, built from the same data sets, each row a label and a value. It can sit under the chart, behind a "show values" toggle, or on its own screen.

This is the part that actually makes the data available, and it needs no library support. Everything else on this page only makes the picture easier to live with.

## Color

Charts are almost always read by color, so the colors carry meaning.

- Check the contrast of lines, bars and text against the background the chart really has. `isDrawGridBackgroundEnabled` is false by default, so the chart draws onto whatever is behind the view, not onto `gridBackgroundColor`.
- Never let color be the only difference between two series. Someone who cannot tell your two blues apart has no way back to the legend.
- Add a second signal. `ScatterDataSet.setScatterShape` gives each set its own shape. `LineDataSet.enableDashedLine(lineLength, spaceLength, phase)` makes one line dashed. Different circle radii, value labels on the important series and entry icons all work too.
- On the charts with axes the highlight lines are drawn in the data set's `highlightColor`, which defaults to a light orange. Check that it stands out against the series it crosses.

See [Colors](/mpandroidchart/docs/colors/) for how colors are assigned across entries.

## Text size

Every text size in the library is in dp and is converted with the display density alone. The system font scale is never applied, so a user who has set large text gets the same 10 dp axis labels as everyone else.

If that matters for your app, scale the sizes yourself:

```kotlin
val fontScale = resources.configuration.fontScale
chart.xAxis.textSize = 10f * fontScale
chart.axisLeft.textSize = 10f * fontScale
chart.legend.textSize = 10f * fontScale
```

In Compose read `LocalDensity.current.fontScale` and apply it in `update` so it follows a settings change.

Two limits are worth knowing. Axis, legend, limit line and description sizes are clamped to 6 until 24 dp, so the value you assign may not be the value you get. Value label sizes, `valueTextSize` on a data set, default to 7 dp and are not clamped, which makes 7 dp the smallest text on most charts and the first thing to raise.

## Touch and selection

Selection has no touch targets, only distances. On the charts with axes, a tap selects the closest value within `maxHighlightDistance`, which defaults to 500 dp and so accepts almost any tap. Bar charts compare the horizontal distance only, so a tap anywhere above or below a bar selects it, and a horizontal bar chart compares the vertical distance. Pie and radar charts ignore the distance and select by the angle of the touch, as long as it lands inside the radius.

A low `maxHighlightDistance` means a tap that misses selects nothing at all, which is a hard thing to recover from without seeing the chart. Leave it high, and prefer `isHighlightPerTapEnabled` over dragging, since a drag is harder to place precisely.

Keep the chart big. A 200 dp row is easier to hit than a 100 dp one, and the accuracy of every selection depends on the size of the view.

## Checklist

- Give every chart a `contentDescription` that names the chart type, the series, the range and the trend.
- Update the description when the data changes, not once at setup.
- Announce a selection from the value selected listener.
- Offer the same numbers as text somewhere, for anything the user actually needs.
- Check contrast against the real background, including highlight colors.
- Give each series a shape, a dash or a label as well as a color.
- Scale text sizes by the system font scale if your app respects it, and raise `valueTextSize` from its 7 dp default.
- Give the chart enough height that a tap lands where the user meant it.
