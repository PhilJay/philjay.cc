# Theming a chart

How to keep one look for every chart in your app in a palette object and a few extension functions, and how to switch it between dark and light.

Styling one chart is covered in [General styling](/mpandroidchart/docs/general-styling/), [Chart specific styling](/mpandroidchart/docs/chart-styling/), [The legend](/mpandroidchart/docs/legend/) and [The description](/mpandroidchart/docs/description/). This chapter is about doing it once instead of on every screen.

The library has no idea of a theme. There is no theme class, no style attribute and nothing to register: a theme is ordinary code in your app that sets the properties those chapters describe. What follows is a pattern, not an API. The example app ships one theme called Nightfall in `com.xxmassdeveloper.mpchartexample.design`, every chart screenshot on this site is drawn by it, and the code below is that theme. Swap the colors, the fonts and the shapes for your own and the pattern carries any look you like.

## The shape of a theme

A theme is two files. `Nightfall.kt` holds the colors and nothing else: no views, no chart code. `NightfallStyle.kt` holds extension functions, one on the chart and one per data set type. Nothing else in the app sets a chart color. A screen picks the variant and applies the base:

```kotlin
val theme = if (isSystemInDarkTheme()) Nightfall.dark else Nightfall.light

LineChart(
    data = revenue,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    update = { nightfallBase(theme) },
)
```

It goes in `update`, not in `setup`. `setup` runs once and freezes what it reads, so a palette that can change belongs in `update`, which runs again whenever the lambda captures a new value. Write the functions so that running them twice is harmless, which plain assignments are. Outside Compose the same function runs on the view: `LineChart(context).apply { nightfallBase(theme) }`.

## The palette

One class, two instances. The fields are named after their job, never after their color, so the same chart code reads both variants without ever asking which one it got.

```kotlin
class Nightfall private constructor(
    val stage: Int, val card: Int, val text: Int, val muted: Int,
    val grid: Int, val track: Int, val pillBackground: Int, val pillText: Int,
) {
    companion object {
        val palette = listOf(0xFF2FB4B6, 0xFFF97066, 0xFFF5B041, 0xFF8B7CF6, 0xFF5DD39E)
            .map { it.toInt() }
        val accent = palette[0]
        val dark = Nightfall(
            stage = 0xFF0F172A.toInt(), card = 0xFF111C33.toInt(),
            text = 0xFFE2E8F0.toInt(), muted = 0xFF94A3B8.toInt(),
            grid = Color.argb(36, 148, 163, 184),
            track = Color.argb(26, 148, 163, 184),
            pillBackground = 0xFFE2E8F0.toInt(), pillText = 0xFF0F172A.toInt(),
        )
        val light = Nightfall(
            stage = 0xFFF8FAFC.toInt(), card = 0xFFFFFFFF.toInt(),
            text = 0xFF0F172A.toInt(), muted = 0xFF64748B.toInt(),
            grid = 0xFFE2E8F0.toInt(), track = 0xFFEEF2F7.toInt(),
            pillBackground = 0xFF0F172A.toInt(), pillText = 0xFFFFFFFF.toInt(),
        )
        fun withAlpha(color: Int, alpha: Int): Int =
            Color.argb(alpha, Color.red(color), Color.green(color), Color.blue(color))
    }
}
```

Five accents in a fixed order, so a chart with several series always picks the same colors in the same sequence; `coral`, `amber`, `violet` and `green` name the other four the same way. The accents are shared between the two variants, because they read on a dark and on a light surface alike. Only the surfaces and the text tones differ.

`stage` is the screen behind the card, `card` the surface the chart sits on, which the donut hole and the circle holes of a line have to match. `text` is for values and center text, `muted` for axis labels, and `grid` and `track` are the muted tone at low alpha. `withAlpha` earns its place in the palette because gradient fills, bar highlights and translucent bubbles are all accents at a lower alpha, and you do not want `Color.argb` spelled out at every call site.

