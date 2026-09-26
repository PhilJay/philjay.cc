# Custom renderers

The classes that paint a chart onto its canvas, how a chart wires them up, and how to replace one with your own.

A renderer is a plain object that takes an `android.graphics.Canvas` and draws on it. It holds no data. It reads the chart through an interface, asks a `Transformer` for pixel positions, checks the `ViewPortHandler` for what is on screen, and paints. A custom data set changes the numbers a renderer is handed. A custom renderer changes what ends up on the screen.

## The hierarchy

Everything that draws extends `Renderer`, an abstract class whose whole body is one protected `viewPortHandler`. Three branches grow out of it.

| Class | Constructor | Draws |
| --- | --- | --- |
| `DataRenderer` | `(animator, viewPortHandler)` | the data: bars, lines, slices, values |
| `AxisRenderer` | `(viewPortHandler, transformer, axis)` | labels, grid lines, axis line, limit lines |
| `LegendRenderer` | `(viewPortHandler, legend)` | the legend entries and their forms |

`DataRenderer` is the one you will subclass most. It declares five members a subclass must fill in:

| Function | When it runs | What it does |
| --- | --- | --- |
| `initBuffers()` | on every data change, not per frame | creates or resizes the buffers for the new data |
| `drawData(c)` | first in a draw pass | the shapes themselves |
| `drawHighlighted(c, indices)` | right after `drawData` | the indicators for the selected entries |
| `drawExtras(c)` | after the clip is lifted | line circles, the radar web, the pie hole |
| `drawValues(c)` | last, after the axis labels | the value labels and entry icons |

It also owns three paints. Each has a read only property in front, and because a `Paint` is mutable that is enough to restyle a built-in renderer without subclassing it:

| Protected field | Public property | Default |
| --- | --- | --- |
| `renderPaint` | `paintRender` | anti-aliased, `Paint.Style.FILL` |
| `highlightPaint` | `paintHighlight` | 2 px stroke, orange `rgb(255, 187, 115)` |
| `valuePaint` | `paintValues` | `rgb(63, 63, 63)`, centered, 9 dp |

One helper is worth knowing. `applyValueTextStyle(set)` copies the typeface and text size of a data set into `valuePaint`, once per data set before its labels are drawn. `drawValue`, whose signature is in the worked example below, is the single open function on `DataRenderer` and the cheapest override in the library.

### Renderers with axes

`BarLineScatterCandleBubbleRenderer` sits between `DataRenderer` and the renderers of the charts that have an x and a y axis. It adds `shouldDrawValues(set)`, `shouldDrawValues(chart, set)`, `visibleEntryCount(chart, set)`, `isInBoundsX(entry, set)` and the `xBounds` field, an instance of its inner `XBounds` class. `shouldDrawValues(chart, set)` is the rule behind `maxVisibleCount`: it is true only while at most that many entries of the set are in the visible x range.

| Member | Meaning |
| --- | --- |
| `min` | index of the first visible entry |
| `max` | index of the last visible entry |
| `range` | `(max - min)` scaled by the x animation phase |
| `set(chart, dataSet)` | recomputes all three from `lowestVisibleX` and `highestVisibleX` |

`set` rounds the first entry down and the last one up, so the entries just off screen are included and lines do not end in mid air at the edge. Every renderer under this class calls `xBounds.set(chart, dataSet)` once per data set and then loops from `min` to `max` only.

Two more layers sit on top: `LineScatterCandleRadarRenderer` adds `drawHighlightLines(c, x, y, set)`, the vertical and horizontal crosshair, and `LineRadarRenderer` adds two `drawFilledPath` overloads, one for a color with an alpha and one for a `Drawable`.

## Which renderer each chart creates

Every chart builds its renderers in its `init` function and stores them in `lateinit var` properties. The data renderer is always `chart.renderer`:

| Chart | `renderer` |
| --- | --- |
| `LineChart` | `LineChartRenderer` |
| `BarChart` | `BarChartRenderer` |
| `HorizontalBarChart` | `HorizontalBarChartRenderer` |
| `ScatterChart` | `ScatterChartRenderer` |
| `CandleStickChart` | `CandleStickChartRenderer` |
| `BubbleChart` | `BubbleChartRenderer` |
| `CombinedChart` | `CombinedChartRenderer` |
| `PieChart` | `PieChartRenderer` |
| `RadarChart` | `RadarChartRenderer` |

