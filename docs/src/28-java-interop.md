# Calling the library from Java

What the Kotlin API looks like from a Java caller: property accessors, default arguments, lambdas, generics and the few places where Java needs a longer spelling.

The library is written in Kotlin and compiles to ordinary JVM bytecode, so a Java project can use it without any bridge. Every chart class is still a `View` you can inflate from a layout, and every feature is reachable. What changes is the spelling, and this chapter goes through every case.

One thing to ignore along the way: a Kotlin `internal` declaration becomes a public method with a mangled name, so `Chart.notifyGesture$MPChartLib` shows up in autocompletion. The dollar sign marks it as not yours to call.

## Properties become getters and setters

A Kotlin `var` compiles to a getter and a setter pair, so what the Kotlin guides write as an assignment is a `setX` call in Java:

```java
set.setColor(Color.BLUE);
set.setLineWidth(2f);
float width = set.getLineWidth();
```

Boolean properties named `isSomething` are the one case with its own rule. The getter keeps the whole name and the setter drops the `is`:

```java
chart.setDragEnabled(true);
boolean dragging = chart.isDragEnabled();

set.setDrawValuesEnabled(false);
boolean labels = set.isDrawValuesEnabled();
```

So `isDragEnabled` in Kotlin is `isDragEnabled()` and `setDragEnabled(...)` in Java, `isClipValuesToContentEnabled` is `isClipValuesToContentEnabled()` and `setClipValuesToContentEnabled(...)`, and `isEnabled` on every component is `isEnabled()` and `setEnabled(...)`. The rule is mechanical: strip `is`, prefix `set`.

A read-only `val` gives you the getter only. `chart.getLowestVisibleX()` works, there is no setter, and the same holds for `getEntryCount()` on a data set.

## Default arguments

A Kotlin function with default values compiles to **one** Java method carrying every parameter. The defaults live in a synthetic `$default` method that Java should not call. So a call that is short in Kotlin can be long in Java:

```java
// Kotlin: chart.animateX(600)
chart.animateX(600, Easing.INSTANCE.getLinear());

// Kotlin: chart.highlightValue(3f, 0)
chart.highlightValue(3f, 0, -1, -1, true);
```

`-1` and `true` above are the defaults the Kotlin declaration uses, so passing them reproduces the short call exactly.

`@JvmOverloads` is the annotation that generates the shorter overloads as well, and in this library it is used for one purpose only: the constructors of the chart views. `Chart`, `BarLineChartBase`, `PieRadarChartBase`, `LineChart`, `BarChart`, `HorizontalBarChart`, `PieChart`, `ScatterChart`, `CandleStickChart`, `BubbleChart`, `RadarChart` and `CombinedChart` all carry it, which is what makes all three forms available:

```java
LineChart chart = new LineChart(context);
LineChart fromXml = new LineChart(context, attrs);
LineChart styled = new LineChart(context, attrs, defStyle);
```

That also means inflating a chart from a layout file works from Java exactly as it does from Kotlin. No other function in the library has `@JvmOverloads`, so assume you have to pass every parameter everywhere else.

## Functional interfaces

The formatter and shape interfaces are declared as `fun interface`, which is a plain Java interface with a single abstract method. Under Java 8 and above a lambda works:

```java
chart.getXAxis().setValueFormatter((value, axis) -> "Q" + (int) value);
set.setValueFormatter((value, entry, dataSetIndex, viewPortHandler) ->
        String.valueOf((int) value));
```

`IValueFormatter`, `IAxisValueFormatter`, `IFillFormatter`, `IShapeRenderer`, `IHighlighter` and `Easing.EasingFunction` all work this way. When the formatter needs state, write a class instead, and build the expensive parts once rather than per call:

```java
class Percent implements IValueFormatter {
    private final DecimalFormat format = new DecimalFormat("###,##0.0");

    @Override
    public String getFormattedValue(float value, Entry<?> entry, int dataSetIndex,
                                    ViewPortHandler viewPortHandler) {
        return format.format(value) + " %";
    }
}
```