## The base every chart shares

One extension on `Chart<*>` covers what every chart in the theme has in common, and narrows to `BarLineChartBase<*>` for the axis part:

```kotlin
fun Chart<*>.nightfallBase(theme: Nightfall) {
    description.isEnabled = false
    legend.isEnabled = false
    noDataText = "Nothing to show yet"
    noDataTextColor = theme.muted
    if (this is BarLineChartBase<*>) {
        isDrawGridBackgroundEnabled = false
        setExtraOffsets(0f, 8f, 8f, 4f)
        xAxis.position = XAxis.XAxisPosition.BOTTOM
        xAxis.isDrawGridLinesEnabled = false
        xAxis.yOffset = 8f
        axisLeft.isDrawGridLinesEnabled = true
        axisLeft.gridColor = theme.grid
        axisLeft.gridLineWidth = 1f
        axisLeft.xOffset = 10f
        axisRight.isEnabled = false
        nightfallAxes(theme)
    }
}
```

The description is off everywhere, because a card already has a title above the chart. The legend is off here and switched back on only where the theme needs it, on the donut and the radar. The grid background is off by default, so that line only writes the decision down. Only the left axis draws grid lines, which gives horizontal rules and no vertical ones. The extra offsets keep a rounded bar or a thick line from being clipped at the edges, and `yOffset` and `xOffset` push the labels away from the plot.

## Styling the axes

The label look is the same on both axes, so it is one loop:

```kotlin
fun BarLineChartBase<*>.nightfallAxes(theme: Nightfall) {
    for (axis in listOf(xAxis, axisLeft)) {
        axis.isDrawAxisLineEnabled = false
        axis.textColor = theme.muted
        axis.textSize = 10f
    }
}
```

These are the properties that carry a theme. All of them sit on `AxisBase`, so they behave the same on the x axis and on both y axes.

| Property | Use in a theme | Default |
| --- | --- | --- |
| `textColor` | The muted tone, so labels sit behind the data | black |
| `textSize` | 10 or 11, clamped to 6 to 24 | `10` |
| `isDrawAxisLineEnabled` | `false` drops the line along the axis | `true` |
| `isDrawGridLinesEnabled` | Left axis only, for horizontal rules | `true` |
| `gridColor`, `gridLineWidth` | The translucent grid tone, `1f` | gray, `0.5` |
| `enableGridDashedLine(length, space, phase)` | Dashed rules instead of solid | solid |
| `labelCount` with `isForceLabelsEnabled` | Exactly as many rows as the design wants | `6`, `false` |
| `granularity` | Smallest step between labels, `1f` for whole slots | `1`, off |

`labelCount` alone is a wish: the axis rounds the interval to a nice value and the real count only comes close. With `isForceLabelsEnabled = true` you get exactly that many labels, evenly spread, which is what a card with four grid rules needs. Assigning `granularity` also sets `isGranularityEnabled`, so you never set both.

Two x axis variants cover almost every card. The padded one leaves half a slot at each end, the way bars sit. The full width one pushes the first and last point onto the edges:

```kotlin
fun BarLineChartBase<*>.nightfallPaddedX(pointCount: Int) {
    xAxis.axisMinimum = -0.5f
    xAxis.axisMaximum = pointCount - 0.5f
    xAxis.granularity = 1f
    xAxis.labelCount = pointCount
}

fun BarLineChartBase<*>.nightfallFullWidthX(pointCount: Int) {
    xAxis.axisMinimum = 0f
    xAxis.axisMaximum = (pointCount - 1).toFloat()
    xAxis.granularity = 1f
    xAxis.labelCount = pointCount
    xAxis.isAvoidFirstLastClippingEnabled = true
    setExtraOffsets(6f, 8f, 6f, 4f)
}
```

`isAvoidFirstLastClippingEnabled` pulls the outermost labels back inside the view, and the extra side offsets keep a 3 dp line from being cut in half at the edges.

