# The fill formatter

How a line data set decides where its filled area ends, what the default does, and how to fill to zero, to an axis edge or to a value of your own.

A filled line chart shades the area between the line and something below or above it. `IFillFormatter` is what names that something: it returns one y value, in value space, and the fill runs from the line down or up to it.

## Turn the fill on

The fill is off by default. Three properties on a line data set control how it looks.

```kotlin
val set = LineDataSet(entries, "Revenue").apply {
    isDrawFilledEnabled = true
    fillColor = Color.BLUE
    fillAlpha = 85          // 0 to 255, the default
}
```

| Property | Default | Meaning |
| --- | --- | --- |
| `isDrawFilledEnabled` | `false` | whether the area is drawn at all |
| `fillColor` | light blue | the fill color; assigning it clears `fillDrawable` |
| `fillDrawable` | `null` | a `Drawable`, usually a gradient; takes precedence over `fillColor` |
| `fillAlpha` | 85 | opacity of `fillColor`, ignored when a drawable is used |
| `fillFormatter` | `DefaultFillFormatter()` | the y value the fill reaches |

A gradient is the nicer option and is what the example app's design charts use:

```kotlin
set.fillDrawable = GradientDrawable(
    GradientDrawable.Orientation.TOP_BOTTOM,
    intArrayOf(Color.argb(115, 92, 128, 255), Color.argb(0, 92, 128, 255))
)
```

## What the default does

`DefaultFillFormatter` is set on every `LineDataSet` unless you replace it. Its rule, in order:

1. If the data set itself has values above and below zero, the fill stops at **zero**, so the part above the axis fills down to it and the part below fills up to it.
2. Otherwise, a data set whose values are all at or above zero fills **down**: to zero when any line in the chart goes negative, and to the chart's `yChartMin` when none does.
3. A data set whose values are all at or below zero fills **up**: to zero when any line in the chart goes positive, and to the chart's `yChartMax` when none does.

With no line data at all it returns 0.

The effect is that a normal positive series fills down to the bottom of the chart, a series that crosses zero fills to the zero line, and you rarely have to think about it.

## Write your own

`IFillFormatter` is a `fun interface`, so a lambda is all it takes.

```kotlin
set.fillFormatter = IFillFormatter { _, _ -> 0f }
```

That one always fills to the zero line, whatever the data does. The two parameters are the data set being drawn and the chart drawing it, so a formatter can look at either:

```kotlin
set.fillFormatter = IFillFormatter { dataSet, provider ->
    provider.getAxis(dataSet.axisDependency).axisMinimum
}
```

This fills to the bottom edge of whichever y axis the data set belongs to, which is the most common custom choice: it keeps the shaded area anchored to the axis even when the data never comes near zero. The provider is a `LineDataProvider` and gives you `lineData`, `yChartMin`, `yChartMax` and `getAxis(axis)`.

A formatter that answers with the data set's own minimum shades only the band the series moves through:

```kotlin
set.fillFormatter = IFillFormatter { dataSet, _ -> dataSet.yMin }
```

The formatter is asked once per filled path, not once per point, so it must not depend on which entry is being drawn.

> The return value is a single y value, so the boundary of a fill is always a horizontal line. There is no way to fill along another curve.

## Fill between two lines

Because the boundary is horizontal, a band between two series is drawn the other way round: color the background, then paint over the parts that should not be visible. The example app's `FilledLineActivity` does exactly this.

```kotlin
chart.isDrawGridBackgroundEnabled = true
chart.gridBackgroundColor = Color.argb(150, 51, 181, 229)   // the band color

val lower = LineDataSet(lowerValues, "Lower").apply {
    isDrawFilledEnabled = true
    isDrawCirclesEnabled = false
    fillColor = Color.WHITE
    fillAlpha = 255
    fillFormatter = IFillFormatter { _, _ -> chart.axisLeft.axisMinimum }
}

val upper = LineDataSet(upperValues, "Upper").apply {
    isDrawFilledEnabled = true
    isDrawCirclesEnabled = false
    fillColor = Color.WHITE
    fillAlpha = 255
    fillFormatter = IFillFormatter { _, _ -> chart.axisLeft.axisMaximum }
}

chart.data = LineData(lower, upper)
```

The lower line fills down to the axis minimum and the upper line fills up to the axis maximum, both in the background color of the view. What is left uncovered is the strip between the two lines, showing the grid background through it. Fixed `axisMinimum` and `axisMaximum` values on the left axis keep the two fills from moving when the data changes.

## Line charts only

The fill properties come from `LineRadarDataSet`, so a `RadarDataSet` fills too, but the formatter does not apply to it: a radar area is always the polygon through its own points, and there is nothing to choose. `fillFormatter` exists on `LineDataSet` alone, and the line chart renderer is the only place it is read.

Inside a line chart it applies to every drawing mode. `LINEAR` and `STEPPED` build the filled area from the segments, `CUBIC_BEZIER` and `HORIZONTAL_BEZIER` close the curve to the same y value. A chart with `isDrawFilledEnabled` on draws the area first and the line on top of it.

While `animateY` is running, the entry values are scaled by the animation phase but the fill boundary is not, so the shaded area grows up from a boundary that stays where it will end.

## Where to go next

- [The DataSet subclasses](/mpandroidchart/docs/dataset-subclasses/) for the rest of what a `LineDataSet` can do.
- [Formatters](/mpandroidchart/docs/formatters/) for the value and axis label formatters.
- [Colors](/mpandroidchart/docs/colors/) for gradients and color lists.
