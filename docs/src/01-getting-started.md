# Getting started

Everything you need to put a first chart on screen: the dependency, the view, and the three classes that hold your data.

## Requirements

The library targets Android 6.0 and newer.

| | |
| --- | --- |
| `minSdk` | 23 |
| `compileSdk` | 35, or 37 for the Compose module |
| Java | 17 |
| Kotlin | 2.0 or newer, and none at all for Java callers |
| Language | Kotlin, with Java callers supported |

Coming from version 3.x? Every getter and setter pair is a property now, and entries carry a typed payload. [Migrating from 3.x](/mpandroidchart/docs/migration/) walks through every change with before and after code.

## Add the dependency

4.0 is a beta. Its coordinates differ from the 3.x ones, so a project still on `com.github.PhilJay:MPAndroidChart:v3.1.0` is untouched by it. Pin the version rather than tracking the newest one.

The library is published through JitPack. Add the repository in `settings.gradle.kts`:

```kotlin
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        maven("https://jitpack.io")
    }
}
```

Then add the dependency in your module's `build.gradle.kts`:

```kotlin
dependencies {
    implementation("com.github.PhilJay.MPAndroidChart:MPChartLib:v4.0.0-beta01")

    // only if you use Jetpack Compose
    implementation("com.github.PhilJay.MPAndroidChart:MPChartCompose:v4.0.0-beta01")
}
```

## Create the chart

In Compose, use the composable of the same name from the `MPChartCompose` module:

```kotlin
LineChart(
    data = lineData,
    modifier = Modifier.fillMaxWidth().height(300.dp),
)
```

With views, every chart type is a `View`, so put one in a layout:

```xml
<com.github.mikephil.charting.charts.LineChart
    android:id="@+id/chart"
    android:layout_width="match_parent"
    android:layout_height="300dp" />
```

And get hold of it in your activity or fragment:

```kotlin
val chart = findViewById<LineChart>(R.id.chart)
```

You can also create one in code and add it to a container:

```kotlin
val chart = LineChart(this)
container.addView(chart, MATCH_PARENT, dpToPx(300))
```

The chart types are `LineChart`, `BarChart`, `HorizontalBarChart`, `PieChart`, `ScatterChart`, `CandleStickChart`, `BubbleChart`, `RadarChart` and `CombinedChart`.

## The three classes that hold data

Data always follows the same shape, whichever chart you use.

1. An **entry** is one value. `Entry(x, y)` for a line or scatter point, `BarEntry` for a bar, `PieEntry` for a slice, and so on.
2. A **data set** is one series plus its styling: color, line width, whether values are drawn. `LineDataSet`, `BarDataSet`, `PieDataSet`.
3. A **data object** holds every series of the chart and is what you assign to it. `LineData`, `BarData`, `PieData`.

```kotlin
val entries = listOf(
    Entry(0f, 4f),
    Entry(1f, 8f),
    Entry(2f, 6f),
    Entry(3f, 12f),
)

val set = LineDataSet(entries, "Sales").apply {
    color = Color.BLUE
    lineWidth = 2f
    circleRadius = 4f
    isDrawValuesEnabled = false
}

chart.data = LineData(set)
```

Assigning `chart.data` recalculates the axes, the legend and the offsets, then redraws. Nothing else is needed to see the chart.

> Entries must be sorted by their x value. `DataSet.addEntryOrdered` inserts at the right place if you are adding to an existing set.

## Add a second series

A data object takes several data sets. Each one keeps its own styling and legend entry.

```kotlin
val revenue = LineDataSet(revenueEntries, "Revenue").apply { color = Color.BLUE }
val costs = LineDataSet(costEntries, "Costs").apply { color = Color.RED }

chart.data = LineData(revenue, costs)
```

## Change the data later

There are two ways, and they differ in one detail.

Replacing the data object applies everything at once:

```kotlin
chart.data = LineData(newSet)
```

Changing entries in place needs one call afterwards, which recalculates and redraws:

```kotlin
set.entries = newEntries.toMutableList()
chart.notifyDataSetChanged()
```

> In version 3.x you had to call `notifyDataSetChanged()` on the data set, on the data object and on the chart, then `invalidate()`. One call on the chart now does all of it.

## A first look at styling

Everything is a property. A few you will reach for immediately:

```kotlin
chart.description.isEnabled = false          // the label in the bottom right corner
chart.legend.isEnabled = true                // the series legend
chart.axisRight.isEnabled = false            // hide the second y axis
chart.xAxis.position = XAxis.XAxisPosition.BOTTOM
chart.noDataText = "Nothing to show yet"
chart.animateX(600)                          // reveal the data from left to right
```

## Where to go next

- [Setting data](/mpandroidchart/docs/setting-data/) for every chart type's entry and data set classes.
- [The axis](/mpandroidchart/docs/axis/) for labels, ranges, grid lines and limit lines.
- [General styling](/mpandroidchart/docs/general-styling/) for the settings shared by all charts.
- [Theming a chart](/mpandroidchart/docs/theming/) for the look behind the screenshots on this site.
- [Interaction with the chart](/mpandroidchart/docs/interaction/) for dragging, zooming and taps.
- The example app in the repository shows all of it running, starting with every chart type in one style.
