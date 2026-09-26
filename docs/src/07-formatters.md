# Formatting values

How to control the text of the values drawn next to the entries and of the labels on the axes.

Two small interfaces do all of it. Both are `fun interface`s with non-null parameters, so a lambda is usually the whole implementation.

```kotlin
chart.axisLeft.valueFormatter = IAxisValueFormatter { value, _ -> "${value.toInt()} €" }
barDataSet.valueFormatter = IValueFormatter { v, _, _, _ -> "${v.roundToInt()}%" }
```

## The two interfaces

`IValueFormatter` formats the values drawn inside the chart, next to each entry. It gets the entry and its data set index, so it can look at more than the number:

```kotlin
fun getFormattedValue(
    value: Float,
    entry: Entry<*>,
    dataSetIndex: Int,
    viewPortHandler: ViewPortHandler,
): String
```

`IAxisValueFormatter` formats axis labels. It gets the axis, which carries the current range and the computed decimals:

```kotlin
fun getFormattedValue(value: Float, axis: AxisBase): String
```

> Version 3 had a single `ValueFormatter` class with one overridable method per chart type. Version 4 is back to these two interfaces, and every argument is non-null, so there is nothing to null check.

Both run for every drawn value on every frame. Build your `DecimalFormat`, `SimpleDateFormat` or label list once, outside the function, and keep the body free of allocations.

## Where to set them

| Target | How | Applies to |
| --- | --- | --- |
| One data set | `set.valueFormatter = ...` | the values of that series |
| All sets of a chart | `data.setValueFormatter(...)` | every set in the data object |
| One axis | `chart.xAxis.valueFormatter = ...` | that axis' labels |

```kotlin
val data = LineData(revenue, costs)
data.setValueFormatter(MyValueFormatter())
chart.data = data
```

`setValueFormatter` on the data object is a function that walks the sets it holds right now, so call it after you have added all of them.

Values are only drawn when the set asks for them:

```kotlin
lineDataSet.isDrawValuesEnabled = true
```

## What happens when you set nothing

Assigning `chart.data` sizes a `DefaultValueFormatter` from the y range of the data and hands it to every set that has no formatter of its own. Small numbers get decimal digits and large ones do not, without you doing anything.

An axis behaves the same way: while no formatter is assigned it returns a `DefaultAxisValueFormatter` built from its computed `decimals`, which follow the label interval.

## The built in formatters

| Class | Result | Usable as |
| --- | --- | --- |
| `DefaultValueFormatter(digits)` | `1,234.50` | value formatter |
| `DefaultAxisValueFormatter(digits)` | `1,234.50` | axis formatter |
| `IndexAxisValueFormatter(values)` | one fixed label per whole x value | axis formatter |
| `LargeValueFormatter(appendix)` | `102k`, `7.8m`, `1b` | both |
| `PercentFormatter(format)` | `12.5 %` | both |
| `StackedValueFormatter(...)` | one label per stack, or one per bar | value formatter |

### IndexAxisValueFormatter

The one you reach for on the x axis when your entries sit at x = 0, 1, 2 and each needs a name.

```kotlin
val months = listOf("Jan", "Feb", "Mar", "Apr", "May", "Jun")

chart.xAxis.apply {
    valueFormatter = IndexAxisValueFormatter(months)
    granularity = 1f
}
```

It rounds the axis value and returns the label at that index. Two cases give an empty string instead: an index outside the list, and a value whose fraction is 0.5 or more. In other words the label of index `n` appears for values from `n` up to, but not including, `n + 0.5`. That is why the granularity of 1 belongs with it. Without it, zooming in produces values like 2.5 and 2.75, and the labels simply vanish.

The list can be swapped later through the `values` property, without building a new formatter.

### LargeValueFormatter

Shortens numbers with a suffix per power of one thousand: `""`, `k`, `m`, `b`, `t`.

```kotlin
chart.axisLeft.valueFormatter = LargeValueFormatter()
```

