# Jetpack Compose

The MPChartCompose module wraps every chart view in a composable, so you can pass data as state, read the selection back, and drive zoom and animation from Compose.

## Add the dependency

The Compose module is published next to the library and depends on it, so one line is enough:

```kotlin
dependencies {
    implementation("com.github.PhilJay.MPAndroidChart:MPChartCompose:v4.0.0-beta01")
}
```

It brings `MPChartLib`, the Compose BOM and `compose-ui` with it as `api` dependencies. The module needs `minSdk 23` and Compose enabled in your build file.

## Your first chart

Every chart type has a composable with the same name as the view. Give it data and a size, and configure the underlying view in `setup`:

```kotlin
val data = remember(entries) {
    LineData(LineDataSet(entries, "Revenue").apply { lineWidth = 2f })
}

LineChart(
    data = data,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    setup = {
        description.isEnabled = false
        axisRight.isEnabled = false
        xAxis.position = XAxis.XAxisPosition.BOTTOM
    },
)
```

The nine composables are `LineChart`, `BarChart`, `HorizontalBarChart`, `PieChart`, `RadarChart`, `ScatterChart`, `CandleStickChart`, `BubbleChart` and `CombinedChart`. Each one takes the data class of its view: `LineData`, `BarData`, `PieData` and so on. They all take the same parameters.

## The parameters

