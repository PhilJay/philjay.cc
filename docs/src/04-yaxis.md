# The y axis

The two vertical axes of a chart: which one a data set plots against, where their labels sit, and how their value range is padded.

Charts with axes have a left and a right `YAxis`, both enabled by default.

```kotlin
val left = chart.axisLeft
val right = chart.axisRight
val byDependency = chart.getAxis(YAxis.AxisDependency.LEFT)

val radar = radarChart.yAxis   // the radar chart has exactly one
```

Everything on [the axis](/mpandroidchart/docs/axis/) applies here too. This page covers what only the y axis has.

> Apply settings that change the value range before you assign `chart.data`, because that is when the range is computed. If you change one afterwards, call `chart.notifyDataSetChanged()` to have it applied.

## Which axis a data set uses

Every data set carries an `axisDependency`. It is `LEFT` by default, so all data plots against the left axis unless you say otherwise.

```kotlin
val temperature = LineDataSet(tempEntries, "Temperature")
val rainfall = LineDataSet(rainEntries, "Rainfall").apply {
    axisDependency = YAxis.AxisDependency.RIGHT
}

chart.data = LineData(temperature, rainfall)
```

Each axis then computes its range only from the sets that point at it, which is how two series with completely different units share one chart. Highlighting, markers and the fill of a line all use the same axis as their set.

If no set uses one of the axes, that axis shows the same range as the other one, so a second scale never appears out of thin air. The usual thing to do with it is to turn it off:

```kotlin
chart.axisRight.isEnabled = false
```

## Where the labels sit

| Property | Meaning | Default |
| --- | --- | --- |
| `labelPosition` | `OUTSIDE_CHART` next to the content area, `INSIDE_CHART` on top of it. | `OUTSIDE_CHART` |
| `labelXOffset` | Extra horizontal shift in dp applied to the labels. | `0`, and `10` on a radar chart |
| `xOffset` | Distance in dp between the labels and the content edge. | `5` |

```figure
<svg viewBox="0 0 640 236" width="100%" role="img" aria-label="Axis labels outside and inside the content area" style="max-width:640px;height:auto;display:block;margin:0 auto 6px">
<title>Axis labels outside and inside the content area</title>
<rect x="40.0" y="46.0" width="250.0" height="130.0" rx="6" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="4 4"/>
<text x="40.0" y="34.0" fill="rgba(255,255,255,0.32)" font-size="10.5" text-anchor="start">the chart view</text>
<rect x="86.0" y="58.0" width="194.0" height="106.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M86.0 128.0 L113.7 109.3 L141.4 121.2 L169.1 92.3 L196.9 106.8 L224.6 80.5 L252.3 99.1 L280.0 114.4" fill="none" stroke="#00a9ab" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
<text x="78.0" y="77.9" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">85</text>
<text x="78.0" y="115.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">50</text>
<text x="78.0" y="152.1" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="end">15</text>
<text x="165.0" y="202.0" fill="rgba(255,255,255,0.78)" font-size="12" text-anchor="middle">OUTSIDE_CHART</text>
<rect x="350.0" y="46.0" width="250.0" height="130.0" rx="6" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="4 4"/>
<text x="350.0" y="34.0" fill="rgba(255,255,255,0.32)" font-size="10.5" text-anchor="start">the chart view</text>
<rect x="360.0" y="58.0" width="230.0" height="106.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M360.0 128.0 L392.9 109.3 L425.7 121.2 L458.6 92.3 L491.4 106.8 L524.3 80.5 L557.1 99.1 L590.0 114.4" fill="none" stroke="#00a9ab" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
<text x="366.0" y="77.9" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="start">85</text>
<text x="366.0" y="115.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="start">50</text>
<text x="366.0" y="152.1" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="start">15</text>
<text x="475.0" y="202.0" fill="rgba(255,255,255,0.78)" font-size="12" text-anchor="middle">INSIDE_CHART</text>
<text x="320.0" y="228.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="middle">Inside costs no offset, so the content area keeps the full width</text>
</svg>
```

```kotlin
chart.axisLeft.labelPosition = YAxis.YAxisLabelPosition.INSIDE_CHART
```