> `labelCount` is clamped to `axisMinLabels`..`axisMaxLabels`, which is 2 to 25. A full width axis with more than 25 points needs a smaller count and a formatter that returns an empty string in between.

## Touches per chart type

The rest of the theme is one small extension per data set type. Bars get rounded corners and a vertical gradient per bar, built from the `Fill` list:

```kotlin
fun BarDataSet<*>.nightfallBars(barColor: Int = Nightfall.accent) {
    barCornerRadius = 7f
    isDrawValuesEnabled = false
    highlightAlpha = 0
    fills = entries.indices.map {
        Fill(barColor, Nightfall.withAlpha(barColor, 90))
    }.toMutableList()
}
```

One `Fill` per bar means you can hand the selected one its own color instead, which is how the orders card marks a quarter. `highlightAlpha = 0` removes the pale block the library draws over a selected bar, which is right when the selection already shows as its own color and a marker. Setting `barShadowColor = theme.track` on the set and `isDrawBarShadowEnabled = true` on the chart paints the empty rest of each slot, which is how the budget card gets its tracks.

A line gets a fading area below it. The fill is an ordinary `GradientDrawable`, from the line color at alpha 115 down to fully transparent:

```kotlin
fun LineDataSet<*>.nightfallLine(theme: Nightfall, lineColor: Int = Nightfall.accent) {
    mode = LineDataSet.Mode.CUBIC_BEZIER
    cubicIntensity = 0.18f
    color = lineColor
    lineWidth = 3f
    isDrawCirclesEnabled = false
    isDrawValuesEnabled = false
    isDrawFilledEnabled = true
    fillDrawable = GradientDrawable(
        GradientDrawable.Orientation.TOP_BOTTOM,
        intArrayOf(
            Nightfall.withAlpha(lineColor, 115),
            Nightfall.withAlpha(lineColor, 0),
        ),
    )
    highlightColor = lineColor
    enableDashedHighlightLine(8f, 8f, 0f)
    isHorizontalHighlightIndicatorEnabled = false
    isDrawHighlightCircleEnabled = true
    circleHoleColor = theme.card
}
```

The guide under the selected point is dashed and the horizontal one is off, so the eye follows the x value. `circleHoleColor = theme.card` is why this function needs the palette at all: the ring around the selected point has to match the surface the chart sits on.

The pie is a donut with a wide hole in the card color, no labels on the slices and the legend switched back on:

```kotlin
PieChart(data = platforms, modifier = cardSize, update = {
    nightfallBase(theme)
    isDrawEntryLabelsEnabled = false
    holeRadius = 72f
    transparentCircleRadius = 0f
    holeColor = theme.card
    isDrawRoundedSlicesEnabled = true
    centerText = "44%\nMobile"
    centerTextColor = theme.text
    centerTextSize = 11f
    legend.isEnabled = true
    legend.textColor = theme.text
    legend.orientation = Legend.LegendOrientation.VERTICAL
    legend.verticalAlignment = Legend.LegendVerticalAlignment.CENTER
    legend.horizontalAlignment = Legend.LegendHorizontalAlignment.RIGHT
    setExtraOffsets(0f, 0f, 24f, 0f)
})
```

`transparentCircleRadius = 0f` removes the pale ring the chart otherwise draws around the hole, which would break the flat surface, and the extra right offset makes room for the legend column. On the data set, `sliceSpace = 3f` cuts the gaps between slices and `colors = Nightfall.palette.take(entryCount)` hands out the accents in order.

A radar chart hangs its look on the web instead of a grid. Put `webColor` and `webColorInner` on the muted tone, both widths on `1f`, and fade the whole web behind the data with `webAlpha = 40`, which applies to both colors at once. Then drop the y labels with `yAxis.isDrawLabelsEnabled = false` and give each set `fillAlpha = 56` over its `fillColor`, so two overlapping shapes stay readable.

## A themed marker

The marker is part of the look, so the palette carries its two colors. In Compose it is a composable, which makes it the smallest piece of the theme:

