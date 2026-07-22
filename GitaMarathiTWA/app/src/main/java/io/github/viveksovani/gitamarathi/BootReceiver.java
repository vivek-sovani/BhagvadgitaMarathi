package io.github.viveksovani.gitamarathi;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** AlarmManager alarms don't survive reboot — re-arm the daily notification alarm on boot. */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            AlarmScheduler.rescheduleFromPrefs(context);
        }
    }
}
