package io.github.viveksovani.gitamarathi;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;

/**
 * Invisible bridge activity reachable from the website via a gitamarathi://schedule?... deep
 * link (see js/notify.js's bridgeToNative()). A TWA has no direct JS-to-native channel, so this
 * is how the web-side notification settings modal hands its enabled/hour/minute choice off to
 * the native AlarmManager-based scheduler.
 */
public class ScheduleBridgeActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Uri data = getIntent() != null ? getIntent().getData() : null;
        if (data != null) {
            boolean enabled = "1".equals(data.getQueryParameter("enabled"));
            int hour = parseIntOr(data.getQueryParameter("hour"), 7);
            int minute = parseIntOr(data.getQueryParameter("minute"), 0);

            AlarmScheduler.save(this, enabled, hour, minute);
            if (enabled) {
                AlarmScheduler.scheduleNext(this, hour, minute);
                maybeRequestBatteryExemption();
            } else {
                AlarmScheduler.cancel(this);
            }
        }

        finish();
    }

    /**
     * OEM battery managers (Samsung's "Freecess", similar features on Xiaomi/Huawei/etc.) can
     * freeze the app in the background and defer or drop the alarm entirely, on top of stock
     * Android's own Doze restrictions. This standard exemption request at least covers the
     * stock-Android layer; it's shown once and skipped if already granted.
     */
    private void maybeRequestBatteryExemption() {
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        if (pm == null || pm.isIgnoringBatteryOptimizations(getPackageName())) return;
        try {
            Intent intent = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
            intent.setData(Uri.parse("package:" + getPackageName()));
            startActivity(intent);
        } catch (Exception e) {
            // Some OEM ROMs block this intent entirely — nothing more we can do here.
        }
    }

    private static int parseIntOr(String value, int fallback) {
        try {
            return value == null ? fallback : Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return fallback;
        }
    }
}
