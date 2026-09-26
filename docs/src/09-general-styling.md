# General styling

The settings every chart type shares: the background, the text shown while there is no data, the space around the drawing area, the paints the chart draws with, and how to save it as an image.

Everything here lives on the chart itself. Styling that belongs to one series is on the data set, see [Setting data](/mpandroidchart/docs/setting-data/), and styling that belongs to one chart type is in [Chart specific styling](/mpandroidchart/docs/chart-styling/).

## The background

A chart is an ordinary `View`, so its background is set the usual Android way. In Compose that is the modifier you pass to the chart:

```kotlin
LineChart(
    data = lineData,
    modifier = Modifier
        .fillMaxWidth()
        .height(300.dp)
        .background(MaterialTheme.colorScheme.surface),
)
```

With views it is a property or a layout attribute:

```kotlin
chart.setBackgroundColor(Color.WHITE)
```

```xml
<com.github.mikephil.charting.charts.LineChart
    android:id="@+id/chart"
    android:layout_width="match_parent"
    android:layout_height="300dp"
    android:background="@color/surface" />
```

The charts with an x axis and two y axes, that is every type except `PieChart` and `RadarChart`, can also fill and outline the content area, the rectangle the data is drawn in.

```kotlin
chart.isDrawGridBackgroundEnabled = true
chart.gridBackgroundColor = Color.rgb(240, 240, 240)

chart.isDrawBordersEnabled = true
chart.borderColor = Color.DKGRAY
chart.borderWidth = 1f
```

| Property | Meaning | Default |
| --- | --- | --- |
| `isDrawGridBackgroundEnabled` | Fill the content area | `false` |
| `gridBackgroundColor` | Fill color | light grey |
| `isDrawBordersEnabled` | Draw a line around the content area | `false` |
| `borderColor` | Border color | black |
| `borderWidth` | Border width in dp | `1` |

## The empty state

While the chart has no data, or data without entries, it draws an empty state instead: a faint outline of its chart type (bars, a line, a ring, a web or dots) above the text "No data yet", in a slate grey that reads on light and dark backgrounds. Every part of it can be changed:

```kotlin
chart.noDataText = "Nothing to show yet"
chart.noDataTextColor = Color.GRAY
chart.noDataTextSize = 14f                     // dp
chart.noDataTextTypeface = typeface
chart.noDataTextAlignment = Paint.Align.CENTER
chart.noDataIconColor = Color.argb(80, 128, 128, 128)
chart.noDataIcon = ContextCompat.getDrawable(context, R.drawable.empty) // replaces the outline
chart.isNoDataIconEnabled = false              // text only
```

The alignment decides where the icon and text sit horizontally: `LEFT` at the left edge of the view, `RIGHT` at the right edge, `CENTER` in the middle. An empty `noDataText` draws only the icon.

### Loading

Set `chart.isLoading = true` while your data is on its way. The empty state then shows `loadingText` ("Loading…" by default) and its icon gently pulses. Data that arrives is drawn as usual, so you can set the flag back to false whenever it suits you.

```kotlin
chart.isLoading = true
viewModel.sales.observe(owner) { sales ->
    chart.data = sales.toBarData()
    chart.isLoading = false
}
```

To draw an empty state of your own, subclass the chart and override `drawEmptyState(canvas)`, or `drawNoDataIcon(canvas, bounds, paint)` to change only the outline.

`chart.clear()` drops the data and brings this text back. `chart.clearValues()` keeps the data object but removes all its data sets, and `chart.isEmpty` tells you whether anything is left to draw.

## Space around the content

The chart computes the content area from the legend, the axis labels and the description. Two properties let you push it around without taking over the calculation.

**Extra offsets** are added on top of the computed ones, in dp. Use them to keep a marker, a rounded corner or a long label from being cut off.

```kotlin
chart.setExtraOffsets(0f, 8f, 8f, 4f)   // left, top, right, bottom
chart.extraBottomOffset = 12f           // or one side at a time
```

**The minimum offset** is the smallest space that is kept on every side, whatever the calculation produces. It is `minOffset` on both `BarLineChartBase` and `PieRadarChartBase`, but the defaults differ.

| Property | Meaning | Default |
| --- | --- | --- |
| `extraLeftOffset`, `extraTopOffset`, `extraRightOffset`, `extraBottomOffset` | Space in dp added to the computed offset | `0` |
| `minOffset` on line, bar, scatter, candle, bubble and combined charts | Smallest space in dp on every side | `15` |
| `minOffset` on pie and radar charts | Smallest space in dp on every side | `0` |

A radar chart adds its own space on top of that, because its axis labels are drawn outside the web: as much as a label is wide to the left and right, and as much as half that plus a label's height above and below. A legend gets twice its own text size as a gap.

