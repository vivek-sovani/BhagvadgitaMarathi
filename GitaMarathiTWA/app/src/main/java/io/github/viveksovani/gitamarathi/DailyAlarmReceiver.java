package io.github.viveksovani.gitamarathi;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;

import androidx.core.app.NotificationCompat;

/**
 * Fires the daily sankalpana reminder at the user's chosen time, even with the app fully closed,
 * then re-arms itself for tomorrow. Taps open sankalpana-today.html, a small redirect page on the
 * live site that computes today's actual concept client-side (same day-index rotation as
 * js/notify.js's todaysSankalpana()) and forwards straight to it — this receiver doesn't need to
 * duplicate that rotation logic (or the growing concept list) natively.
 */
public class DailyAlarmReceiver extends BroadcastReceiver {
    private static final String CHANNEL_ID = "daily_sankalpana";
    private static final int NOTIFICATION_ID = 2201;

    @Override
    public void onReceive(Context context, Intent intent) {
        showNotification(context);
        AlarmScheduler.rescheduleFromPrefs(context);
    }

    private void showNotification(Context context) {
        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                && nm.getNotificationChannel(CHANNEL_ID) == null) {
            nm.createNotificationChannel(new NotificationChannel(
                    CHANNEL_ID, "दैनंदिन संकल्पना", NotificationManager.IMPORTANCE_DEFAULT));
        }

        Intent openApp = new Intent(context, LauncherActivity.class);
        openApp.setAction(Intent.ACTION_VIEW);
        openApp.setData(Uri.parse(context.getString(R.string.launchUrl) + "sankalpana-today.html"));
        openApp.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity(context, 0, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_notification_icon)
                .setContentTitle(context.getString(R.string.appName))
                .setContentText("आजची नवीन संकल्पना पाहण्यासाठी टॅप करा")
                .setAutoCancel(true)
                .setContentIntent(contentIntent);

        nm.notify(NOTIFICATION_ID, builder.build());
    }
}
