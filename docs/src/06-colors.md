# Setting colors

How a chart decides what color to paint each entry with, from a single line color to per-bar gradients and value label colors.

Every data set carries its own colors, so each line, each group of bars and each pie keeps its own look. Nothing is set globally.

## One color, or a list

A data set holds a `colors` list. The renderer asks for the color of entry `i` with `getColor(i)`, which returns `colors[i % colors.size]`, so the list is reused from the start once you run out of colors.

```kotlin
val set = LineDataSet(entries, "Revenue")
set.color = Color.BLUE                                  // one color for everything
set.colors = listOf(Color.BLUE, Color.RED, Color.GREEN) // cycled per entry
```

`color` is a convenience on top of the list: reading it returns the first color, assigning it throws the list away and keeps only that one color.

What "per entry" means depends on the chart:

| Chart | One color per |
| --- | --- |
| Pie | slice |
| Bar | bar, and per stack value in a stacked bar |
| Scatter, bubble | point |
| Radar | set, because the polygon is drawn as one path |
| Line | line segment, but only in `LINEAR` and `STEPPED` mode |

> A cubic line is drawn as one path, so `CUBIC_BEZIER` and `HORIZONTAL_BEZIER` always use `color` and ignore the rest of the list.

If you never touch the colors, a data set starts with one light blue, `Color.rgb(140, 234, 255)`.

## Building the list

Beside assigning `colors` directly there are a few helpers on `BaseDataSet`, so on every data set class:

| Call | What it does |
| --- | --- |
| `setColors(vararg colors: Int)` | replaces the list with the given colors |
| `setColors(colors: List<Int>, alpha: Int)` | same, but applies `alpha` to each color |
| `setColor(color: Int, alpha: Int)` | one color with `alpha` applied |
| `addColor(color: Int)` | appends one color |
| `resetColors()` | empties the list |

The alpha variants ignore whatever alpha the color already carries and replace it with the value you pass, from 0 for invisible to 255 for opaque.

```kotlin
set.setColor(ColorTemplate.COLORFUL_COLORS[0], 130)   // half transparent
set.setColors(ColorTemplate.MATERIAL_COLORS, 200)
```

> `resetColors()` leaves the set without any color. `color` and `getColor(index)` then throw `IllegalStateException`, and the chart fails as soon as it draws the set. Add at least one color back first.

## Colors from resources

Color resource ids are not colors, they have to be resolved first. Two ways:

```kotlin
set.setColors(listOf(R.color.red1, R.color.red2, R.color.red3), context)

// or resolve them yourself, for example to reuse the list
val palette = ColorTemplate.createColors(resources, listOf(R.color.red1, R.color.red2))
set.colors = palette
```

`ColorTemplate.rgb("#2ecc71")` parses a hex string with or without the leading `#` into an opaque color, and `ColorTemplate.colorWithAlpha(color, alpha)` replaces the alpha channel of a color you already have.

## The ColorTemplate palettes

`ColorTemplate` carries six ready-made palettes. Since version 4 they are `List<Int>`, not arrays, so you can assign, slice and concatenate them like any other list.

| Palette | Colors |
| --- | --- |
| `LIBERTY_COLORS` | five light blue and teal tones |
| `JOYFUL_COLORS` | five strong pink, orange, yellow, green and cyan tones |
| `PASTEL_COLORS` | five muted blue, green, beige, rose and red tones |
| `COLORFUL_COLORS` | five saturated red, orange, yellow, green and brown tones |
| `VORDIPLOM_COLORS` | five light green, yellow, orange, blue and pink tones |
| `MATERIAL_COLORS` | four material tones: green, yellow, red, blue |

```kotlin
set.colors = ColorTemplate.VORDIPLOM_COLORS
set.colors = ColorTemplate.MATERIAL_COLORS.take(3)
set.colors = ColorTemplate.JOYFUL_COLORS + ColorTemplate.PASTEL_COLORS
```

There is also `ColorTemplate.holoBlue`, the light blue from Android 4, which the example app uses a lot.

## COLOR_NONE and COLOR_SKIP

Two constants in `ColorTemplate` are not colors but markers. Both are fully transparent values, so nothing is ever drawn with them by accident.

`COLOR_NONE` means "nothing set here, decide for me". Renderers that see it either fall back to the entry color or leave the element out:

- `CandleDataSet.increasingColor`, `decreasingColor`, `neutralColor` and `shadowColor` all default to it, and the candle renderer then uses the entry's color from `colors`.
- `ScatterDataSet.scatterShapeHoleColor` defaults to it, and the shape renderers leave the hole transparent.
- `RadarDataSet.highlightCircleStrokeColor` defaults to it, and the radar renderer strokes the highlight ring in the set's first color. Its `highlightCircleFillColor` set to `COLOR_NONE` leaves the ring unfilled.
- `LineDataSet.circleHoleColor` set to it makes the line renderer punch a see through hole, so the chart background shows through the circle.

