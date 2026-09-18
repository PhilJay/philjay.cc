# Miscellaneous

The useful corners of the library that do not belong to any one chart type: unit conversion, number formatting, saving an image, the pooled geometry classes, sorting, logging and what to do with a very large data set.

## Utils and unit conversion

`Utils` is an object of static helpers shared by every chart. The dp conversions read the display density, which it has to learn from a `Context` first:

```kotlin
Utils.init(context)
```

Every chart calls this in its constructor, so in normal use you never do. You only need it when you call a `Utils` function before any chart exists, for example while building data on a background thread or in a unit test. Calling it twice is harmless.

```kotlin
val eightDp = Utils.convertDpToPixel(8f)
val backInDp = Utils.convertPixelsToDp(eightDp)
```

Without `init`, both functions log an error to logcat and return the value unchanged, so a marker offset silently comes out in the wrong unit rather than crashing. `init` also reads the fling velocities from the `ViewConfiguration`, available as `Utils.minimumFlingVelocity` and `Utils.maximumFlingVelocity`.

A few constants live there too: `Utils.DEG2RAD` and `Utils.FDEG2RAD` convert degrees to radians as a `Double` and a `Float`, and `Utils.FLOAT_EPSILON` and `Utils.DOUBLE_EPSILON` are the smallest positive values of their type, useful when comparing chart values against zero.

## Formatting numbers

`Utils` carries the number helpers the axis renderers use. They are public, so your own [formatters](/mpandroidchart/docs/formatters/) can reuse them.

| Function | What it returns |
| --- | --- |
| `formatNumber(number, digitCount, separateThousands, separateChar)` | `number` with a fixed number of decimals. Zero returns `"0"`, values between -1 and 1 get a leading zero, `digitCount` above 9 is limited to 9, and the decimal separator is a comma. |
| `roundToNextSignificant(number)` | `number` rounded to one significant digit: 123 becomes 100, 0.0234 becomes 0.02, 150 becomes 200. Infinite, NaN and zero return 0. |
| `getDecimals(number)` | How many decimals it takes to show `number` with two digits beyond its magnitude: 0 for 100, 2 for 5, 4 for 0.02. This is how a chart picks its default formatter. |
| `Utils.defaultValueFormatter` | The one decimal place formatter that components fall back to. |

```kotlin
Utils.formatNumber(1234.5f, 1, separateThousands = true)  // "1.234,5"
```

> `formatNumber` writes a comma as the decimal separator regardless of locale. For anything a user reads, prefer `NumberFormat` or `String.format` inside your own `IValueFormatter`.

## Saving a chart as an image

`toBitmap()` draws the chart into a new bitmap of the view size, over the view background or white when there is none. It always holds the latest drawing state.

```kotlin
val bitmap = chart.toBitmap()
```

`saveToGallery` writes that bitmap to the device gallery through the `MediaStore` and returns whether it worked:

```kotlin
val saved = chart.saveToGallery(
    fileName = "revenue",
    subFolderPath = "MyApp",
    fileDescription = "Revenue for August",
    format = Bitmap.CompressFormat.JPEG,
    quality = 80,
)
```

| Parameter | Meaning | Default |
| --- | --- | --- |
| `fileName` | File name. The extension for `format` is appended when it is missing. | required |
| `subFolderPath` | Folder inside DCIM, or empty for DCIM itself. | `""` |
| `fileDescription` | Description stored alongside the image. | a library string |
| `format` | `PNG`, `JPEG` or `WEBP`. PNG ignores the quality. | `PNG` |
| `quality` | Compression quality from 0 to 100. Values outside that range fall back to 40. | 40 |

It returns false when the folder could not be created, the `MediaStore` entry could not be inserted, or writing failed. On Android 9 and below the app needs the write external storage permission; from Android 10 on it does not.

> Version 3 had `saveToPath` and `getChartBitmap`. They are gone. Use `toBitmap()` and write the bitmap wherever you like, or `saveToGallery` for the gallery.

## What the chart tells you

