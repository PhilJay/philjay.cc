# MPAndroidChart guides

Every chapter of the MPAndroidChart documentation, from getting started to custom data sets. Each chapter is also available as HTML without the index.md suffix. All chapters in one file: https://philjay.cc/mpandroidchart/docs/llms-full.txt

## Basics

- [Getting started](https://philjay.cc/mpandroidchart/docs/getting-started/index.md): Everything you need to put a first chart on screen: the dependency, the view, and the three classes that hold your data.

## The axes

- [The axis](https://philjay.cc/mpandroidchart/docs/axis/index.md): The settings that both axes share: which parts are drawn, how many labels there are, how the value range is chosen, and the lines you can put on top.
- [The x axis](https://philjay.cc/mpandroidchart/docs/xaxis/index.md): Where the horizontal axis sits, how its labels are drawn, and the recipes for names, dates and edge padding.
- [The y axis](https://philjay.cc/mpandroidchart/docs/yaxis/index.md): The two vertical axes of a chart: which one a data set plots against, where their labels sit, and how their value range is padded.

## Data

- [Setting data](https://philjay.cc/mpandroidchart/docs/setting-data/index.md): How to build entries, data sets and a data object for every chart type, from a single line to a combined chart.
- [Setting colors](https://philjay.cc/mpandroidchart/docs/colors/index.md): How a chart decides what color to paint each entry with, from a single line color to per-bar gradients and value label colors.
- [Formatting values](https://philjay.cc/mpandroidchart/docs/formatters/index.md): How to control the text of the values drawn next to the entries and of the labels on the axes.
- [Highlighting values](https://philjay.cc/mpandroidchart/docs/highlighting/index.md): How a value gets selected, how to select one from code, what the resulting Highlight object holds, and how to style the indicator that marks it.

## Styling

- [General styling](https://philjay.cc/mpandroidchart/docs/general-styling/index.md): The settings every chart type shares: the background, the text shown while there is no data, the space around the drawing area, the paints the chart draws with, and how to save it as an image.
- [Chart specific styling](https://philjay.cc/mpandroidchart/docs/chart-styling/index.md): What each chart type adds on top of the settings all charts share, from bar shadows and the pie hole to the web of a radar chart and the draw order of a combined chart.
- [The legend](https://philjay.cc/mpandroidchart/docs/legend/index.md): How the chart builds its legend from the data sets, how to place and style it, and how to replace the computed entries with your own.
- [The description](https://philjay.cc/mpandroidchart/docs/description/index.md): The small label drawn in the bottom right corner of a chart's content area, and the handful of properties that place and style it.
- [Theming a chart](https://philjay.cc/mpandroidchart/docs/theming/index.md): How to keep one look for every chart in your app in a palette object and a few extension functions, and how to switch it between dark and light.

## Motion and viewport

- [Interaction with the chart](https://philjay.cc/mpandroidchart/docs/interaction/index.md): Every touch gesture a chart understands, how to switch each one off, and the listeners that tell you what the user did.
- [Dynamic and realtime data](https://philjay.cc/mpandroidchart/docs/dynamic-data/index.md): How to add and remove entries and data sets while a chart is on screen, what to call afterwards, and how to keep a fast feed drawing smoothly.
- [Modifying the viewport](https://philjay.cc/mpandroidchart/docs/viewport/index.md): Everything that decides which part of the data is on screen: zoom, scroll, the limits on both, the offsets around the content area, and how to read the current state back.
- [Animations](https://philjay.cc/mpandroidchart/docs/animations/index.md): Building the chart up with animateX, animateY and animateXY, knowing when an animation ends, moving values to new data with animateValue and animateDataChange, the easing curves, spinning round charts, and animating the viewport.
- [Markers](https://philjay.cc/mpandroidchart/docs/markers/index.md): The popup drawn at a highlighted value: the composable marker of the Compose module, MarkerView from a layout, MarkerImage from a drawable, and the IMarker interface behind them all.

## Classes in depth

- [The ChartData class](https://philjay.cc/mpandroidchart/docs/chartdata/index.md): The base class behind LineData, BarData and the rest: the list of data sets, the cached ranges over them, and the lookups and broadcast styling every data object shares.
- [ChartData subclasses](https://philjay.cc/mpandroidchart/docs/chartdata-subclasses/index.md): What each data class adds on top of ChartData, from the bar width to the five slots of a combined chart.
- [The DataSet class](https://philjay.cc/mpandroidchart/docs/dataset/index.md): The styling and behaviour every data set shares, from the legend label to the entry lookups and the cached value ranges.
- [DataSet subclasses](https://philjay.cc/mpandroidchart/docs/dataset-subclasses/index.md): What each chart type's data set adds on top of the shared settings, from line modes and bar corners to candle colors and pie value lines.
- [The ViewPortHandler](https://philjay.cc/mpandroidchart/docs/viewporthandler/index.md): The object behind every chart that knows the chart size, the rectangle the data is drawn in, and the zoom and drag state, with the limits that keep all three sane.
- [The fill formatter](https://philjay.cc/mpandroidchart/docs/fillformatter/index.md): How a line data set decides where its filled area ends, what the default does, and how to fill to zero, to an axis edge or to a value of your own.
- [Custom data sets](https://philjay.cc/mpandroidchart/docs/custom-datasets/index.md): How to write your own data set class, what the renderers actually read from it, and how far you can go before you have to touch a renderer.
- [Custom renderers](https://philjay.cc/mpandroidchart/docs/custom-renderers/index.md): The classes that paint a chart onto its canvas, how a chart wires them up, and how to replace one with your own.

## Integration

- [Jetpack Compose](https://philjay.cc/mpandroidchart/docs/compose/index.md): The MPChartCompose module wraps every chart view in a composable, so you can pass data as state, read the selection back, and drive zoom and animation from Compose.
- [Calling the library from Java](https://philjay.cc/mpandroidchart/docs/java-interop/index.md): What the Kotlin API looks like from a Java caller: property accessors, default arguments, lambdas, generics and the few places where Java needs a longer spelling.
- [Charts in lists and scrolling screens](https://philjay.cc/mpandroidchart/docs/lists-and-scrolling/index.md): How to put a chart into a LazyColumn, a recycled row, a fragment or a scrolling screen without rebuilding data on every frame or fighting the parent for the gesture.
- [R8 and ProGuard](https://philjay.cc/mpandroidchart/docs/proguard/index.md): What a minified release build needs for the chart library, which is nothing, and the few cases in your own code that may still want a rule.

## In practice

- [Performance with large data](https://philjay.cc/mpandroidchart/docs/performance/index.md): What a chart spends its time on when it draws, which settings buy the most of it back, and how to measure instead of guess.
- [Accessibility](https://philjay.cc/mpandroidchart/docs/accessibility/index.md): What a screen reader can and cannot get from a chart, and the things you can do about it.
- [Troubleshooting](https://philjay.cc/mpandroidchart/docs/troubleshooting/index.md): Concrete symptoms you may hit with a chart, what causes each one in the library, and what to change.
- [Migrating from 3.x](https://philjay.cc/mpandroidchart/docs/migration/index.md): What to change in an app written against MPAndroidChart 3.x when you move it to the Kotlin rewrite.
- [Miscellaneous](https://philjay.cc/mpandroidchart/docs/miscellaneous/index.md): The useful corners of the library that do not belong to any one chart type: unit conversion, number formatting, saving an image, the pooled geometry classes, sorting, logging and what to do with a very large data set.
