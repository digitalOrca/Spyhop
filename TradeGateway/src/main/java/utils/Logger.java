package utils;

import enums.Log;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Created by meng on 5/21/17.
 */
public class Logger {

    private static Logger ourInstance = new Logger();

    public static Logger getInstance() {
        return ourInstance;
    }

    private static String[] logRoots;

    private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMdd");
    private SimpleDateFormat timeFormat = new SimpleDateFormat("[HH:mm:ss.SSS]");

    private String callbackLogRoot = "/home/meng/Projects/NeuroTrader/Logs/Callback/";
    private String callbackLogFileName = "";
    private File callbackLog = null;
    private BufferedWriter callbackBufferedWriter = null;
    private FileWriter callbackFileWriter = null;

    private String actionLogRoot = "/home/meng/Projects/NeuroTrader/Logs/Action/";
    private String actionLogFileName = "";
    private File actionLog = null;
    private BufferedWriter actionBufferedWriter = null;
    private FileWriter actionFileWriter = null;

    private Logger() {
        Date date = new Date();
        String timestamp = this.dateFormat.format(date);

        this.callbackLogFileName = callbackLogRoot + "C" + timestamp + ".txt";
        this.actionLogFileName = actionLogRoot + "A" + timestamp + ".txt";
        this.callbackLog = new File(this.callbackLogFileName);
        this.actionLog = new File(this.actionLogFileName);
        try {
            if (!this.callbackLog.exists()) {
                this.callbackLog.createNewFile();
            }
            if (!this.actionLog.exists()) {
                this.actionLog.createNewFile();
            }
            this.callbackFileWriter = new FileWriter(this.callbackLog, true);
            this.actionFileWriter = new FileWriter(this.actionLog, true);
        } catch (Exception e) {
            e.printStackTrace();
        }
        this.callbackBufferedWriter = new BufferedWriter(callbackFileWriter);
        this.actionBufferedWriter = new BufferedWriter(actionFileWriter);
    }

    public void log(Log type, String entry) {
        String timestamp = this.timeFormat.format(new Date());
        try {
            if (type == Log.CALLBACK) {
                this.callbackBufferedWriter.write(timestamp + entry + "\n");
                this.callbackBufferedWriter.flush();
            }
            if (type == Log.ACTION) {
                this.actionBufferedWriter.write(timestamp + entry + "\n");
                this.actionBufferedWriter.flush();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void close() {
        try {
            if (this.callbackBufferedWriter != null) {
                this.callbackBufferedWriter.close();
            }
            if (this.actionBufferedWriter != null) {
                this.actionBufferedWriter.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}