If you need exact control, `setViewPortOffsets(left, top, right, bottom)` replaces the calculation with fixed pixel values and `resetViewPortOffsets()` gives it back. See [Modifying the viewport](/mpandroidchart/docs/viewport/).

> Offsets are recalculated when the data changes, when the view is resized and when the chart zooms. Setting them at any point is enough, they do not need to be reapplied.

## The paints

Version 3.x had one `setPaint(paint, PAINT_INFO)` function with a list of integer constants. Every paint is now a named property.

| Property | What it draws | Declared on |
| --- | --- | --- |
| `infoPaint` | The no data text | `Chart` |
| `descriptionPaint` | The description text | `Chart` |
| `legendLabelPaint` | The legend labels | `Chart` |
| `gridBackgroundPaint` | The fill behind the content area | `BarLineChartBase` |
| `holePaint` | The hole in the middle of a pie | `PieChart` |
| `centerTextPaint` | The text in the middle of a pie | `PieChart` |

Reach for a paint when you want something the properties do not expose, such as a shader, a shadow layer or the text size of the no data text.

```kotlin
chart.infoPaint.textSize = Utils.convertDpToPixel(16f)

chart.gridBackgroundPaint.shader = LinearGradient(
    0f, 0f, 0f, chart.height.toFloat(),
    Color.WHITE, Color.LTGRAY, Shader.TileMode.CLAMP,
)
```

> `descriptionPaint` and `legendLabelPaint` have their typeface, text size and color overwritten from the `Description` and `Legend` components before every draw. Set those three on the component, and use the paint only for the rest.

## Value labels

Value labels are drawn per data set with `set.isDrawValuesEnabled`. On the charts with an x axis, one chart level property limits them: a data set draws its labels only while at most `maxVisibleCount` of its entries are in view, so zooming in brings them back. The default is 100.

```kotlin
chart.maxVisibleCount = 60
chart.isClipValuesToContentEnabled = true
```

`isClipValuesToContentEnabled` keeps labels inside the content area instead of letting them bleed over the axes. Its sibling `isClipDataToContentEnabled` does the same for the data itself and is on by default. Turn it off when thick lines or large shapes get cut at the edge of the content.

## Refreshing

Two calls cover everything.

- `chart.invalidate()` redraws with what the chart already knows. Use it after a pure styling change.
- `chart.notifyDataSetChanged()` refreshes the data, recalculates the axis ranges, the legend and the offsets, and redraws. Use it after changing entries or data sets in place.

Assigning `chart.data` calls `notifyDataSetChanged()` for you, so nothing else is needed after setting new data.

## Hardware acceleration

A chart draws through whatever the window gives it until you ask for a layer of its own. `isHardwareAccelerationEnabled` puts the view on one.

```kotlin
chart.isHardwareAccelerationEnabled = true    // hardware layer
chart.isHardwareAccelerationEnabled = false   // software layer
```

A hardware layer helps a chart that animates or scrolls over a busy background. A software layer is the fallback when a large data set with a lot of transparency draws wrong or slowly on the GPU.

> The property reads back true only while a hardware layer is set. A fresh chart has no layer at all, so it reads false even though drawing is hardware accelerated, and setting it to false forces a software layer rather than removing the layer.

## Saving the chart as an image

`toBitmap()` draws the chart into a new `ARGB_8888` bitmap the size of the view, over the view background or over white when there is none. Before the first layout the view has no size, and you get a 1 by 1 bitmap.

```kotlin
val bitmap = chart.toBitmap()
```

`saveToGallery()` writes that bitmap into the device gallery through the `MediaStore` and returns whether it worked.

```kotlin
val saved = chart.saveToGallery(
    fileName = "sales_${System.currentTimeMillis()}",
    subFolderPath = "MPAndroidChart",
    format = Bitmap.CompressFormat.JPEG,
    quality = 70,
)
```

Only the file name is required. The image lands in that folder inside DCIM, the matching extension is appended when the name does not already carry it, and PNG ignores the quality. On Android 10 and above the MediaStore creates the folder; below that the library creates it and the app needs the write external storage permission.

> `saveToPath` from version 3.x is gone. Write `toBitmap()` to a file yourself if you need a specific location.

## Logging

Logging writes what the chart is doing to logcat under the tag `MPAndroidChart`: when data is set, the computed offsets, the content rectangle, every highlight, and the draw time per frame.

```kotlin
chart.isLogEnabled = true
```

It slows drawing down noticeably, so keep it off in release builds. On the charts with an x axis, `chart.resetTracking()` clears the running draw time average.

## Releasing view resources

A chart inside a list or a pager can hold on to background drawables after it leaves the window. Setting `chart.isUnbindEnabled = true` releases them and removes child views when the view is detached. Leave it off unless you are chasing a leak, since a rebound chart has to rebuild what was released.