Every chart that extends `BarLineChartBase` also has `rendererXAxis`, `rendererLeftYAxis` and `rendererRightYAxis`, an `XAxisRenderer` and two `YAxisRenderer` instances. `HorizontalBarChart` swaps all three for `XAxisRendererHorizontalBarChart` and `YAxisRendererHorizontalBarChart`. `PieChart` has no axis renderers at all, and `RadarChart` names its two differently: `xAxisRenderer` of type `XAxisRendererRadarChart` and `yAxisRenderer` of type `YAxisRendererRadarChart`. `legendRenderer` is on every chart too, but its setter is protected, so you restyle it rather than replace it: `chart.legendLabelPaint` reads and writes the renderer's `labelPaint`.

## Replacing one

Assign your instance to the property. Every data renderer takes the chart, the animator and the viewport handler, in that order:

```kotlin
BarChart(
    data = barData,
    setup = {
        renderer = BadgeBarRenderer(this, animator, viewPortHandler)
    },
)
```

From a view, do the same before the data:

```kotlin
val chart = BarChart(context)
chart.renderer = BadgeBarRenderer(chart, chart.animator, chart.viewPortHandler)
chart.data = barData
```

Order matters. Setting `chart.data` calls `notifyDataSetChanged()`, and that is what calls `renderer.initBuffers()`. Assign the renderer first and the buffers are built for you. Assign it afterwards and you have to call `chart.notifyDataSetChanged()` yourself, or the first draw will read buffers that were never filled. The Compose `setup` lambda runs once after the view is created and before any data is set, which is exactly the right moment.

An axis renderer needs the axis it draws and a transformer instead of the animator:

```kotlin
chart.rendererXAxis = TickedXAxisRenderer(
    chart.viewPortHandler,
    chart.xAxis,
    chart.getTransformer(YAxis.AxisDependency.LEFT),
)
```

`XAxisRendererHorizontalBarChart` takes a fourth argument, the `BarChart` itself. The two radar axis renderers take `(viewPortHandler, axis, chart)` and no transformer, because a radar chart places its labels from the center and the slice angle rather than through a matrix. Note that `chart.renderer` is typed `DataRenderer`, so reading it back for anything type specific needs a cast.

## A worked example

Draw every bar value on a soft rounded badge. The only override is `drawValue`, so all the positioning, the stacked case, the icons and the bounds checks stay as they are:

```kotlin
class BadgeBarRenderer(
    chart: BarDataProvider,
    animator: ChartAnimator,
    viewPortHandler: ViewPortHandler,
) : BarChartRenderer(chart, animator, viewPortHandler) {

    private val badgePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.argb(30, 0, 0, 0)
    }
    private val badge = RectF()

    override fun drawValue(
        c: Canvas,
        formatter: IValueFormatter,
        value: Float,
        entry: Entry<*>,
        dataSetIndex: Int,
        x: Float,
        y: Float,
        color: Int,
    ) {
        val text = formatter.getFormattedValue(
            value, entry, dataSetIndex, viewPortHandler
        )
        val padding = Utils.convertDpToPixel(3f)
        val half = paintValues.measureText(text) / 2f + padding
        badge.set(x - half, y - paintValues.textSize, x + half, y + padding)
        c.drawRoundRect(badge, padding, padding, badgePaint)
        super.drawValue(c, formatter, value, entry, dataSetIndex, x, y, color)
    }
}
```

The constructor takes `BarDataProvider`, not `BarChart`, because that is what `BarChartRenderer` declares, and `y` is the text baseline rather than the top of the label.

To change the bars themselves rather than their labels, override `drawDataSet(c, dataSet: IBarDataSet<*>, index: Int)` on the same class, or `drawDataSet(c, dataSet: ILineDataSet<*>)` on `LineChartRenderer`, or `drawDataSet(c, dataSet: IPieDataSet<*>)` on `PieChartRenderer`. `LineChartRenderer` also opens up `drawLinear`, `drawCubicBezier`, `drawHorizontalBezier`, `drawCubicFill`, `drawLinearFill`, `drawCircles` and `drawHighlightCircle` one by one, so you rarely have to replace a whole line path.

## The draw order

`Chart.onDraw` itself draws almost nothing: it draws the empty state (`drawEmptyState`) when there is nothing to show and calculates the offsets once. Everything else lives in the subclass. `BarLineChartBase.onDraw` runs this sequence on every frame:

