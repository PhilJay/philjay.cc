# The legend

How the chart builds its legend from the data sets, how to place and style it, and how to replace the computed entries with your own.

Every chart has one, reached as `chart.legend`, and it is drawn unless you turn it off.

```kotlin
chart.legend.isEnabled = false
```

## How the legend is built

The legend is recomputed from the data every time the chart data changes, so you never fill it yourself unless you want to. One entry is created per color of a data set, and the entry labels come from the data set labels.

- A data set with one color gives one entry carrying the data set label.
- A data set with several colors gives one entry per color, capped at the number of entries. Only the last of them carries the label, the earlier ones have no label and are stacked next to it as a row of forms.
- A stacked `BarDataSet` gives one entry per stack color, labelled from `set.stackLabels`, followed by a label only entry for the data set itself.
- A `PieDataSet` gives one entry per slice, labelled from each `PieEntry`, followed by a label only entry for the data set when it has a label.
- A `CandleDataSet` with a decreasing color gives two entries, one in the decreasing and one in the increasing color, sharing the data set label.

An entry with no label draws only its form and sits next to the following entry, separated by `stackSpace`. That is how a multi color data set ends up as several forms in front of one label.

## Placement

The position is the combination of a horizontal alignment, a vertical alignment and an orientation.

```kotlin
chart.legend.apply {
    verticalAlignment = Legend.LegendVerticalAlignment.TOP
    horizontalAlignment = Legend.LegendHorizontalAlignment.RIGHT
    orientation = Legend.LegendOrientation.VERTICAL
    isDrawInsideEnabled = false
}
```

| Property | Values | Default |
| --- | --- | --- |
| `horizontalAlignment` | `LEFT`, `CENTER`, `RIGHT` | `LEFT` |
| `verticalAlignment` | `TOP`, `CENTER`, `BOTTOM` | `BOTTOM` |
| `orientation` | `HORIZONTAL` for rows, `VERTICAL` for one column | `HORIZONTAL` |
| `isDrawInsideEnabled` | Draw the legend over the content area instead of reserving space for it | `false` |
| `direction` | `LEFT_TO_RIGHT` or `RIGHT_TO_LEFT` | `LEFT_TO_RIGHT` |

```figure
<svg viewBox="0 0 760 262" width="100%" role="img" aria-label="Where the legend sits" style="max-width:760px;height:auto;display:block;margin:0 auto 6px">
<title>Where the legend sits</title>
<rect x="8.0" y="46.0" width="162.0" height="122.0" rx="6" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="4 4"/>
<rect x="18.0" y="56.0" width="142.0" height="82.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M18.0 110.1 L41.7 95.7 L65.3 104.9 L89.0 82.6 L112.7 93.7 L136.3 73.4 L160.0 87.8" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<rect x="18.0" y="147.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<rect x="34.0" y="148.5" width="34" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<rect x="76.0" y="147.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<rect x="92.0" y="148.5" width="34" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="89.0" y="194.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">BOTTOM · LEFT</text>
<text x="89.0" y="212.0" fill="#00a9ab" font-size="11" text-anchor="middle">the default</text>
<rect x="202.0" y="46.0" width="162.0" height="122.0" rx="6" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="4 4"/>
<rect x="212.0" y="60.0" width="96.0" height="98.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M212.0 124.7 L228.0 107.4 L244.0 118.4 L260.0 91.8 L276.0 105.1 L292.0 80.8 L308.0 98.0" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<rect x="318.0" y="67.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<rect x="334.0" y="68.5" width="28" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<rect x="318.0" y="85.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<rect x="334.0" y="86.5" width="28" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="283.0" y="194.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">TOP · RIGHT</text>
<text x="283.0" y="212.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="middle">vertical</text>
<rect x="396.0" y="46.0" width="162.0" height="122.0" rx="6" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="4 4"/>
<rect x="406.0" y="56.0" width="142.0" height="82.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M406.0 110.1 L429.7 95.7 L453.3 104.9 L477.0 82.6 L500.7 93.7 L524.3 73.4 L548.0 87.8" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<rect x="425.0" y="147.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<rect x="441.0" y="148.5" width="34" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<rect x="483.0" y="147.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<rect x="499.0" y="148.5" width="34" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="477.0" y="194.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">BOTTOM · CENTER</text>
<rect x="590.0" y="46.0" width="162.0" height="122.0" rx="6" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="4 4"/>
<rect x="600.0" y="56.0" width="142.0" height="102.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M600.0 123.3 L623.7 105.4 L647.3 116.8 L671.0 89.0 L694.7 102.9 L718.3 77.6 L742.0 95.6" fill="none" stroke="#00a9ab" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
<rect x="680.0" y="62.0" width="56.0" height="36.0" rx="4" fill="rgba(10,16,19,0.88)" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<rect x="688.0" y="69.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<rect x="704.0" y="70.5" width="28" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<rect x="688.0" y="84.0" width="9" height="9" rx="2" fill="#8b7cf6"/>
<rect x="704.0" y="85.5" width="28" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="671.0" y="194.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">TOP · RIGHT</text>
<text x="671.0" y="212.0" fill="rgba(255,255,255,0.32)" font-size="11" text-anchor="middle">drawn inside</text>
<text x="380.0" y="24.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="middle">The legend sits where a vertical and a horizontal alignment put it</text>
</svg>
```

