# R8 and ProGuard

What a minified release build needs for the chart library, which is nothing, and the few cases in your own code that may still want a rule.

## The short answer

You do not need any keep rules for MPAndroidChart. Turn on minification the usual way and build:

```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }
}
```

The library does no reflection: nothing in it looks up a class, a field or a method by name, so R8 is free to shrink, rename and optimize all of it. The Compose module needs nothing extra either; the Compose artifacts ship their own rules.

> The library does not ship consumer rules. `MPChartLib` sets no `consumerProguardFiles`, so nothing is merged into your configuration behind your back. What you write is what applies.

## Drop the old rule

Older documentation told you to whitelist the whole package:

```proguard
-keep class com.github.mikephil.charting.** { *; }
```

Delete that line. It is no longer needed, and it costs you: it keeps every chart type, renderer, formatter and utility class in the library whether you use them or not, along with all their members, so nothing of the library can be shrunk out of your APK.

The rule existed because of animation. Version 3 drove the entry animations with `ObjectAnimator.ofFloat(this, "phaseX", ...)`, which looks the setter up by name at runtime. Once R8 renamed `setPhaseX`, the lookup failed and animations silently did nothing.

Version 4 does not do that any more. Every animation in the library now drives a `ValueAnimator` and assigns the value in an update listener, so no name is ever looked up:

- `ChartAnimator`, behind `animateX`, `animateY` and `animateXY`, runs a `ValueAnimator` from 0 to 1 and sets `phaseX` or `phaseY` in a lambda.
- `AnimatedViewPortJob`, behind the animated zoom and move calls, drives its `phase` the same way.
- `PieRadarChartBase.spin()` animates `rotationAngle` the same way.

Renaming those members is now harmless, so nothing needs to keep them.

## What keeps the chart views

The library has no `@Keep` annotations and no dependency on `androidx.annotation`. The one thing that is looked up by name is a chart written into a layout file, which the layout inflater creates from its fully qualified class name. The build takes care of that: for every view class named in a layout, AAPT2 writes a keep rule for its name and constructors, and R8 applies it. A chart you only create in code is kept because your code references it.

Beyond that, the default configuration already covers the pieces of Android that charts touch: view constructors that take a `Context` and an `AttributeSet`, and the `CREATOR` field of `Parcelable` classes, which `Entry` implements.

## Your own code

Most of what you write needs nothing.

**Value formatters and fill formatters.** `IValueFormatter`, `IAxisValueFormatter` and `IFillFormatter` are Kotlin functional interfaces. You implement one and assign it from your own code, so R8 sees the reference and keeps the class. It may rename it, which does not matter. Nothing to add.

```kotlin
xAxis.valueFormatter = IAxisValueFormatter { value, _ -> months[value.toInt()] }
```

**Markers.** A `MarkerView` subclass is the same story as long as you create it in code. Its layout resource is kept because you name it through `R.layout`, and the views it looks up with `findViewById` keep their ids.

```kotlin
chart.marker = MyMarkerView(context, R.layout.marker_view)
```

A chart subclass of yours that appears only in a layout XML file needs nothing either, for the same reason as the library's own charts: AAPT2 writes the keep rule for every view class named in a layout.

**Entry payloads.** An `Entry(x, y, data = order)` payload is your class, and the library only ever hands it back to you. It needs a keep rule only if something else reflects on it: a JSON library reading its field names, or `writeToParcel` on an entry, which requires the payload to be `Parcelable` and therefore to keep its `CREATOR`. Those rules belong to that library, not to this one.

**Resource shrinking.** `isShrinkResources = true` removes drawables that nothing references. Entry icons and marker layouts you load through `R.drawable` or `R.layout` are references, so they stay. Ones you resolve by name at runtime do not, and need `tools:keep` in a resources file.

## Readable crash reports

Minified stack traces from a chart are as unreadable as any other. Keep the line numbers and hide the renamed source file:

```proguard
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile
```

Then deobfuscate with the mapping file that the build writes to `build/outputs/mapping/release/mapping.txt`, and upload it wherever you collect crashes.

## Checking what R8 did

If a chart misbehaves only in a release build, first confirm it is really R8 and not the build type. Build the release variant with `isMinifyEnabled = false` and try again. If the problem goes away, add this to your configuration and look at what was removed:

```proguard
-printusage build/outputs/mapping/release/usage.txt
```

Then keep exactly the class you found, not the whole package:

```proguard
-keep class com.example.MyReflectedFormatter { *; }
```

If you are migrating an app that still carries the wide keep rule, remove it, build a release APK and compare the size. Nothing about the charts should change; the APK gets smaller.
