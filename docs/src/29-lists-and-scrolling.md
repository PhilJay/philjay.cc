# Charts in lists and scrolling screens

How to put a chart into a LazyColumn, a recycled row, a fragment or a scrolling screen without rebuilding data on every frame or fighting the parent for the gesture.

## A chart in a LazyColumn

The rule for a list is always the same: the data is built once, somewhere the list does not throw away, and the item only shows it.

```kotlin
@Composable
fun ReportList(reports: List<Report>) {
    val charts = remember(reports) {
        reports.associate { it.id to lineDataFor(it) }
    }

    LazyColumn {
        items(reports, key = { it.id }) { report ->
            LineChart(
                data = charts[report.id],
                modifier = Modifier.fillMaxWidth().height(200.dp),
                setup = {
                    description.isEnabled = false
                    legend.isEnabled = false
                    axisRight.isEnabled = false
                    isDragEnabled = false
                    isScaleEnabled = false
                },
            )
        }
    }
}
```

**Build the data above the list.** A `remember` written inside the item body belongs to that item's composition. When the row scrolls out the composition goes away and the data is built again on the way back, in the middle of a fling. Keep the finished `LineData` in a view model or in a `remember` above the `LazyColumn`, as above.

**Give the item a fixed height.** `Chart.onMeasure` resolves the measure spec against a default size of 50 dp, so a chart that is measured with an unbounded height ends up 50 dp tall. That is `Modifier.height(200.dp)` in Compose and a real `android:layout_height` in XML, never `wrap_content`.

> A chart with `wrap_content` inside a `ScrollView` or a list row collapses to a 50 dp strip. It is the most common layout surprise with this library.

**What a recomposition costs.** The composable compares `data` by identity. A new instance is assigned to the chart, and the setter calls `notifyDataSetChanged()`, which walks every entry to recompute the ranges, recomputes the legend and the offsets and redraws. Passing the same instance skips all of that and only runs your `update` lambda and a redraw. Building a `LineData` in the item body means paying the full recalculation on every recomposition of that row.

**The chart view is not reused.** The wrapper creates the chart through `AndroidView` without an `onReset`, so a row that leaves the viewport is disposed and comes back as a freshly created chart. Keep `setup` cheap: no file reading, no typeface loading. Resolve a typeface once with `rememberTypeface` outside the list and let `setup` capture it.

**Give the items a key.** `rememberChartState()` is a `rememberSaveable`, so a stable item key is what makes a saved selection or zoom come back on the row it belongs to instead of on its neighbour.