`COLOR_SKIP` only appears in the legend. A `LegendEntry` whose `formColor` is `COLOR_SKIP`, `COLOR_NONE` or plain 0 gets no form drawn, just its label. That is how you write a legend entry that is only a heading.

```kotlin
chart.legend.entries = listOf(
    LegendEntry("Quarterly", formColor = ColorTemplate.COLOR_SKIP),
    LegendEntry(
        "Revenue",
        form = Legend.LegendForm.SQUARE,
        formSize = 10f,
        formColor = Color.BLUE,
    ),
)
```

## Gradients with Fill

A plain color int cannot describe a gradient, so bar data sets take a list of `Fill` objects instead. A `Fill` knows four types, picked by the constructor you use:

| Constructor | `Fill.Type` | Draws |
| --- | --- | --- |
| `Fill()` | `EMPTY` | nothing |
| `Fill(color)` | `COLOR` | a solid color, with `alpha` applied on top |
| `Fill(startColor, endColor)` | `LINEAR_GRADIENT` | a two color gradient |
| `Fill(gradientColors)` | `LINEAR_GRADIENT` | evenly spread colors |
| `Fill(gradientColors, gradientPositions)` | `LINEAR_GRADIENT` | colors at positions from 0 to 1 |
| `Fill(drawable)` | `DRAWABLE` | the drawable stretched to the filled area |

Assign the list to `fills` and it replaces `colors` for the bars. Like `colors`, the list is cycled per bar.

```kotlin
val set = BarDataSet(entries, "The year 2017")
set.fills = mutableListOf(
    Fill(orangeLight, blueDark),
    Fill(blueLight, purple),
    Fill(greenLight, redDark),
)
```

For one gradient on every bar there is a shortcut:

```kotlin
set.setGradientColor(startColor, endColor)
```

`Fill.Direction` says where a linear gradient starts: `DOWN` from the top edge, `UP` from the bottom edge, `RIGHT` from the left edge, `LEFT` from the right edge. You do not set it on the fill, the renderer picks it: a vertical bar chart draws `UP`, a horizontal one `RIGHT`, and both flip when the axis is inverted.

## Fills under a line

Line and radar sets do not use `Fill`. They fill with a color plus an alpha, or with a drawable, which is how you get a fading area under a line:

```kotlin
set.isDrawFilledEnabled = true
set.fillColor = Color.BLUE
set.fillAlpha = 85                 // 0 to 255, default 85

// or a gradient, which takes precedence over fillColor
set.fillDrawable = GradientDrawable(
    GradientDrawable.Orientation.TOP_BOTTOM,
    intArrayOf(
        ColorTemplate.colorWithAlpha(Color.BLUE, 115),
        ColorTemplate.colorWithAlpha(Color.BLUE, 0),
    ),
)
```

Assigning `fillColor` clears `fillDrawable`, so the last one you set wins. How far down the fill reaches is decided by the [fill formatter](/mpandroidchart/docs/fillformatter/).

## Value label colors

The labels drawn at the entries have their own color list, with the same cycling rule and the same convenience property.

```kotlin
set.valueTextColor = Color.DKGRAY
set.valueTextColors = listOf(Color.DKGRAY, Color.RED)
```

The default is a single `Color.BLACK`. To set one color for every set at once, call it on the data object rather than on each set:

```kotlin
chart.data?.setValueTextColor(Color.WHITE)
```

Circle colors on a line set are a third list, independent of both: see [DataSet subclasses](/mpandroidchart/docs/dataset-subclasses/).

## Colors in Compose

Compose `Color` values are not ARGB ints, so the `MPChartCompose` module adds three extensions that convert for you.

```kotlin
import com.github.mikephil.charting.compose.setCircleColors
import com.github.mikephil.charting.compose.setColors
import com.github.mikephil.charting.compose.toComposeColors

set.setColors(
    listOf(MaterialTheme.colorScheme.primary, MaterialTheme.colorScheme.secondary)
)
set.setCircleColors(listOf(MaterialTheme.colorScheme.primary))

// and the other direction, for a Compose legend or a swatch next to the chart
val swatches: List<Color> = ColorTemplate.MATERIAL_COLORS.toComposeColors()
```

For a single color there is no helper and none is needed, `color = myColor.toArgb()` does it. More on the Compose module in [Charts in Compose](/mpandroidchart/docs/compose/).
