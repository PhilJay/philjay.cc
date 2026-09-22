# The description

The small label drawn in the bottom right corner of a chart's content area, and the handful of properties that place and style it.

Every chart has one, reached as `chart.description`. It is drawn by default with the placeholder text "Description Label", so the first thing most charts do is turn it off.

```kotlin
chart.description.isEnabled = false
```

## Text

```kotlin
chart.description.text = "Revenue per quarter, in thousands"
```

It is a single line of plain text. There is no wrapping and no formatting, so keep it short or place it where there is room.

## Position

By default the text sits in the bottom right corner of the content area, pushed in from its right edge by `xOffset` and up from its bottom edge by `yOffset`, both in dp and both 5 by default.

```figure
<svg viewBox="0 0 620 216" width="100%" role="img" aria-label="Where the description is drawn" style="max-width:620px;height:auto;display:block;margin:0 auto 6px">
<title>Where the description is drawn</title>
<rect x="48.0" y="52.0" width="420.0" height="120.0" rx="6" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
<path d="M48.0 131.2 L108.0 110.1 L168.0 123.5 L228.0 90.9 L288.0 107.2 L348.0 77.4 L408.0 98.6 L468.0 115.8" fill="none" stroke="#00a9ab" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
<text x="452.0" y="158.0" fill="rgba(255,255,255,0.78)" font-size="12.5" text-anchor="end">Revenue 2026</text>
<rect x="336.0" y="138.0" width="126.0" height="28.0" rx="4" fill="none" stroke="rgba(255,255,255,0.10)" stroke-width="1" stroke-dasharray="3 3"/>
<line x1="462.0" y1="152.0" x2="484.0" y2="152.0" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<text x="490.0" y="156.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="start">xOffset in</text>
<text x="490.0" y="169.0" fill="rgba(255,255,255,0.5)" font-size="10.5" text-anchor="start">yOffset up</text>
<text x="48.0" y="32.0" fill="rgba(255,255,255,0.5)" font-size="11.5" text-anchor="start">The description sits in the bottom right corner unless you place it</text>
</svg>
```

```kotlin
chart.description.xOffset = 12f
chart.description.yOffset = 12f
```

For anything else, give it a fixed position. The coordinates are in pixels on the chart view, measured from the top left corner, and the y coordinate is the text baseline rather than the top of the text.

```kotlin
chart.description.setPosition(24f, 48f)
```

Reading `description.position` gives you the point that was set, or null while the corner placement is in use.

> The offsets are in dp and the position is in pixels. Convert with `Utils.convertDpToPixel(dp)` if you want a fixed position that holds up across densities.

## Styling

```kotlin
chart.description.apply {
    textColor = Color.GRAY
    textSize = 10f
    typeface = tfLight
    textAlign = Paint.Align.RIGHT
}
```

| Property | Meaning | Default |
| --- | --- | --- |
| `isEnabled` | Whether the text is drawn at all | `true` |
| `text` | The text | `"Description Label"` |
| `textColor` | Text color | black |
| `textSize` | Text size in dp, clamped to 6 until 24 | `8` |
| `typeface` | Typeface, or null for the default | `null` |
| `textAlign` | How the text sits relative to its position | `Paint.Align.RIGHT` |
| `position` | Fixed position in pixels, or null for the corner | `null` |
| `xOffset`, `yOffset` | Distance in dp from the corner | `5` |

`textAlign` matters most together with a fixed position: `RIGHT` makes the position the right end of the text, `LEFT` the left end and `CENTER` its middle.

These properties are copied into `chart.descriptionPaint` before every draw, so set them on the description and use the paint only for things the description does not expose, such as a shadow layer.

That is the last of the individual styling pieces. [Theming a chart](/mpandroidchart/docs/theming/) puts them together into one look you can share across a whole app.