| Input | Output |
| --- | --- |
| 856 | `856` |
| 5821 | `5.8k` |
| 101800 | `102k` |
| 7800000 | `7.8m` |
| 1000000000 | `1b` |

`appendix` adds a unit after the number and `suffix` replaces the five strings with a list of your own, such as `suffix = listOf("", "K", "M", "B", "T")`. A scaled value of 100 or more is printed without decimals, below that with one, so 5821 reads `5.8k` and 101800 reads `102k`. It is built for numbers of 1 and above: anything under 0.05 comes out as `0`.

### PercentFormatter

Appends a percent sign, with one decimal digit unless you pass your own `DecimalFormat`.

```kotlin
pieDataSet.valueFormatter = PercentFormatter()
pieChart.isUsePercentValuesEnabled = true
```

The pie chart setting matters: without it the formatter puts a percent sign after the raw value.

### StackedValueFormatter

For stacked bars, where you either label every stack value or only the total.

```kotlin
barData.setValueFormatter(StackedValueFormatter(false, " €", 0))
```

With `false` the total is drawn once, at the topmost stack value of each bar, and the other stack values come back empty. With `true` every stack value gets its own label.

A formatter of your own that needs to know where in the stack a value sits can override `getStackedFormattedValue(value, stackIndex, entry, dataSetIndex, viewPortHandler)`, which the bar renderers call instead of `getFormattedValue`. Its default forwards to `getFormattedValue`, so a plain lambda formatter keeps working.

## Writing your own

### A currency

```kotlin
private val currency = DecimalFormat("###,###,##0.00")

chart.axisLeft.valueFormatter = IAxisValueFormatter { value, _ ->
    currency.format(value.toDouble()) + " €"
}
```

### A percentage on a bar chart

```kotlin
barDataSet.valueFormatter = IValueFormatter { value, _, _, _ ->
    "${value.roundToInt()}%"
}
```

### Month names from a timestamp

Keep the x value a number and turn it into text in the formatter. Nothing is stored twice this way, and zooming keeps working.

```kotlin
private val month = SimpleDateFormat("MMM", Locale.getDefault())

chart.xAxis.apply {
    granularity = 1f
    valueFormatter = IAxisValueFormatter { value, _ ->
        month.format(Date(TimeUnit.DAYS.toMillis(value.toLong())))
    }
}
```

An axis formatter can also look at the axis it is given, for example to write shorter labels once the visible range gets wide:

```kotlin
private val day = SimpleDateFormat("d MMM", Locale.getDefault())
private val month = SimpleDateFormat("MMM yyyy", Locale.getDefault())

chart.xAxis.valueFormatter = IAxisValueFormatter { value, axis ->
    val date = Date(TimeUnit.DAYS.toMillis(value.toLong()))
    if (axis.axisRange > 180f) month.format(date) else day.format(date)
}
```

### Reading the entry payload

Entries are generic in their payload, so a value formatter can print something the chart never knew about, like an order number or a product name.

```kotlin
data class Order(val id: String, val total: Float)

val entries = orders.mapIndexed { i, order ->
    Entry(i.toFloat(), order.total, data = order)
}

val set = LineDataSet(entries, "Orders").apply {
    valueFormatter = IValueFormatter { _, entry, _, _ ->
        (entry.data as? Order)?.id ?: ""
    }
}
```

The interface hands you an `Entry<*>`, so the payload arrives as `Any?` and needs the cast. For a bar chart you can cast the entry itself instead, to reach `BarEntry` details such as the stack values.

## One more formatter

`IFillFormatter` is the third of them. It decides how far the fill under a line reaches rather than how a number reads, so it has its own chapter: [the fill formatter](/mpandroidchart/docs/fillformatter/).

## Next

- [The axis](/mpandroidchart/docs/axis/) for where axis labels come from in the first place.
- [The x axis](/mpandroidchart/docs/xaxis/) for the index and date recipes in context.
- [Markers](/mpandroidchart/docs/markers/) for text shown on a highlighted value instead of next to every one.