1. the grid background, then `autoScale()` when `isAutoScaleMinMaxEnabled`
2. `computeAxis` on the left y, right y and x axis renderers, for the enabled axes
3. `renderAxisLine` on all three
4. `renderGridLines` and then `renderLimitLines` for every axis with `isDrawGridLinesBehindDataEnabled` or `isDrawLimitLinesBehindDataEnabled` set
5. the canvas is saved and clipped to `viewPortHandler.contentRect` when `isClipDataToContentEnabled`
6. `renderer.drawData`
7. `renderGridLines` for the axes that draw their grid in front of the data
8. `renderer.drawHighlighted`, only when something is highlighted
9. the clip is restored, then `renderer.drawExtras`
10. `renderLimitLines` for the axes that draw in front
11. `renderAxisLabels` on all three axis renderers
12. `renderer.drawValues`, clipped again when `isClipValuesToContentEnabled`
13. `legendRenderer.renderLegend`, the description, the markers

So `drawData` is clipped to the content rectangle and `drawExtras` is not. A line chart relies on that: it draws its circles in `drawExtras` so a circle at the very edge is not sliced in half.

`PieChart.onDraw` is far shorter: `drawData`, `drawHighlighted`, `drawExtras`, `drawValues`, legend, description, markers. `RadarChart.onDraw` calls `drawExtras` first of all when `isDrawWebEnabled`, so the web ends up behind the polygons.

## What every renderer reads

Two objects are handed to every renderer and are the reason it can stay stateless. The **animator** supplies `phaseX` and `phaseY`, both 1 when nothing is animating. `phaseX` is a fraction of the entry count: a renderer stops its loop at `entryCount * phaseX`, which is why an x animation reveals entries one by one. `phaseY` multiplies the y value of each entry before it is transformed, which is why a y animation grows the shapes out of the zero line. Respect both or your renderer will ignore [the animations](/mpandroidchart/docs/animations/).

The **viewport handler** is the content rectangle and the current zoom, in pixels. Renderers use `contentLeft`, `contentTop`, `contentRight`, `contentBottom` to draw and `isInBoundsLeft(x)`, `isInBoundsRight(x)`, `isInBoundsY(y)` and `isInBounds(x, y)` to skip what is off screen. The full API is in [the ViewPortHandler](/mpandroidchart/docs/viewporthandler/). The pattern below is worth copying, because the two checks are not symmetric:

```kotlin
if (!viewPortHandler.isInBoundsRight(pixel)) break
if (!viewPortHandler.isInBoundsLeft(pixel)) continue
```

Entries arrive in ascending x, so once one is past the right edge every later one is too and the loop can stop. One before the left edge only means this one is skipped.

## The data provider interfaces

A renderer never names a chart class. It is written against a small interface in `interfaces.dataprovider`, which is what lets `CombinedChart` reuse all five data renderers unchanged.

| Interface | Adds | Read by |
| --- | --- | --- |
| `ChartInterface` | `data`, `contentRect`, `maxVisibleCount`, the value and pixel ranges | every renderer and marker |
| `BarLineScatterCandleBubbleDataProvider` | `getTransformer(axis)`, `isInverted(axis)`, `lowestVisibleX`, `highestVisibleX` | the renderers with axes |
| `BarDataProvider` | `barData`, `isDrawBarShadowEnabled`, `isDrawValueAboveBarEnabled`, `isHighlightFullBarEnabled` | `BarChartRenderer` |
| `LineDataProvider` | `lineData`, `getAxis(axis)` | `LineChartRenderer` |
| `ScatterDataProvider` | `scatterData` | `ScatterChartRenderer` |
| `CandleDataProvider` | `candleData` | `CandleStickChartRenderer` |
| `BubbleDataProvider` | `bubbleData` | `BubbleChartRenderer` |
| `CombinedDataProvider` | `combinedData`, extends the five above | `CombinedHighlighter` |

`PieChartRenderer` and `RadarChartRenderer` are the exceptions. They take `PieChart` and `RadarChart` directly, because they need the center, the radius and the rotation angle, none of which are on an interface. Take the narrowest interface that gives you what you need and your renderer works on the combined chart as well as on the single type chart.

## The combined chart renderer

