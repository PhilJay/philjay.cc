# Markers

The popup drawn at a highlighted value: the composable marker of the Compose module, MarkerView from a layout, MarkerImage from a drawable, and the IMarker interface behind them all.

## Show a marker

A marker is anything that implements `IMarker`. Assign one to the chart and it is drawn at every highlighted value:

```figure
<svg viewBox="0 0 660 272" width="100%" role="img" aria-label="A marker drawn over the highlighted entry" style="max-width:660px;height:auto;display:block;margin:0 auto 6px">
<title>A marker drawn over the highlighted entry</title>
<rect x="60.0" y="78.0" width="540.0" height="150.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="60.0" y1="127.5" x2="600.0" y2="127.5" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="60.0" y1="177.0" x2="600.0" y2="177.0" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<line x1="403.6" y1="78.0" x2="403.6" y2="228.0" stroke="#ffbb73" stroke-width="1.5" stroke-dasharray="6 5"/>
<path d="M60.0 177.0 L109.1 150.6 L158.2 167.4 L207.3 126.6 L256.4 147.0 L305.5 109.8 L354.5 136.2 L403.6 157.8 L452.7 143.4 L501.8 119.4 L550.9 133.8 L600.0 165.0" fill="none" stroke="#00a9ab" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="403.6" cy="157.8" r="9" fill="rgba(255,187,115,0.22)"/>
<circle cx="403.6" cy="157.8" r="5" fill="#0a1013" stroke="#00a9ab" stroke-width="2.5"/>
<path d="M403.6 146.8 l-7 -8 h14 Z" fill="rgba(255,255,255,0.10)"/>
<rect x="342.6" y="93.8" width="122.0" height="46.0" rx="8" fill="#141d21" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<text x="403.6" y="113.8" fill="rgba(255,255,255,0.5)" font-size="11" text-anchor="middle">12 March</text>
<text x="403.6" y="130.8" fill="rgba(255,255,255,0.78)" font-size="13.5" text-anchor="middle" font-weight="700">128 sold</text>
<text x="60.0" y="34.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">A marker is a view you draw over the entry that was tapped</text>
</svg>
```

```kotlin
chart.marker = MyMarkerView(context, R.layout.custom_marker_view)
```

That is the whole setup. The chart stores the marker in `chart.marker`, keeps a weak reference back to itself inside `MarkerView` and `MarkerImage`, and draws the marker whenever a value is selected. Set `chart.marker = null` to remove it.

`chart.isDrawMarkersEnabled` switches drawing off without losing the marker. It defaults to `true`, so a marker shows as soon as it is assigned.

> In version 3.x you had to call `markerView.chartView = chart` yourself. Assigning `chart.marker` does that now.

## Markers in Compose

The Compose charts take the marker as a composable, through their `marker` parameter:

```kotlin
LineChart(
    data = lineData,
    modifier = Modifier.fillMaxWidth().height(220.dp),
    marker = { entry, _ ->
        Pill("${months[entry.x.toInt()]} · ${entry.y.roundToInt()}")
    },
)

@Composable
private fun Pill(text: String) {
    Surface(color = pillBackground, shape = RoundedCornerShape(8.dp)) {
        Text(
            text,
            color = pillText,
            fontSize = 12.sp,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
        )
    }
}
```

The lambda receives the highlighted entry and its `Highlight` and is recomposed when the selection changes. Behind it sits `ComposeMarker`, which keeps an invisible `ComposeView` as a child of the chart so the content takes part in composition, and the chart draws that view at the highlighted position. It centers the content above the entry with a 12 dp gap, so no offset is needed for the usual pill; `setOffset(x, y)` shifts it from there, in dp.

Because the content composes on the next frame, a newly selected entry shows its marker one frame later. If you create a `ComposeMarker` yourself instead of using the `marker` parameter, call `detach()` when the chart should drop it.

## A MarkerView from a layout

`MarkerView` inflates a layout resource and draws it on the chart surface. The layout is an ordinary Android layout, sized with `wrap_content`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="40dp"
    android:background="@drawable/marker_background">

    <TextView
        android:id="@+id/tvContent"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_centerHorizontal="true"
        android:layout_marginTop="7dp"
        android:textColor="@android:color/white"
        android:textSize="12sp" />

</RelativeLayout>
```

Subclass `MarkerView` and override `refreshContent` to fill the views. It runs before every draw, with the highlighted entry and its `Highlight`:

```kotlin
class MyMarkerView(context: Context, layout: Int) : MarkerView(context, layout) {