```kotlin
marker = { entry, _ ->
    Surface(color = Color(theme.pillBackground), shape = RoundedCornerShape(8.dp)) {
        Text(
            entry.y.roundToInt().toString(),
            color = Color(theme.pillText),
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
        )
    }
},
```

The design screen in the example app is built from views, so it uses `PillMarkerView` instead: a `MarkerView` that inflates a layout with one `TextView`, gives it a rounded `GradientDrawable` in `theme.pillBackground` and text in `theme.pillText`, and takes the label as a `(Entry<*>) -> String` lambda so that one class serves every card. It overrides `offset` to center itself above the entry with 14 dp of air. [Markers](/mpandroidchart/docs/markers/) covers that override and the rest of the marker API.

## Dark mode and Material 3

The line that picks the variant reads `isSystemInDarkTheme()`, so it recomposes by itself when the system theme flips. Wrap it in a `@Composable fun rememberNightfall(): Nightfall` and no screen has to think about it again.

If your colors come from Material 3 rather than a hand written palette, read the scheme and convert. The library takes ARGB ints, and `toArgb()` on a Compose color is all it takes: `axisLeft.gridColor = MaterialTheme.colorScheme.outlineVariant.toArgb()`. For lists there are two extensions in the `MPChartCompose` module, so Compose colors reach the data set unconverted:

```kotlin
val set = LineDataSet(entries, "Revenue").apply {
    setColors(listOf(MaterialTheme.colorScheme.primary))
    setCircleColors(listOf(MaterialTheme.colorScheme.primary))
}
```

`setColors` takes the list the set cycles through for its entries, `setCircleColors` the circles of a line, and both run `toArgb()` over the list; import them from `com.github.mikephil.charting.compose`. For a single color there is no helper and none is needed: `color = myColor.toArgb()`.

Every one of these reads a Compose value, so they belong in `update`. A chart whose colors are set in `setup` keeps the palette it was built with and turns unreadable the moment the system switches to dark. A view based screen gets the switch for free, because a night mode change recreates the activity and your `onCreate` picks the variant again.

## Fonts

A `Typeface` is loaded once and handed to each component that draws text. In Compose, `rememberTypeface(FontFamily.SansSerif, FontWeight.Medium)` resolves a Compose font to one. Outside Compose, load it with `Typeface.createFromAsset(context.assets, "OpenSans-Regular.ttf")` or from `res/font`, and keep it in a field rather than building it per chart.

Either way, one more extension spreads it over the chart. There is no single font property, each component owns its own:

```kotlin
fun Chart<*>.nightfallFont(typeface: Typeface) {
    description.typeface = typeface
    legend.typeface = typeface
    xAxis.typeface = typeface
    noDataTextTypeface = typeface
    data?.setValueTypeface(typeface)
    if (this is BarLineChartBase<*>) {
        axisLeft.typeface = typeface
        axisRight.typeface = typeface
    }
}
```

Call it next to the base, in `update = { nightfallBase(theme); nightfallFont(typeface) }`. `data?.setValueTypeface(typeface)` walks the data sets and sets `valueTypeface` on each, so it only reaches sets that are on the chart already, which is why it belongs in `update` and not in `setup`. A pie chart has two more of its own: `entryLabelTypeface` for the slice labels and `centerTextTypeface` for the center text.

## Make it your own

Nothing above is special to Nightfall. Replace the palette with your brand colors, or read them from `MaterialTheme.colorScheme` so the charts follow the rest of your app, and rename the extensions after your own theme. The parts worth keeping are the shape rather than the values:

- One palette type with an instance per variant, and fields named after their job rather than their color, so the same chart code renders both.
- One extension per thing you style: the chart, each data set type, and the pieces that differ per chart type.
- Everything called from `update` rather than `setup`, so a theme change reaches charts that already exist.
- No color anywhere else in the app. When every screen goes through these functions, changing the look is one file.