`CombinedChartRenderer` draws nothing itself. It owns `subRenderers`, a mutable list of `DataRenderer`, and forwards all four draw functions plus `initBuffers` to each entry in order. `createRenderers()` rebuilds that list. It walks `chart.drawOrder` and adds a renderer only for a data kind that is actually present, so a combined chart holding line and bar data gets exactly two sub renderers, in the order the draw order lists them. The list is rebuilt for you whenever you set `chart.data`, and you only call `createRenderers()` by hand after changing `drawOrder` without setting data again. `drawHighlighted` is the one function that does not simply forward. It matches each highlight against the data index of the sub renderer's own data and passes on only the highlights that belong to it, plus any with a data index of -1, which are meant for every renderer.

`getSubRenderer(index)` returns an entry or null when the index is out of range. Replacing one entry in `subRenderers` is how you change a single data kind inside a combined chart, but do it after the data is set, because the data setter rebuilds the whole list.

## Buffers

Drawing runs on every frame, so the bar renderers keep their coordinates in a reusable `FloatArray` rather than allocating one. `AbstractBuffer<T>` is that array plus a write position: `buffer` holds the floats, `feed(data)` fills them, `setPhases(phaseX, phaseY)` sets the animation phases used by the next feed, and `reset()` moves the write position back to the start.

`BarBuffer` is the bar layout: four floats per bar, left, top, right and bottom, in value space. Left and right are `x - barWidth / 2` and `x + barWidth / 2`; top and bottom span from the bar value to zero, swapped when the y axis is inverted. A stacked entry produces one rectangle per stack value. `HorizontalBarBuffer` keeps the same four floats but swaps their meaning: left and right are y values, top and bottom are x values.

`BarChartRenderer.initBuffers` creates one buffer per data set, sized `entryCount * 4`, times the stack size for a stacked set. `drawDataSet` then feeds the buffer, converts the whole array to pixels in one `trans.pointValuesToPixel(buffer.buffer)` call and steps through it four floats at a time. One matrix call for a whole data set is the reason the buffers exist. Only the bar renderers use them. `ScatterChartRenderer`, `CandleStickChartRenderer`, `RadarChartRenderer` and `PieChartRenderer` all have an empty `initBuffers`, and `LineChartRenderer` uses an offscreen bitmap instead, and only for the modes that need one.

## Scatter shape renderers

The smallest custom drawing hook in the library is not a renderer subclass at all. `IShapeRenderer` is a `fun interface` with a single `renderShape(c, dataSet, viewPortHandler, posX, posY, renderPaint)`, which `ScatterChartRenderer` calls once per entry with the pixel position already worked out and `renderPaint` already set to the color of that entry. A lambda is enough:

```kotlin
val set = ScatterDataSet(entries, "Points")
set.shapeRenderer = IShapeRenderer { c, dataSet, _, x, y, paint ->
    val half = Utils.convertDpToPixel(dataSet.scatterShapeSize) / 2f
    c.drawLine(x - half, y - half, x + half, y + half, paint)
}
```

The built-in implementations are `SquareShapeRenderer` (the default on `ScatterDataSet`), `CircleShapeRenderer`, `TriangleShapeRenderer`, `CrossShapeRenderer`, `XShapeRenderer`, `ChevronUpShapeRenderer` and `ChevronDownShapeRenderer`, and `set.setScatterShape(ScatterChart.ScatterShape.CIRCLE)` is a shortcut that installs one of them. `scatterShapeSize` and `scatterShapeHoleRadius` are both in dp, and every one of them converts with `Utils.convertDpToPixel` before drawing, so do the same if you want your shape to match the others.

## What a renderer must not do

> A draw function runs on the UI thread up to sixty times a second, once per data set, and often once per visible entry. Everything written here follows from that.

**Do not allocate in a draw function.** No `Paint`, no `Path`, no `RectF`, no `FloatArray`, no boxing. Create them as fields, as the built-in renderers do with `barRect`, `barShapePath` and the various float buffers. For points, use `MPPointF.getInstance(...)` and hand the instance back with `MPPointF.recycleInstance(...)` when you are done.

**Do not hold a strong reference that outlives the chart.** A renderer is reachable from the view, so holding the view back is not itself a leak, but anything longer lived that holds your renderer then holds the whole view hierarchy. `CombinedChartRenderer` and `LineChartRenderer` both use a `java.lang.ref.WeakReference` for exactly this reason, and both handle the reference having been cleared.

**Do not skip the bounds checks.** Without `xBounds` and the `isInBounds` calls you transform and draw every entry in the data set, including the thousands that are off screen. That is the difference between a chart that scrolls smoothly and one that does not.

And keep dp conversions inside `Utils.convertDpToPixel` rather than hard coding pixel values, so your renderer looks the same on every screen density.
