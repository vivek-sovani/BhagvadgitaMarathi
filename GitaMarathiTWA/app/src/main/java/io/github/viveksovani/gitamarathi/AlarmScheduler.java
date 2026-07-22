package io.github.viveksovani.gitamarathi;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import java.util.Calendar;

/** Schedules/cancels the daily sankalpana notification alarm and persists its settings. */
final class AlarmScheduler {
    private static final String PREFS = "daily_notify_prefs";
    private static final String KEY_ENABLED = "enabled";
    private static final String KEY_HOUR = "hour";
    private static final String KEY_MINUTE = "minute";
    private static final int REQUEST_CODE = 4201;

    private AlarmScheduler() {}

    static void save(Context context, boolean enabled, int hour, int minute) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putBoolean(KEY_ENABLED, enabled)
                .putInt(KEY_HOUR, hour)
                .putInt(KEY_MINUTE, minute)
                .apply();
    }

    /** Re-arms the alarm from whatever was last saved — used after reboot and after each fire. */
    static void rescheduleFromPrefs(Context context) {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        if (p.getBoolean(KEY_ENABLED, false)) {
            scheduleNext(context, p.getInt(KEY_HOUR, 7), p.getInt(KEY_MINUTE, 0));
        } else {
            cancel(context);
        }
    }

    static void scheduleNext(Context context, int hour, int minute) {
        AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;

        Calendar target = Calendar.getInstance();
        target.set(Calendar.HOUR_OF_DAY, hour);
        target.set(Calendar.MINUTE, minute);
        target.set(Calendar.SECOND, 0);
        target.set(Calendar.MILLISECOND, 0);
        if (!target.after(Calendar.getInstance())) {
            target.add(Calendar.DAY_OF_YEAR, 1);
        }

        PendingIntent pi = pendingIntent(context);
        am.cancel(pi);
        // Inexact-but-Doze-aware: no SCHEDULE_EXACT_ALARM permission needed, at the cost of
        // possibly firing up to ~15 minutes late under Doze.
        am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, target.getTimeInMillis(), pi);
    }

    static void cancel(Context context) {
        AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(pendingIntent(context));
    }

    private static PendingIntent pendingIntent(Context context) {
        Intent intent = new Intent(context, DailyAlarmReceiver.class);
        return PendingIntent.getBroadcast(context, REQUEST_CODE, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
}