A handful of members on `Chart` that are easy to overlook.

| Member | Meaning |
| --- | --- |
| `clear()` | Sets the data to null, clears the highlight and redraws, which shows the no data text. |
| `clearValues()` | Removes all data sets but keeps the data object, then redraws. |
| `isEmpty` | True when there is no data or the data holds no entries. |
| `data` | The data object you assigned. |
| `viewPortHandler` | Size, content rectangle, zoom and scroll state. See [the ViewPortHandler](/mpandroidchart/docs/viewporthandler/). |
| `renderer` | The `DataRenderer` that draws the data. Replace it for custom drawing. |
| `center` | Center of the whole view in pixels. |
| `centerOffsets` | Center of the content area, which is the view minus the axis, legend and extra offsets. |
| `yMin`, `yMax` | Smallest and largest y value across all data sets, or 0 without data. |
| `isHardwareAccelerationEnabled` | Switches the view between a hardware and a software layer. |
| `isUnbindEnabled` | Releases background drawables and child views when the chart leaves the window. Off by default. |

On line, bar, scatter, candle, bubble and combined charts, `lowestVisibleX` and `highestVisibleX` give the x values at the edges of the content area, and `visibleXRange` the span between them.

> These are values on the x axis, not indices. Version 3 had `getLowestVisibleXIndex()`; there are no x indices any more. `getPercentOfTotal` is also gone; on a pie chart set `isUsePercentValuesEnabled = true` instead.

## Pooled points and sizes

The renderers run inside `onDraw`, so the library avoids allocating there. Three small mutable classes come from shared pools instead.

| Class | Holds |
| --- | --- |
| `MPPointF` | An `x` and a `y` float, usually a pixel position. |
| `MPPointD` | An `x` and a `y` double, where value to pixel conversion needs the precision. |
| `FSize` | A `width` and a `height` float, usually measured text bounds. |

All three follow the same contract. `getInstance(...)` takes one out of the pool, `recycleInstance(...)` puts it back, and `recycleInstances(list)` puts several back at once.

```kotlin
val size = Utils.calcTextSize(paint, "Revenue")
val width = size.width
FSize.recycleInstance(size)
```

Two rules matter. `MPPointF.getInstance()` without arguments keeps whatever values the point held before, so set them; the other two always take their values as arguments. And recycling the same instance twice throws `IllegalArgumentException`, as does recycling an instance into a pool while another pool holds it. If you are unsure whether you own an instance, do not recycle it; the pool refills itself.

Points returned by public chart getters such as `chart.center` are fresh instances rather than pooled ones. You may keep them or recycle them, whichever suits you.

Every `Utils` function that hands you an `FSize` or an `MPPointF` says so in its documentation: `calcTextSize`, `getPosition`, `getSizeOfRotatedRectangleByDegrees` and `getSizeOfRotatedRectangleByRadians`. `calcTextSize` and `getPosition` also have an overload that writes into a size or point you already own, which avoids the pool entirely.

### The pool itself

`ObjectPool` is generic, so you can pool your own type in a custom renderer. Subclass `ObjectPool.Poolable` and implement `instantiate()`, then create a pool with a starting capacity:

```kotlin
class Segment(var from: Float = 0f, var to: Float = 0f) : ObjectPool.Poolable() {
    override fun instantiate(): ObjectPool.Poolable = Segment()
}

private val pool = ObjectPool.create(64, Segment()).apply { replenishPercentage = 0.5f }
```

An empty pool creates new instances from the model object, and a full pool doubles its capacity. `replenishPercentage` is the fraction of the capacity created when it runs empty, 1 by default and clamped to 0 until 1; with 0 the pool never refills. `poolCapacity` and `poolCount` tell you how it is doing. `create`, `get` and `recycle` are synchronised, and `create` needs a capacity greater than 0 or it throws.

## Sorting entries

Data sets expect their entries sorted by x. `EntryXComparator` does that:

```kotlin
val entries = readEntries().sortedWith(EntryXComparator())
val set = LineDataSet(entries, "Revenue")
```

