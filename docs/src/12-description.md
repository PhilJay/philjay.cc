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