`OnChartValueSelectedListener` and `OnChartGestureListener` have more than one method, so they stay anonymous classes. `IMarker` does too, but you normally extend `MarkerView`, which implements it for you.

> The Kotlin shortcut `chart.onValueSelected { ... }` takes `Function0` and `Function2` parameters, so from Java it needs `kotlin.Unit` returns and reads badly. Use `chart.setOnChartValueSelectedListener(...)` or add to `chart.getValueSelectedListeners()` instead.

## Lists instead of varargs and arrays

Colors, labels and draw orders are `List`, not arrays, so build a `java.util.List` and hand it over. Ints are boxed to `Integer` automatically:

```java
set.setColors(Arrays.asList(Color.BLUE, Color.RED, Color.GREEN));
set.setColors(ColorTemplate.INSTANCE.getMATERIAL_COLORS());
```

There is still an `int` varargs overload for the common case, so `set.setColors(Color.BLUE, Color.RED)` compiles too.

One rule is easy to trip over from Java. A data set keeps the list you pass only when it really is a `java.util.ArrayList`; any other list is copied into a new one. The same holds for the data sets you pass to a data object.

```java
ArrayList<Entry<Object>> live = new ArrayList<>();
LineDataSet<Object> set = new LineDataSet<>(live, "Live");

live.add(new Entry<>(4f, 9f, null, null)); // the set sees this
set.notifyDataSetChanged();
```

`Arrays.asList(...)` returns `java.util.Arrays$ArrayList`, which is a different class, so a set built from it holds a copy and your later changes go nowhere. Use `new ArrayList<>(...)` when you mean to keep the reference.

## Generics

Every entry type carries a payload type parameter, `Entry<D>`, and the data set and data interfaces pass it along. From Java you name it explicitly or use the diamond:

```java
List<Entry<Object>> entries = new ArrayList<>();
entries.add(new Entry<>(0f, 4f, null, null));

LineDataSet<Object> set = new LineDataSet<>(entries, "Sales");
```

Use `Object` when you do not need a payload; there is no Java equivalent of Kotlin's `Nothing`.

The data classes fix their own type argument to a wildcard, which is why `LineData` is not generic and its sets come back as wildcards. Iterating them is the shape you will see most often:

```java
for (IBarDataSet<?> dataSet : barData.getDataSets()) {
    int count = dataSet.getEntryCount();
}
```

The listener callbacks use the same form, `Entry<?>`, because the chart does not know your payload type. Cast when you need the payload or a subclass:

```java
@Override
public void onValueSelected(Entry<?> e, Highlight h) {
    BarEntry<?> bar = (BarEntry<?>) e;
}
```

The Kotlin factory functions return an entry typed with `Nothing`: `Entry(x, y)` gives an `Entry<Nothing>`, `BarEntry(x, y)` a `BarEntry<Nothing>`, and so on for `PieEntry`, `RadarEntry`, `BubbleEntry` and `CandleEntry`. They are top level functions, so Java finds them as static methods on a class named after the file, and `Nothing` has no Java counterpart, so the return type arrives raw:

```java
Entry<Object> e = EntryKt.Entry(1f, 2f, null); // unchecked conversion
```

Call the constructor instead and pass `null` for both the icon and the payload, as the snippets above do. That is the only spelling that stays type safe in Java.

## Objects, companions and top level declarations

No declaration in this library carries `@JvmStatic`, so nothing is called the way a Java static method would be. Two shapes exist.

`ColorTemplate`, `Utils` and `Easing` are Kotlin `object` declarations. Their members are reached through a static `INSTANCE` field:

```java
float px = Utils.INSTANCE.convertDpToPixel(8f);
int green = ColorTemplate.INSTANCE.rgb("#2ecc71");
EasingFunction easing = Easing.INSTANCE.getEaseInOutQuad();
```