`isDrawInsideEnabled` is the difference between the chart shrinking to make room and the legend floating on top of the data.

`direction` flips an entry around: `RIGHT_TO_LEFT` draws the label first and the form after it, and lays the entries out towards the left. Use it for right to left locales.

The legend is inset from its corner by `xOffset` and `yOffset`, both in dp. The legend starts at 5 and 3.

## Forms

The form is the small shape drawn next to a label in the color of what it describes.

```kotlin
chart.legend.apply {
    form = Legend.LegendForm.LINE
    formSize = 10f
    formLineWidth = 2f
    formLineDashEffect = DashPathEffect(floatArrayOf(10f, 5f), 0f)
}
```

| Form | Result |
| --- | --- |
| `SQUARE` | A filled square |
| `CIRCLE` | A filled circle |
| `LINE` | A horizontal line using `formLineWidth` and `formLineDashEffect` |
| `EMPTY` | Nothing is drawn, but the space is kept |
| `NONE` | Nothing is drawn and no space is kept |
| `DEFAULT` | On an entry, use the legend's `form`. On the legend itself, a circle |

```figure
<svg viewBox="0 0 700 132" width="100%" role="img" aria-label="The legend forms" style="max-width:700px;height:auto;display:block;margin:0 auto 6px">
<title>The legend forms</title>
<rect x="47.0" y="51.0" width="9" height="9" rx="2" fill="#00a9ab"/>
<rect x="63.0" y="52.5" width="40" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="90.0" y="92.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">SQUARE</text>
<circle cx="181.5" cy="55.5" r="4.5" fill="#00a9ab"/>
<rect x="193.0" y="52.5" width="40" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="220.0" y="92.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">CIRCLE</text>
<line x1="307.0" y1="55.5" x2="318.0" y2="55.5" stroke="#00a9ab" stroke-width="3" stroke-linecap="round"/>
<rect x="323.0" y="52.5" width="40" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="350.0" y="92.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">LINE</text>
<rect x="437.0" y="51.0" width="9" height="9" rx="2" fill="none" stroke="rgba(255,255,255,0.10)" stroke-dasharray="2 2"/>
<rect x="453.0" y="52.5" width="40" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="480.0" y="92.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">EMPTY</text>
<text x="480.0" y="110.0" fill="rgba(255,255,255,0.32)" font-size="10.5" text-anchor="middle">space kept</text>
<rect x="567.0" y="52.5" width="40" height="6" rx="3" fill="rgba(255,255,255,0.32)"/>
<text x="610.0" y="92.0" fill="rgba(255,255,255,0.78)" font-size="11.5" text-anchor="middle">NONE</text>
<text x="610.0" y="110.0" fill="rgba(255,255,255,0.32)" font-size="10.5" text-anchor="middle">no space kept</text>
<text x="350.0" y="26.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="middle">The form is the shape drawn next to a legend label</text>
</svg>
```

`formSize` and `formLineWidth` are in dp and default to 8 and 3. A data set can override the form for its own entries through `set.form`, `set.formSize`, `set.formLineWidth` and `set.formLineDashEffect`.

## Spacing and text

```kotlin
chart.legend.apply {
    xEntrySpace = 7f
    yEntrySpace = 5f
    formToTextSpace = 5f
    stackSpace = 3f
    textColor = Color.WHITE
    textSize = 12f
    typeface = tfLight
}
```

| Property | Meaning | Default |
| --- | --- | --- |
| `xEntrySpace` | Space in dp between two entries in a row | `6` |
| `yEntrySpace` | Space in dp between two entries in a column, or between wrapped rows | `0` |
| `formToTextSpace` | Space in dp between a form and its label | `5` |
| `stackSpace` | Space in dp between stacked forms, that is entries without a label | `3` |
| `textSize` | Label size in dp, clamped to 6 until 24 | `10` |
| `textColor` | Label color | black |
| `typeface` | Label typeface, or null for the default | `null` |

