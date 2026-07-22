# GitaMarathiTWA — Project Documentation

## Overview

**GitaMarathiTWA** is an Android app that wraps the Bhagavad Gita (Marathi / Dnyaneshwari) Progressive Web App (PWA) as a **Trusted Web Activity (TWA)**. It uses Google's `androidbrowserhelper` library to launch the PWA hosted on GitHub Pages as a full-screen, native-feeling Android app — with no browser UI chrome visible to the user.

- **App name (display):** गीता-ज्ञानेश्वरी
- **Package ID:** `io.github.viveksovani.gitamarathi`
- **Version:** 1.0.0 (versionCode 1)
- **Generated using:** `bubblewrap-cli`

---

## Architecture

```
GitHub Pages PWA  ←──────────────────────────────────┐
https://vivek-sovani.github.io/BhagvadgitaMarathi/   │
                                                       │
AndroidManifest.xml                                    │
  └── LauncherActivity (androidbrowserhelper)  ───────┘
        ↕ Digital Asset Links verification
        Opens PWA in Chrome as TWA (no browser UI)
```

This is a **shell app** — it contains no business logic or UI of its own. All content is served from the web.

---

## Project Structure

```
GitaMarathiTWA/
├── twa-manifest.json              # bubblewrap TWA configuration (source of truth)
├── build.gradle                   # Root Gradle build (AGP 8.3.0)
├── settings.gradle                # Project settings, repo config
├── gradle.properties              # JVM args, AndroidX flags
├── android.keystore               # Release signing keystore
│
└── app/
    ├── build.gradle               # App-level Gradle config
    └── src/main/
        ├── AndroidManifest.xml    # App manifest — activities, permissions, intent filters
        └── res/
            ├── drawable/
            │   └── splash.xml     # Splash screen background layer-list
            ├── mipmap-*/
            │   └── ic_launcher.png  # Launcher icons (mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi)
            ├── values/
            │   ├── strings.xml    # App name string
            │   ├── colors.xml     # colorPrimary, backgroundColor
            │   └── styles.xml     # AppTheme (NoActionBar)
            └── xml/
                └── file_paths.xml # FileProvider paths config
```

---

## Key Configuration

### TWA Manifest (`twa-manifest.json`)

This file is the **bubblewrap source of truth**. When regenerating Android project files, bubblewrap reads this.

| Field | Value |
|---|---|
| `packageId` | `io.github.viveksovani.gitamarathi` |
| `host` | `vivek-sovani.github.io` |
| `startUrl` | `/BhagvadgitaMarathi/` |
| `fullScopeUrl` | `https://vivek-sovani.github.io/BhagvadgitaMarathi/` |
| `webManifestUrl` | `https://vivek-sovani.github.io/BhagvadgitaMarathi/manifest.json` |
| `display` | `standalone` |
| `orientation` | `portrait` |
| `themeColor` | `#9c4a10` (deep saffron/brown) |
| `backgroundColor` | `#FFF8F0` (warm cream) |
| `fallbackType` | `customtabs` (falls back to Chrome Custom Tabs if TWA not supported) |
| `minSdkVersion` | 24 (Android 7.0) |
| `enableNotifications` | false |
| `isChromeOSOnly` | false |
| `isMetaQuest` | false |

### Signing Config (`app/build.gradle`)

| Field | Value |
|---|---|
| Keystore file | `../android.keystore` (project root) |
| Key alias | `gitamarathi` |
| Store password | `gitamarathi123` |
| Key password | `gitamarathi123` |

> **Important:** The keystore file `android.keystore` is at the project root. Keep it backed up — losing it means you cannot publish updates to the Play Store under the same package ID.

### App Build Config (`app/build.gradle`)

| Field | Value |
|---|---|
| `compileSdk` | 35 |
| `minSdk` | 24 |
| `targetSdk` | 35 |
| Java compatibility | VERSION_17 |
| `minifyEnabled` | false |

### Dependencies

```gradle
implementation 'com.google.androidbrowserhelper:androidbrowserhelper:2.5.0'
implementation 'androidx.appcompat:appcompat:1.6.1'
```

---

## AndroidManifest.xml — Key Details

### Permission
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### Main Activity
Uses `com.google.androidbrowserhelper.trusted.LauncherActivity` — no custom Java/Kotlin activity code.

**Meta-data values:**
- `DEFAULT_URL`: `https://vivek-sovani.github.io/BhagvadgitaMarathi/`
- Status bar color: `@color/colorPrimary` → `#9c4a10`
- Navigation bar color: `@color/colorPrimary` → `#9c4a10`
- File provider authority: `io.github.viveksovani.gitamarathi.fileprovider`

**Intent filters:**
1. MAIN / LAUNCHER — app entry point
2. `android.intent.action.VIEW` with `autoVerify="true"` for Digital Asset Links (DAL) verification:
   - scheme: `https`
   - host: `vivek-sovani.github.io`
   - pathPrefix: `/BhagvadgitaMarathi`

### FileProvider
Authority: `io.github.viveksovani.gitamarathi.fileprovider`
Paths config: `res/xml/file_paths.xml` — exposes internal `files/` directory.

---

## Theming & Branding

| Resource | Value |
|---|---|
| `colorPrimary` | `#9c4a10` — deep saffron/brown (status bar, nav bar) |
| `backgroundColor` | `#FFF8F0` — warm cream (window background, splash) |
| App theme | `Theme.AppCompat.Light.NoActionBar` |
| Splash screen | Solid `backgroundColor` layer (no image, just warm cream background) |
| Launcher icon | PNG icons across all density buckets (mdpi to xxxhdpi) |

---

## Build Outputs

| Output | Path |
|---|---|
| Debug APK | `app/build/outputs/apk/debug/app-debug.apk` |
| Release APK | `app/build/outputs/apk/release/app-release.apk` |
| Release AAB | `app/build/outputs/bundle/release/app-release.aab` |

The **AAB** (`app-release.aab`) is what should be uploaded to the Google Play Console.

---

## How TWA Works (Brief)

1. User launches the app → `LauncherActivity` starts.
2. Android checks Digital Asset Links on the host (`vivek-sovani.github.io`) to verify the app is trusted.
3. If verified, Chrome opens the PWA URL (`/BhagvadgitaMarathi/`) with no browser chrome — it looks like a native app.
4. If not verified (or Chrome not available), falls back to **Chrome Custom Tabs** (`fallbackType: customtabs`).

For DAL verification to work, the file `https://vivek-sovani.github.io/.well-known/assetlinks.json` must list the app's SHA-256 signing fingerprint.

---

## How to Build

```bash
# Debug build
./gradlew assembleDebug

# Release APK
./gradlew assembleRelease

# Release AAB (for Play Store)
./gradlew bundleRelease
```

Gradle version used: **8.6**  
Android Gradle Plugin: **8.3.0**

---

## Regenerating with Bubblewrap

If you need to regenerate the Android project from scratch:

```bash
npm install -g @bubblewrap/cli
bubblewrap build   # uses twa-manifest.json
```

The `twa-manifest.json` at the project root is the bubblewrap config and will re-generate all Android files.

---

## Related Resources

- **PWA source:** `https://vivek-sovani.github.io/BhagvadgitaMarathi/`
- **Web manifest:** `https://vivek-sovani.github.io/BhagvadgitaMarathi/manifest.json`
- **Icons hosted at:** `https://vivek-sovani.github.io/BhagvadgitaMarathi/assets/icons/`
  - `icon-512.png` (standard + monochrome)
  - `icon-maskable-512.png` (maskable)
- **bubblewrap docs:** https://github.com/GoogleChromeLabs/bubblewrap