    private val content = findViewById<TextView>(R.id.tvContent)

    override fun refreshContent(e: Entry<*>, highlight: Highlight) {
        content.text = Utils.formatNumber(e.y, 0, true)
        super.refreshContent(e, highlight)
    }

    override var offset: MPPointF
        get() = MPPointF(-(width / 2f), -height.toFloat())
        set(value) { super.offset = value }
}
```

Always call `super.refreshContent(e, highlight)` at the end. The base implementation measures and lays the view out again, which is what makes a marker that changed its text resize correctly.

The entry arrives as `Entry<*>`, so cast it when a chart type carries more than x and y:

```kotlin
override fun refreshContent(e: Entry<*>, highlight: Highlight) {
    val value = when {
        e is CandleEntry<*> -> e.high
        e is BarEntry<*> && highlight.isStacked ->
            e.stackValues?.get(highlight.stackIndex) ?: e.y
        else -> e.y
    }
    content.text = Utils.formatNumber(value, 0, true)
    super.refreshContent(e, highlight)
}
```

The `Highlight` also gives you `dataSetIndex`, so one marker can label several series differently. Its fields are listed in [Highlighting values](/mpandroidchart/docs/highlighting/).

## Position the marker

The chart draws the marker at the highlighted point, with the point at the marker's top left corner. `offset` shifts it from there, in pixels:

| Offset | Result |
| --- | --- |
| `MPPointF(0f, 0f)` | Top left corner sits on the value, the default |
| `MPPointF(-(width / 2f), -height.toFloat())` | Centered horizontally, sitting directly above the value |
| `MPPointF(-(width / 2f), -(height / 2f))` | Centered on the value |

Leave a gap by subtracting a few more pixels:

```kotlin
override var offset: MPPointF
    get() = MPPointF(-(width / 2f), -height - Utils.convertDpToPixel(14f))
    set(value) { super.offset = value }
```

If you do not need the size of the view, `setOffset(x, y)` is enough and no override is required:

```kotlin
marker.setOffset(-40f, -60f)
```

`MarkerView` and `MarkerImage` already keep themselves inside the chart: `getOffsetForDrawingAtPoint` takes your offset and pulls the marker back when it would be drawn past an edge. Override that function only when you want a different rule, for example flipping the marker below the value near the top of the chart.

## A MarkerImage from a drawable

When the marker is just an image, `MarkerImage` saves you a layout:

```kotlin
val marker = MarkerImage(context, R.drawable.pin).apply {
    size = FSize(48f, 48f)       // px; a 0 uses the drawable's intrinsic size
    setOffset(-24f, -48f)
}
chart.marker = marker
```

`refreshContent` does nothing here, because an image has no content to update. Subclass and override it if you want to swap the drawable per entry.

## Write an IMarker yourself

`IMarker` has four members. Implement it directly when you want to draw on the canvas rather than use a view.

| Member | Purpose |
| --- | --- |
| `val offset: MPPointF` | Offset in px from the highlighted point to the marker's top left corner |
| `getOffsetForDrawingAtPoint(posX, posY)` | The offset to use at this position; return `offset` when nothing has to change |
| `refreshContent(e, highlight)` | Update the content before drawing |
| `draw(canvas, posX, posY)` | Draw the marker; positions are in px on the chart view |

```kotlin
class DotMarker(private val paint: Paint) : IMarker {

    override val offset = MPPointF()

    override fun getOffsetForDrawingAtPoint(posX: Float, posY: Float) = offset

    override fun refreshContent(e: Entry<*>, highlight: Highlight) = Unit

    override fun draw(canvas: Canvas, posX: Float, posY: Float) {
        canvas.drawCircle(posX, posY, 12f, paint)
    }
}
```

> The function was called `getOffsetForDrawingAtPos` and the offset was `getOffset()` in version 3.x.

## When a marker is not drawn

A marker only appears when all of these hold:

- a value is highlighted, so `chart.valuesToHighlight()` is true
- `chart.marker` is not null and `chart.isDrawMarkersEnabled` is true
- the point lies inside the content area; a marker for a value scrolled out of view is skipped
- the entry index is within the current x animation phase, so markers appear as `animateX` reaches them

The position comes from `getMarkerPosition`, which returns `Highlight.drawX` and `Highlight.drawY`, written by the renderer while drawing the highlight. That is why a bar marker sits at the top center of the bar rather than at the raw touch position. `PieChart` overrides that function and computes a point inside the slice from its angles, and `HorizontalBarChart` swaps the two coordinates.