| Parameter | Meaning |
| --- | --- |
| `data` | The chart data, nullable. Passing null clears the chart and shows its no data text. |
| `modifier` | Applied to the chart, usually to give it a size. |
| `state` | A [ChartState](#chart-state) that reports selection and viewport back and lets you drive the chart. Defaults to a fresh `rememberChartState()`. |
| `contentDescription` | Text read by screen readers. Null adds no semantics. |
| `marker` | A composable drawn at the highlighted entry. Null for no marker. |
| `setup` | Runs once, on the view, right after it is created and before any data is set. |
| `update` | Runs on the view before every redraw that Compose triggers. |

### New instance versus same instance

The composable compares `data` by identity. A **new** instance is assigned to the chart, which recalculates the axes, the legend and the offsets and redraws. The **same** instance is left alone, even when you changed entries inside it. After changing data in place, tell the chart yourself:

```kotlin
lineSet.addEntry(Entry(x, y))
state.notifyDataChanged()
```

Wrapping the data in `remember` keyed on what it is built from is the simplest way to get a new instance exactly when you want one.

### setup runs once, update runs again

`setup` runs a single time, when the view is created. Whatever it reads is frozen at that moment, so theme colors or anything else that changes do not belong there. Put those in `update`:

```kotlin
val labelColor = MaterialTheme.colorScheme.onSurface.toArgb()

BarChart(
    data = barData,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    setup = {
        description.isEnabled = false
        isDrawGridBackgroundEnabled = false
    },
    update = {
        xAxis.textColor = labelColor
        axisLeft.textColor = labelColor
    },
)
```

`update` runs when `data`, `state`, `contentDescription`, `marker` or the lambda itself change. The lambda captures the Compose values it reads, so reading `labelColor` above makes it a different lambda whenever the theme changes, which is what re-runs it. The composable calls `invalidate()` after `update`, so you do not need to.

> `setup` and `update` have the chart view as their receiver. Everything in the [general styling](/mpandroidchart/docs/general-styling/) and [axis](/mpandroidchart/docs/axis/) chapters works inside them unchanged.

## Chart state

`rememberChartState()` creates a `ChartState`. Pass it to one chart composable and it observes that chart: it reports what the user selected and where the viewport is, and its functions drive the chart back.

```kotlin
val state = rememberChartState()

LineChart(
    data = lineData,
    state = state,
    modifier = Modifier.fillMaxWidth().height(220.dp),
)

Text(state.selectedEntry?.let { "Selected ${it.y}" } ?: "Tap a point")
Row {
    Button(onClick = { state.zoomIn() }) { Text("Zoom in") }
    Button(onClick = { state.fitScreen() }) { Text("Fit") }
}
```

These properties are read-only and update themselves:

| Property | Meaning | Default |
| --- | --- | --- |
| `selectedEntry` | The highlighted entry, null while nothing is highlighted. Every chart type updates it. | null |
| `selectedHighlight` | The `Highlight` of that entry, with its data set, data and stack index. | null |
| `lowestVisibleX` | Lowest x value visible, in value space. | 0 |
| `highestVisibleX` | Highest x value visible, in value space. | 0 |
| `zoomX` | Horizontal zoom factor, 1 when not zoomed. | 1 |
| `zoomY` | Vertical zoom factor, 1 when not zoomed. | 1 |
| `rotationAngle` | Rotation in degrees clockwise from 3 o'clock. Only pie and radar charts update it. | 270 |
| `isAttached` | False until the chart composable has created its view, and again after it left the composition. | false |

The four viewport properties only move for line, bar, scatter, candle, bubble and combined charts. The other types leave them at their defaults.

And these functions drive the chart:

| Function | What it does |
| --- | --- |
| `highlight(x, dataSetIndex = 0)` | Highlights the entry closest to `x` in that data set, as if the user had tapped it. Clears the selection when the index is out of range or nothing is near `x`. |
| `clearHighlight()` | Removes the highlight and sets both selection properties to null. |
| `notifyDataChanged()` | Recomputes axes, legend and offsets, redraws, then refreshes the viewport properties. Call it after changing data in place. |
| `animateX(durationMillis, easing)` | Animates the drawing along the x axis. |
| `animateY(durationMillis, easing)` | Animates the drawing along the y axis. |
| `animateXY(durationMillisX, durationMillisY, easingX, easingY)` | Animates both axes at once. `easingY` defaults to `easingX`. |
| `fitScreen()` | Resets zoom and scroll so all data is visible. |
| `zoomIn()` | Zooms in by a factor of 1.4 around the center of the content area. |
| `zoomOut()` | Zooms out by a factor of 0.7 around the center. |
| `resetZoom()` | Resets the zoom to 1 without moving the scroll position. |
| `moveViewToX(xValue)` | Scrolls so `xValue` sits at the left edge, keeping the zoom. |

Every easing parameter defaults to `Easing.Linear`, except `easingY`, which follows `easingX`; the [animations](/mpandroidchart/docs/animations/) chapter lists the curves. The five viewport functions only affect line, bar, scatter, candle, bubble and combined charts, and the viewport properties catch up after the next layout pass.

All members are main thread only, and every function quietly does nothing while `isAttached` is false. That makes it safe to call one from a `LaunchedEffect` that may run before the view exists:

```kotlin
LaunchedEffect(lineData) { state.animateX(600) }
```

### It survives configuration changes

`rememberChartState` uses `rememberSaveable`, so zoom, scroll position, rotation and the highlighted entry come back after a rotation or process death. The saved values are applied once the restored state is attached to a chart that has its data and its size.

> One state belongs to one chart. Attaching the same `ChartState` to a second chart throws `IllegalStateException`. Call `rememberChartState()` once per chart.

Listeners you set on the chart view yourself keep working. The state adds its own listeners alongside them rather than replacing them.

## Markers

The `marker` parameter takes a composable that receives the highlighted entry and its highlight:

```kotlin
LineChart(
    data = lineData,
    state = state,
    marker = { entry, _ ->
        Surface(color = Color(0xFF1B1F3B), shape = RoundedCornerShape(8.dp)) {
            Text(
                "${entry.y.roundToInt()}",
                color = Color.White,
                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
            )
        }
    },
)
```

The content is composed in an invisible `ComposeView` that lives as a child of the chart, and the chart draws that view at the highlighted position. By default the marker is centered above the entry, with 12 dp of space, and it is pushed back inside the chart bounds when it would stick out.

Content for a newly highlighted entry composes on the next frame, so the marker appears one frame after the highlight. Changing the composable you pass recomposes the marker without recreating it.

If you want a composable marker on a chart view outside Compose, create a `ComposeMarker(chart, content)` and assign it to `chart.marker`. Call `detach()` when the chart should drop it; that removes the view and unsets the marker. `setOffset(x, y)` shifts the content by that many pixels from its default position. The chart composables create and release one for you.

## Compose colors, fonts and painters

The library takes ARGB ints, `Typeface` and `Drawable`. The module has small helpers that bridge the gap.

| Helper | Use |
| --- | --- |
| `BaseDataSet.setColors(List<Color>)` | Sets the colors a data set cycles through for its entries. |
| `LineDataSet.setCircleColors(List<Color>)` | Sets the colors of the circles drawn at each point. |
| `List<Int>.toComposeColors()` | Turns ARGB ints, such as `ColorTemplate.MATERIAL_COLORS`, into Compose colors. |
| `rememberTypeface(fontFamily, fontWeight, fontStyle)` | Resolves a Compose font to the `Typeface` that axes, the legend and other components take. |
| `rememberDrawable(painter, size)` | Draws a painter into a bitmap of that dp size and returns it as a `Drawable`, ready to use as an entry icon. |

For a single color there is no helper, just use `toArgb()`:

```kotlin
val set = LineDataSet(entries, "Revenue").apply {
    color = MaterialTheme.colorScheme.primary.toArgb()
    setCircleColors(listOf(Color(0xFF3DDC97), Color(0xFF7C6CF5)))
}
```

`rememberTypeface` re-resolves only when the family, weight, style or the font resolver change. `rememberDrawable` re-draws only when the painter, size, density or layout direction change, and the bitmap it makes is at least 1 by 1 px.

```kotlin
val typeface = rememberTypeface(FontFamily.SansSerif, FontWeight.Medium)

PieChart(
    data = pieData,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    update = {
        legend.typeface = typeface
        entryLabelTypeface = typeface
    },
)
```

## Previews

A chart view needs a real display, so it cannot render inside the Android Studio preview pane. Instead of failing, the composables detect the inspection mode and draw a placeholder: a framed box with a sample line and a label naming the chart type, in light or dark to match the preview. The `modifier` and `contentDescription` you passed still apply, so the placeholder occupies the same space the chart will. Run the app to see the real thing.

## A complete screen

This puts the pieces together: data in `remember`, styling split between `setup` and `update`, a marker, and buttons that drive the chart through the state.

```kotlin
private val months = listOf("Jan", "Feb", "Mar", "Apr", "May", "Jun")

@Composable
fun RevenueCard() {
    var seed by remember { mutableIntStateOf(0) }
    val set = remember(seed) { revenueSet(seed) }
    val data = remember(set) { LineData(set) }
    var pointCount by remember(set) { mutableIntStateOf(set.entryCount) }
    val state = rememberChartState()
    val gridColor = MaterialTheme.colorScheme.outlineVariant.toArgb()

    LaunchedEffect(data) { state.animateX(600) }

    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        LineChart(
            data = data,
            modifier = Modifier.fillMaxWidth().height(220.dp),
            state = state,
            contentDescription = "Revenue per month",
            marker = { entry, _ -> Text("${entry.y.roundToInt()}") },
            setup = {
                description.isEnabled = false
                axisRight.isEnabled = false
                xAxis.position = XAxis.XAxisPosition.BOTTOM
                xAxis.valueFormatter = IAxisValueFormatter { value, _ ->
                    months[value.toInt() % months.size]
                }
                xAxis.granularity = 1f
                axisLeft.axisMinimum = 0f
            },
            update = {
                xAxis.gridColor = gridColor
                axisLeft.gridColor = gridColor
                xAxis.axisMaximum = pointCount - 0.5f
                notifyDataSetChanged()
            },
        )

        val selected = state.selectedEntry
        Text(selected?.let { "Selected: ${it.y.roundToInt()}" } ?: "Tap a point")

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = {
                val next = nextValue(set.entries.last().y)
                set.addEntry(Entry(pointCount.toFloat(), next))
                pointCount++
                state.highlight(pointCount - 1f)
            }) { Text("Add point") }

            Button(onClick = { seed++ }) { Text("New data") }
        }
    }
}
```

"Add point" changes the data set in place, so the same `LineData` instance stays on the chart. `pointCount` changes, which makes `update` a new lambda, and the `notifyDataSetChanged()` in there picks the new entry up. "New data" bumps the seed, which builds a fresh `LineData`, and the composable assigns it because it is a different instance.

The `ComposeChartActivity` in the example app runs this pattern with a line, a pie and a bar chart on one screen.

## Where to go next

- [Markers](/mpandroidchart/docs/markers/) for the view based `MarkerView` and the `IMarker` interface.
- [Interaction with the chart](/mpandroidchart/docs/interaction/) for the gestures the state observes.
- [Animations](/mpandroidchart/docs/animations/) for the easing curves.
- [Charts in lists and scrolling screens](/mpandroidchart/docs/lists-and-scrolling/) for a chart inside a `LazyColumn`.
- [MPChartCompose API reference](https://jitpack.io/com/github/PhilJay/MPAndroidChart/MPChartCompose/v4.0.0-beta01/javadoc/)
