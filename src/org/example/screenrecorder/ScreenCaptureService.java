package org.example.screenrecorder;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.MediaRecorder;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.IBinder;
import android.provider.MediaStore;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.WindowManager;
import android.widget.Toast;

import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class ScreenCaptureService extends Service {
    private static final String TAG = "ScreenCaptureService";
    private static final String CHANNEL_ID = "ScreenCaptureServiceChannel";
    private static final int NOTIFICATION_ID = 1001;
    public static final String ACTION_STOP = "org.example.screenrecorder.STOP";

    private MediaProjection mediaProjection;
    private MediaRecorder mediaRecorder;
    private VirtualDisplay virtualDisplay;
    private File videoFile;
    private MediaProjection.Callback projectionCallback;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            String action = intent.getAction();
            if (ACTION_STOP.equals(action)) {
                stopRecording();
                stopForeground(true);
                stopSelf();
                return START_NOT_STICKY;
            }

            int resultCode = intent.getIntExtra("resultCode", -1);
            Intent data = intent.getParcelableExtra("data");

            // ۱. ناتیفیکیشن پیش‌زمینه
            Notification notification;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                notification = new Notification.Builder(this, CHANNEL_ID)
                        .setContentTitle("ضبط صفحه نمایش")
                        .setContentText("در حال ضبط ویدیو...")
                        .setSmallIcon(android.R.drawable.ic_menu_camera)
                        .setPriority(Notification.PRIORITY_LOW)
                        .build();
            } else {
                notification = new Notification.Builder(this)
                        .setContentTitle("ضبط صفحه نمایش")
                        .setContentText("در حال ضبط ویدیو...")
                        .setSmallIcon(android.R.drawable.ic_menu_camera)
                        .setPriority(Notification.PRIORITY_LOW)
                        .build();
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
            } else {
                startForeground(NOTIFICATION_ID, notification);
            }

            // ۲. محاسبه دقیق ابعاد و زوج‌سازی رزولوشن
            DisplayMetrics metrics = new DisplayMetrics();
            WindowManager wm = (WindowManager) getSystemService(Context.WINDOW_SERVICE);
            if (wm != null) {
                wm.getDefaultDisplay().getRealMetrics(metrics);
            }
            int width = metrics.widthPixels;
            int height = metrics.heightPixels;
            int density = metrics.densityDpi;

            // ⚠️ حتماً ابعاد باید عدد زوج باشند تا MediaEncoder کرش نکند
            if (width % 2 != 0) width -= 1;
            if (height % 2 != 0) height -= 1;

            MediaProjectionManager projectionManager = (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            if (projectionManager != null && data != null) {
                mediaProjection = projectionManager.getMediaProjection(resultCode, data);

                // ⚠️ شرط اجباری برای اندروید ۱۴ و ۱۵: ثبت Callback
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                    projectionCallback = new MediaProjection.Callback() {
                        @Override
                        public void onStop() {
                            super.onStop();
                            stopRecording();
                        }
                    };
                    mediaProjection.registerCallback(projectionCallback, null);
                }

                startRecording(width, height, density);
            } else {
                Log.e(TAG, "projectionManager or data is null");
                stopSelf();
            }
        }
        return START_NOT_STICKY;
    }

    private void startRecording(int width, int height, int density) {
        try {
            File storageDir = new File(getExternalFilesDir(Environment.DIRECTORY_MOVIES), "ScreenRecordings");
            if (!storageDir.exists()) {
                storageDir.mkdirs();
            }
            String fileName = "REC_" + new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date()) + ".mp4";
            videoFile = new File(storageDir, fileName);

            mediaRecorder = new MediaRecorder();
            mediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
            mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
            mediaRecorder.setOutputFile(videoFile.getAbsolutePath());
            mediaRecorder.setVideoSize(width, height);
            mediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
            mediaRecorder.setVideoEncodingBitRate(6000000); // 6 Mbps
            mediaRecorder.setVideoFrameRate(30);
            mediaRecorder.prepare();

            virtualDisplay = mediaProjection.createVirtualDisplay(
                    "ScreenCapture",
                    width, height, density,
                    DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                    mediaRecorder.getSurface(), null, null
            );

            mediaRecorder.start();
            Log.d(TAG, "Recording started to: " + videoFile.getAbsolutePath());
        } catch (Exception e) {
            Log.e(TAG, "startRecording failed", e);
            stopRecording();
            stopSelf();
        }
    }

    private void stopRecording() {
        if (mediaRecorder != null) {
            try {
                mediaRecorder.stop();
                mediaRecorder.reset();
                mediaRecorder.release();
            } catch (Exception e) {
                Log.e(TAG, "stopRecording error", e);
            }
            mediaRecorder = null;
        }
        if (virtualDisplay != null) {
            virtualDisplay.release();
            virtualDisplay = null;
        }
        if (mediaProjection != null) {
            if (projectionCallback != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                mediaProjection.unregisterCallback(projectionCallback);
            }
            mediaProjection.stop();
            mediaProjection = null;
        }

        if (videoFile != null && videoFile.exists() && videoFile.length() > 0) {
            moveToGallery(videoFile);
        } else {
            Log.e(TAG, "No valid video file to move to gallery");
        }
        videoFile = null;
    }

    private void moveToGallery(File sourceFile) {
        try {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Video.Media.DISPLAY_NAME, sourceFile.getName());
            values.put(MediaStore.Video.Media.MIME_TYPE, "video/mp4");
            values.put(MediaStore.Video.Media.RELATIVE_PATH, Environment.DIRECTORY_MOVIES + "/ScreenRecordings");
            values.put(MediaStore.Video.Media.IS_PENDING, 1);

            ContentResolver resolver = getContentResolver();
            Uri uri = resolver.insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values);
            if (uri != null) {
                try (OutputStream out = resolver.openOutputStream(uri);
                     FileInputStream in = new FileInputStream(sourceFile)) {
                    byte[] buffer = new byte[4096];
                    int len;
                    while ((len = in.read(buffer)) > 0) {
                        out.write(buffer, 0, len);
                    }
                }

                values.clear();
                values.put(MediaStore.Video.Media.IS_PENDING, 0);
                resolver.update(uri, values, null, null);

                sourceFile.delete();
                Log.d(TAG, "Video moved to gallery: " + uri);
            }
        } catch (Exception e) {
            Log.e(TAG, "moveToGallery failed", e);
        }
    }

    @Override
    public void onDestroy() {
        stopRecording();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel serviceChannel = new NotificationChannel(
                    CHANNEL_ID,
                    "Screen Capture Service Channel",
                    NotificationManager.IMPORTANCE_LOW
            );
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(serviceChannel);
            }
        }
    }
}
