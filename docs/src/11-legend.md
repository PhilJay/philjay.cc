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
