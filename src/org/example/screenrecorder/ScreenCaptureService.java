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
import android.os.ParcelFileDescriptor;
import android.provider.MediaStore;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.WindowManager;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class ScreenCaptureService extends Service {
    private static final String TAG = "ScreenCaptureService";
    private static final String CHANNEL_ID = "ScreenCaptureServiceChannel";
    private static final int NOTIFICATION_ID = 1001;

    private MediaProjection mediaProjection;
    private MediaRecorder mediaRecorder;
    private VirtualDisplay virtualDisplay;

    private int screenWidth = 720;
    private int screenHeight = 1280;
    private int screenDensity = 320;

    private ParcelFileDescriptor pfd;
    private Uri videoUri;
    private boolean usingMediaStore = false;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            int resultCode = intent.getIntExtra("resultCode", -1);
            Intent data = intent.getParcelableExtra("data");

            // دریافت ابعاد واقعی صفحه
            DisplayMetrics metrics = new DisplayMetrics();
            WindowManager wm = (WindowManager) getSystemService(Context.WINDOW_SERVICE);
            wm.getDefaultDisplay().getMetrics(metrics);
            screenWidth = metrics.widthPixels;
            screenHeight = metrics.heightPixels;
            screenDensity = metrics.densityDpi;

            Notification notification;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                notification = new Notification.Builder(this, CHANNEL_ID)
                        .setContentTitle("ضبط صفحه نمایش")
                        .setContentText("برنامه در حال ضبط ویدیو از صفحه است...")
                        .setSmallIcon(android.R.drawable.ic_menu_camera)
                        .setPriority(Notification.PRIORITY_LOW)
                        .build();
            } else {
                notification = new Notification.Builder(this)
                        .setContentTitle("ضبط صفحه نمایش")
                        .setContentText("برنامه در حال ضبط ویدیو از صفحه است...")
                        .setSmallIcon(android.R.drawable.ic_menu_camera)
                        .setPriority(Notification.PRIORITY_LOW)
                        .build();
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
            } else {
                startForeground(NOTIFICATION_ID, notification);
            }

            MediaProjectionManager projectionManager = (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            if (projectionManager != null && data != null) {
                mediaProjection = projectionManager.getMediaProjection(resultCode, data);
                startRecording();
            } else {
                Log.e(TAG, "projectionManager or data is null");
            }
        }
        return START_NOT_STICKY;
    }

    private void startRecording() {
        try {
            String fileName = "REC_" + new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date()) + ".mp4";

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ContentValues values = new ContentValues();
                values.put(MediaStore.Video.Media.DISPLAY_NAME, fileName);
                values.put(MediaStore.Video.Media.MIME_TYPE, "video/mp4");
                values.put(MediaStore.Video.Media.RELATIVE_PATH, Environment.DIRECTORY_MOVIES + "/ScreenRecordings");
                values.put(MediaStore.Video.Media.IS_PENDING, 1);

                ContentResolver resolver = getContentResolver();
                videoUri = resolver.insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values);
                if (videoUri != null) {
                    pfd = resolver.openFileDescriptor(videoUri, "w");
                    if (pfd != null) {
                        usingMediaStore = true;
                        Log.d(TAG, "MediaStore file created: " + videoUri);
                    } else {
                        Log.e(TAG, "openFileDescriptor returned null, falling back to private storage");
                        resolver.delete(videoUri, null, null);
                        videoUri = null;
                    }
                } else {
                    Log.e(TAG, "MediaStore insert returned null, falling back to private storage");
                }
            }

            if (!usingMediaStore) {
                File storageDir = new File(getExternalFilesDir(Environment.DIRECTORY_MOVIES), "ScreenRecordings");
                if (!storageDir.exists()) {
                    storageDir.mkdirs();
                }
                File videoFile = new File(storageDir, fileName);
                mediaRecorder = new MediaRecorder();
                mediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
                mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
                mediaRecorder.setOutputFile(videoFile.getAbsolutePath());
                mediaRecorder.setVideoSize(screenWidth, screenHeight);
                mediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
                mediaRecorder.setVideoEncodingBitRate(5120000);
                mediaRecorder.setVideoFrameRate(30);
                mediaRecorder.prepare();
                virtualDisplay = mediaProjection.createVirtualDisplay(
                        "ScreenCapture",
                        screenWidth, screenHeight, screenDensity,
                        DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                        mediaRecorder.getSurface(), null, null
                );
                mediaRecorder.start();
                Log.d(TAG, "Recording started to private storage: " + videoFile.getAbsolutePath());
            } else {
                mediaRecorder = new MediaRecorder();
                mediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
                mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
                mediaRecorder.setOutputFile(pfd.getFileDescriptor());
                mediaRecorder.setVideoSize(screenWidth, screenHeight);
                mediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
                mediaRecorder.setVideoEncodingBitRate(5120000);
                mediaRecorder.setVideoFrameRate(30);
                mediaRecorder.prepare();
                virtualDisplay = mediaProjection.createVirtualDisplay(
                        "ScreenCapture",
                        screenWidth, screenHeight, screenDensity,
                        DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                        mediaRecorder.getSurface(), null, null
                );
                mediaRecorder.start();
                Log.d(TAG, "Recording started to MediaStore");
            }
        } catch (Exception e) {
            Log.e(TAG, "startRecording failed", e);
            if (videoUri != null) {
                getContentResolver().delete(videoUri, null, null);
            }
            if (pfd != null) {
                try { pfd.close(); } catch (IOException ignored) {}
            }
            videoUri = null;
            pfd = null;
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
            mediaProjection.stop();
            mediaProjection = null;
        }
        if (pfd != null) {
            try { pfd.close(); } catch (IOException e) { e.printStackTrace(); }
            pfd = null;
        }
        if (usingMediaStore && videoUri != null) {
            try {
                ContentValues values = new ContentValues();
                values.put(MediaStore.Video.Media.IS_PENDING, 0);
                getContentResolver().update(videoUri, values, null, null);
                Log.d(TAG, "IS_PENDING set to 0");
            } catch (Exception e) {
                Log.e(TAG, "Failed to update IS_PENDING", e);
            }
        }
        usingMediaStore = false;
        videoUri = null;
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