**Switch the gestures off.** A row is there to be read, and a chart that pans competes with the list for the same vertical drag. See [A chart inside a scrolling parent](#a-chart-inside-a-scrolling-parent).

## A chart in a recycled row

`ListViewBarChartActivity` in the example app builds twenty `BarData` objects in `onCreate` and hands the list to an adapter. That order is the point: the data exists before the first row is bound, so binding is only an assignment.

With a `RecyclerView`, configure the chart when the holder is created and assign data when it is bound:

```kotlin
class ChartAdapter(private val items: List<BarData>) :
    RecyclerView.Adapter<ChartAdapter.Holder>() {

    class Holder(val binding: ListItemBarchartBinding) :
        RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder {
        val binding = ListItemBarchartBinding.inflate(
            LayoutInflater.from(parent.context), parent, false,
        )
        binding.chart.apply {
            description.isEnabled = false
            legend.isEnabled = false
            isDragEnabled = false
            isScaleEnabled = false
            axisRight.isEnabled = false
            xAxis.position = XAxis.XAxisPosition.BOTTOM
            axisLeft.labelCount = 5
        }
        return Holder(binding)
    }

    override fun onBindViewHolder(holder: Holder, position: Int) {
        holder.binding.chart.apply {
            highlightValues(emptyList())
            fitScreen()
            data = items[position]
        }
    }

    override fun getItemCount() = items.size
}
```

**Reset what the previous row left behind.** A recycled chart still carries the highlight, the zoom and the pan of the row it showed before. Assigning `data` does not touch any of them: it recalculates and redraws, nothing more. `highlightValues(emptyList())` clears the selection and `fitScreen()` undoes zoom and drag. If the rows have no gestures, the two lines cost nothing and protect you the day someone enables dragging.

**No `invalidate()` after assigning data.** The setter already redraws. An extra call only queues a second draw.

**Usually do not animate on bind.** The example calls `animateY(700)` in `getView`, which is fine for a demo screen. In a real list, bind is not a "this row appeared" callback: a fling binds dozens of rows, each restarts an animation, and every running animation keeps invalidating its chart for the whole duration. If you want the entrance animation, run it once per item, for example from `onViewAttachedToWindow` guarded by the set of ids you have already animated.

**One listener per row.** `onChartValueSelectedListener` holds a single listener, so assigning a new one in bind replaces the old one and the row cannot end up reporting the previous item's position.

## Several chart types in one list

`ListViewMultiChartActivity` mixes line, bar and pie rows. Each row is a `ChartItem` that already holds its finished `ChartData` and knows its `itemType`, one of `TYPE_BARCHART`, `TYPE_LINECHART` or `TYPE_PIECHART`, and the adapter reports that through `getItemViewType` with `getViewTypeCount` of 3. Without the view types a bar row would be handed the layout of a line row.

In a `RecyclerView` the same idea is a sealed type:

```kotlin
sealed interface ChartRow {
    data class Line(val data: LineData) : ChartRow
    data class Bar(val data: BarData) : ChartRow
    data class Pie(val data: PieData) : ChartRow
}

override fun getItemViewType(position: Int) = when (rows[position]) {
    is ChartRow.Line -> 0
    is ChartRow.Bar -> 1
    is ChartRow.Pie -> 2
}
```

Give each type its own layout and its own holder, and style each chart in `onCreateViewHolder` as above.

Anything that depends only on the data belongs to the data, not to the bind step. The example's pie rows set a `PercentFormatter`, the value typeface, the value size and the value color inside `getView`, which repeats that work on every bind. Do it once, where the `PieData` is built.

In Compose the list is a `when` inside the item, and each branch calls a different composable:

```kotlin
items(rows, key = { it.id }, contentType = { it::class }) { row ->
    when (row) {
        is ChartRow.Line -> LineChart(row.data, chartModifier)
        is ChartRow.Bar -> BarChart(row.data, chartModifier)
        is ChartRow.Pie -> PieChart(row.data, chartModifier)
    }
}
```

The `contentType` keeps the slots of the three chart types apart, so Compose does not try to reuse a pie row's composition for a bar row.

## A chart inside a scrolling parent

`ScrollViewActivity` puts a 450 dp bar chart between two spacers inside a `ScrollView`. Both the chart and the scroller want the vertical drag, and only one of them can have it.

The chart claims the gesture late. `BarLineChartTouchListener` calls `chart.disableScroll()` once a second finger goes down or once a drag is actually under way, and `chart.enableScroll()` when the touch ends. Until the drag is recognised the parent may already have taken the gesture, which is why a slow vertical swipe that starts on a chart often scrolls the page instead.

There are two honest answers.

**Take the gestures away.** In a row or a long form the chart is a picture, so let the parent scroll:

```kotlin
chart.isDragEnabled = false
chart.isScaleEnabled = false
chart.isDoubleTapToZoomEnabled = false
```

`isHighlightPerTapEnabled` stays on, so a tap still selects a value. This is the reliable option, and the only one worth using for a chart inside a `LazyColumn`.

**Or claim the gesture as soon as a finger lands.** `onChartGestureStart` fires on the touch down, before any gesture is recognised, which is early enough to lock the parent out:

```kotlin
chart.onChartGestureListener = object : OnChartGestureListener {

    override fun onChartGestureStart(
        me: MotionEvent,
        lastPerformedGesture: ChartTouchListener.ChartGesture,
    ) = chart.disableScroll()

    override fun onChartGestureEnd(
        me: MotionEvent,
        lastPerformedGesture: ChartTouchListener.ChartGesture,
    ) = chart.enableScroll()
}
```

`disableScroll()` and `enableScroll()` are just `requestDisallowInterceptTouchEvent` on the parent, so they work the same in a `ScrollView`, a `NestedScrollView`, a `ViewPager2` or a `RecyclerView`. The price is that the user can no longer scroll the page by starting the swipe on the chart, so reserve it for a chart that is the point of the screen. The rest of `OnChartGestureListener` is in [Interaction with the chart](/mpandroidchart/docs/interaction/).

## Fragments and pager pages

The fragments in the example app share a `SimpleFragment` base that only generates data, and each page builds its chart in `onCreateView` from those generators. `PieChartFrag` styles the chart from its binding; `BarChartFrag` creates the `BarChart` in code and adds it to the layout. Both work.

In `onDestroyView`, null your binding and any chart reference you kept. The chart dies with the view hierarchy, and nothing in the library needs an explicit teardown. A Compose chart cleans up on its own: the wrapper detaches the state and releases the marker when the composable leaves.

`chart.isUnbindEnabled` is not a teardown hook, whatever the name suggests. It defaults to false, and while it is true `onDetachedFromWindow` clears the callback of the chart's background drawable and removes the chart's child views, walking down the tree. It does not release the data, the renderers or the paints. It fires on every detach, including a row scrolling out of a list or a pager page being detached, and the marker of a Compose chart lives in a child view of the chart, so a chart that gets reattached comes back without it. Leave it off unless you are chasing a measured leak on an old device.

On a pager, watch the offscreen pages. `SimpleChartDemo` sets `offscreenPageLimit = 3`, which keeps three pages alive on each side of the current one, so all five demo pages hold a live chart with its data at the same time. That is fine for five design demos and wrong for a pager over a long list: keep the default limit of 1 and rebuild, or hold the data in a view model so only the views are recreated. The same applies to entrance animations. A page that is created ahead of time starts its `animateY` while it is off screen and has finished before the user swipes to it, so start the animation when the page becomes visible instead of in `onCreateView`.

## Performance in a list

Twenty charts on screen means twenty views measuring, laying out and drawing. The cheap wins are: turn off what you do not need per row with `description.isEnabled = false` and `legend.isEnabled = false`, set `isDrawValuesEnabled = false` on the data sets, and keep the entry count per row small. Value labels stop being drawn on their own once the entry count reaches `maxVisibleCount`, which defaults to 100 on the charts with axes.

Everything else, including `isHardwareAccelerationEnabled` and what to do with large data sets, is in [Performance](/mpandroidchart/docs/performance/).