Drawing the labels inside is worth knowing about because of `needsOffset`. That read only property is true only when the axis is enabled, draws labels, and draws them outside. While it is false the chart adds no space for the axis, and that side of the content area keeps only the chart's `minOffset`, 15 dp by default.

## How much width the axis takes

With outside labels, the chart reserves the width of the longest label plus `xOffset` on both sides. Two properties bound that number, both in dp:

| Property | Meaning | Default |
| --- | --- | --- |
| `minWidth` | Smallest width the chart reserves. | `0` |
| `maxWidth` | Largest width it reserves. | no limit |

```kotlin
chart.axisLeft.minWidth = 40f
```

A minimum width is the fix for a chart that jumps sideways while its data changes, for example a live chart whose labels grow from "9" to "10". A maximum width keeps one very long label from eating the plot, at the price of the label sticking into it.

In a `HorizontalBarChart` the y axes run horizontally, the left one along the top edge and the right one along the bottom. The chart reserves height for them there, the label height plus `yOffset` on both sides, so `minWidth` and `maxWidth` have no effect in that layout.

## Padding above and below the data

`spaceTop` and `spaceBottom` are percentages of the data range, not values. Both default to 10, which is the small gap you see above the highest point of a fresh chart.

```kotlin
chart.axisLeft.spaceTop = 35f    // room for value labels above the bars
chart.axisLeft.spaceBottom = 0f
```

They only apply to an end that the chart computes. Once you assign `axisMinimum`, `spaceBottom` is ignored; once you assign `axisMaximum`, `spaceTop` is ignored.

```kotlin
chart.axisLeft.axisMinimum = 0f     // bars measured from zero
chart.axisLeft.axisMaximum = 100f
```

Starting a bar chart at zero is almost always right, and it is the one case where fixing a limit beats padding it.

> `spaceMin` and `spaceMax` from `AxisBase` do nothing on a y axis. The y axis computes its own range and uses the two percentages instead.

## Label count and granularity

The y axis picks round values by default, which is usually what you want. Fix the range and force the count when you want the grid to line up with something else, for example across several charts in a list:

```kotlin
chart.axisLeft.apply {
    axisMinimum = 0f
    axisMaximum = 100f
    labelCount = 5
    isForceLabelsEnabled = true
}
```

For whole numbers that must not repeat while zooming, set the granularity:

```kotlin
chart.axisLeft.granularity = 1f
```

## Hiding the outer labels

The topmost y label sits at the top corner of the chart, where it often collides with an x axis label at `TOP` position or with the legend. Each end can be dropped on its own.

| Property | Meaning | Default |
| --- | --- | --- |
| `isDrawTopYLabelEntryEnabled` | Draws the label at the top end of the axis. | `true` |
| `isDrawBottomYLabelEntryEnabled` | Draws the label at the bottom end. | `true` |

## Inverting the axis

```kotlin
chart.axisLeft.isInverted = true
```

The largest value is then at the bottom and the smallest at the top. Ranks and race positions read better that way. Grid lines, limit lines and highlights follow the inversion. `chart.isAnyAxisInverted` tells you whether either side is inverted.

## The zero line

Besides the grid, a y axis can draw one line at the value 0, styled on its own. It is drawn whenever the axis is enabled, even with grid lines off.

| Property | Meaning | Default |
| --- | --- | --- |
| `isDrawZeroLineEnabled` | Draws a line at value 0. | `false` |
| `zeroLineColor` | Its color. | gray |
| `zeroLineWidth` | Its width in dp. | `0.5` |

A chart with nothing but a baseline, for a bar chart with positive and negative values:

```kotlin
chart.axisLeft.apply {
    isDrawLabelsEnabled = false
    isDrawAxisLineEnabled = false
    isDrawGridLinesEnabled = false
    isDrawZeroLineEnabled = true
    zeroLineWidth = 1f
}
chart.axisRight.isEnabled = false
```

## Next

- [The x axis](/mpandroidchart/docs/xaxis/) for the horizontal side.
- [Formatting values](/mpandroidchart/docs/formatters/) for units and currencies on the labels.
- [Setting data](/mpandroidchart/docs/setting-data/) for the data sets that carry the axis dependency.