`MPPointF`, `MPPointD` and `FSize` keep their pool functions in a companion object, reached through a static `Companion` field:

```java
MPPointF point = MPPointF.Companion.getInstance(-12f, -24f);
MPPointF.Companion.recycleInstance(point);
```

Two kinds of member escape both shapes. A `const val` is a real static field, so `ColorTemplate.COLOR_NONE`, `ColorTemplate.COLOR_SKIP`, `Utils.FLOAT_EPSILON`, `Utils.DEG2RAD` and `Chart.LOG_TAG` are plain constants you read directly. A `@JvmField` property is a public field, so `Entry.CREATOR` works without a `Companion` in front of it, and `point.x` is a field read rather than `getX()`.

> `INSTANCE` and `Companion` are fields, so a static import of them compiles but reads worse than the long form and collides as soon as you import two of them. If `Utils.INSTANCE.` appears all over your code, wrap the two or three conversions you actually use in a small helper of your own.

## Nullability

The Kotlin compiler annotates every parameter and return type with `org.jetbrains.annotations.NotNull` or `Nullable`, so your IDE warns when you pass a null where the Kotlin declaration says non-null. It also inserts a runtime check at the top of every public function. Passing null anyway throws immediately, with the offending method and parameter named:

```text
java.lang.NullPointerException: Parameter specified as non-null is null:
method com.github.mikephil.charting.data.filter.Approximator.reduceWithDouglasPeucker,
parameter points
```

The exception is a plain `NullPointerException`, and it is thrown before any of the function body runs, so nothing is half applied. Where the Kotlin type really is nullable, such as `chart.getData()` on a chart that has none or `Highlight` in `chart.highlightValue(...)`, Java sees `@Nullable` and you handle it as usual.

## A complete example

The same chart as the Kotlin [getting started](/mpandroidchart/docs/getting-started/) example, written in Java:

```java
public class ChartActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LineChart chart = new LineChart(this);
        setContentView(chart);

        List<Entry<Object>> entries = new ArrayList<>();
        entries.add(new Entry<>(0f, 4f, null, null));
        entries.add(new Entry<>(1f, 8f, null, null));
        entries.add(new Entry<>(2f, 6f, null, null));
        entries.add(new Entry<>(3f, 12f, null, null));

        LineDataSet<Object> set = new LineDataSet<>(entries, "Sales");
        set.setColor(Color.BLUE);
        set.setLineWidth(2f);
        set.setCircleRadius(4f);
        set.setDrawValuesEnabled(false);

        chart.setData(new LineData(set));

        chart.getDescription().setEnabled(false);
        chart.getLegend().setEnabled(true);
        chart.getAxisRight().setEnabled(false);
        chart.getXAxis().setPosition(XAxis.XAxisPosition.BOTTOM);
        chart.getXAxis().setValueFormatter((value, axis) -> "Q" + (int) value);
        chart.setNoDataText("Nothing to show yet");

        chart.setOnChartValueSelectedListener(new OnChartValueSelectedListener() {
            @Override
            public void onValueSelected(Entry<?> e, Highlight h) {
            }

            @Override
            public void onNothingSelected() {
            }
        });

        chart.animateX(600, Easing.INSTANCE.getEaseInOutQuad());
    }
}
```

Changing the data later follows the Kotlin rule unchanged: replace the whole data object, or change the entries in place and call `chart.notifyDataSetChanged()`, which recalculates and redraws in one step.

## Where to go next

- [Getting started](/mpandroidchart/docs/getting-started/) for the Kotlin version of the same chart.
- [Formatters](/mpandroidchart/docs/formatters/) for what each formatter interface receives.
- [Migrating from 3.x](/mpandroidchart/docs/migration/) if your Java code was written against version 3.
- [API reference](https://jitpack.io/com/github/PhilJay/MPAndroidChart/MPChartLib/v4.0.0-beta01/javadoc/) for the generated signatures of everything else.