For a set that already exists, `addEntryOrdered` inserts at the right position instead of appending, which saves a re-sort. See [dynamic data](/mpandroidchart/docs/dynamic-data/).

> A `DataSet` keeps an `ArrayList` you pass by reference and copies any other list. Sorting an `ArrayList` you handed over therefore also sorts the data set.

## Exceptions the library throws

There are few of them, and each one points at a specific mistake.

| Exception | Thrown by | Cause |
| --- | --- | --- |
| `IllegalStateException` | `BarChart.groupBars` | No data was set on the chart yet. |
| `IllegalStateException` | `BarData.groupBars` | The data holds fewer than two bar data sets, so there is nothing to group. |
| `ParcelFormatException` | `Entry.writeToParcel` | The entry carries a payload that does not implement `Parcelable`. |
| `IllegalArgumentException` | `ObjectPool.recycle` | The instance is already stored in this pool or in another one. |
| `IllegalStateException` | `BaseDataSet.color` and `getColor` | The set has no colors, usually after `resetColors()`. |
| `NumberFormatException`, `IndexOutOfBoundsException` | `FileUtils.loadEntriesFromFile` and `loadEntriesFromAssets` | A line is malformed. Read errors are only logged, parse errors are not. |

In Compose, `ChartState.attach` throws `IllegalStateException` when you pass one state to a second chart. Call `rememberChartState()` once per chart.

## Logging

Every chart has a switch that writes its internals to logcat under the tag `MPAndroidChart`:

```kotlin
chart.isLogEnabled = true
```

It reports when data is set, when the chart gets a size, what is highlighted, the axis ranges as the matrices are prepared, and for line, bar and the other axis charts the time each draw took plus the running average:

```text
Drawtime: 6 ms, average: 7 ms, cycles: 42
```

On those charts `resetTracking()` zeroes the average, which is handy before measuring one specific interaction. Pie and radar charts log their computed offsets instead. Logging costs time on every draw, so leave it off in release builds.

## Large data sets

Charts handle tens of thousands of entries, but a few settings decide whether that feels smooth.

Turn off per-entry drawing you do not need. Text and circles are the expensive parts:

```kotlin
set.isDrawValuesEnabled = false
set.isDrawIconsEnabled = false
lineSet.isDrawCirclesEnabled = false
```

Keep lines straight. `LineDataSet.Mode.LINEAR` and `STEPPED` draw a path directly, while `CUBIC_BEZIER` and `HORIZONTAL_BEZIER` compute control points for every segment.

Show a window instead of everything. The renderers only draw entries between `lowestVisibleX` and `highestVisibleX`, so limiting how far out the user can zoom limits the work per frame. Call this after setting the data, since it is computed from the current axis range:

```kotlin
chart.setVisibleXRangeMaximum(100f)
chart.moveViewToX(0f)
```

Let the y axis follow the window with `chart.isAutoScaleMinMaxEnabled = true`, so a zoomed-in section uses the full height instead of the range of the whole set.

Prepare data off the main thread. Building entries, sorting them and constructing the data set are plain object work and can run on a background thread; only assigning `chart.data` and calling `notifyDataSetChanged()` have to happen on the main thread.

Finally, `chart.isHardwareAccelerationEnabled` switches the view between a hardware and a software layer. Which one wins depends on the chart and the device, so measure with `isLogEnabled` on before deciding.

## Where to go next

- [The ViewPortHandler](/mpandroidchart/docs/viewporthandler/) for the zoom and scroll state these settings operate on.
- [Formatters](/mpandroidchart/docs/formatters/) for turning values into labels.
- [Performance with large data](/mpandroidchart/docs/performance/) for the settings that decide how fast a chart draws.
- [Troubleshooting](/mpandroidchart/docs/troubleshooting/) when something on screen is not what you expected.
- [API reference](https://jitpack.io/com/github/PhilJay/MPAndroidChart/MPChartLib/v4.0.0/javadoc/) for everything else.