Those three text properties are copied into `chart.legendLabelPaint` before every draw, so set them here rather than on the paint.

## Word wrap and maximum size

A horizontal legend with many entries would otherwise run off the side of the chart.

```kotlin
chart.legend.isWordWrapEnabled = true
chart.legend.maxSizePercent = 0.7f
```

`isWordWrapEnabled` lets a horizontal legend break into several rows. It costs drawing time and does nothing for a vertical legend.

`maxSizePercent` is the largest share of the chart the legend may take, between 0 and 1, and defaults to 0.95. For a vertical legend at the side it limits the width, for a horizontal one the height, and a wrapping horizontal legend breaks its rows at that share of the content width.

## Custom entries

Assign `entries` to take over the legend completely. That marks it custom, so the chart stops recomputing it from the data sets.

```kotlin
val square = Legend.LegendForm.SQUARE

chart.legend.entries = listOf(
    LegendEntry("Below", square, 10f, Float.NaN, null, Color.RED),
    LegendEntry("On target", square, 10f, Float.NaN, null, Color.GREEN),
)
chart.notifyDataSetChanged()
```

Every `LegendEntry` argument has a default, so named arguments read better when you only need a few:

```kotlin
LegendEntry(label = "Forecast", form = Legend.LegendForm.LINE, formColor = Color.BLUE)
```

| Argument | Meaning | Default |
| --- | --- | --- |
| `label` | The text, or null to draw only the form and stack it with the next entry | `null` |
| `form` | The shape; `DEFAULT` uses the legend's `form` | `DEFAULT` |
| `formSize` | Size in dp, or `Float.NaN` for the legend's `formSize` | `NaN` |
| `formLineWidth` | Line width in dp, or `Float.NaN` for the legend's `formLineWidth` | `NaN` |
| `formLineDashEffect` | Dash pattern, or null for the legend's | `null` |
| `formColor` | Color of the form | `ColorTemplate.COLOR_NONE` |

> The default `formColor` draws nothing, so always pass a color for an entry that should show a form.

`chart.legend.isLegendCustom` tells you whether the current entries were assigned or computed. The chart owns its `Legend`, so a custom legend is always made by assigning `chart.legend.entries`.

To go back to the automatic legend, call `resetCustom()` and let the chart recompute:

```kotlin
chart.legend.resetCustom()
chart.notifyDataSetChanged()
```

> In version 3.x this was `setCustom(colors, labels)` with two parallel arrays. Assigning `entries` replaces it, and one `LegendEntry` now carries the form, its size and its dash effect as well.

## Extra entries

Extra entries are appended after the computed ones, which is what you want for a threshold line or a note that is not a data set.

```kotlin
chart.legend.setExtra(
    colors = listOf(Color.RED, ColorTemplate.COLOR_NONE),
    labels = listOf("Target", "measured weekly"),
)
chart.notifyDataSetChanged()
```

`setExtra` pairs the two lists by index and drops the surplus of the longer one. Two sentinel colors change the form instead of coloring it:

| Color | Result |
| --- | --- |
| `ColorTemplate.COLOR_SKIP` or `0` | Form `NONE`, so no form and no space for one |
| `ColorTemplate.COLOR_NONE` | Form `EMPTY`, so no form but the space is kept, which lines the label up with the others |

You can also assign `extraEntries` directly with fully built `LegendEntry` objects. Extra entries are appended the next time the legend is computed, so call `notifyDataSetChanged()` when the chart already has data, and note that a custom legend ignores them.

## The computed sizes

After the legend has been measured, four properties describe the result. They are read only, filled during the measurement, and in pixels.

| Property | Meaning |
| --- | --- |
| `neededWidth` | Total width the legend takes, `xOffset` included |
| `neededHeight` | Total height the legend takes, `yOffset` included |
| `textWidthMax` | Width of the widest entry, form and spacing included |
| `textHeightMax` | Height of the tallest label |

They are what the chart uses to reserve space, so they are useful when you place something next to the legend yourself. `calculatedLabelSizes`, `calculatedLineSizes` and `calculatedLabelBreakPoints` hold the per entry and per row layout of a horizontal legend, for the same reason.

> These were plain getters in version 3.x. They are now properties the library sets, so assigning them is not possible and was never useful.
