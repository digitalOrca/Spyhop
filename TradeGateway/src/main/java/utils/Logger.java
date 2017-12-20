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

    private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMdd");
    private SimpleDateFormat timeFormat = new SimpleDateFormat("[HH:mm:ss.SSS]");

    private String logRoot = "/home/meng/Projects/NeuroTrader/Logs/";
    private String logFileName = "";
    private File log = null;
    private BufferedWriter bufferedWriter = null;
    private FileWriter fileWriter = null;

    private Logger() {
        Date date = new Date();
        String timestamp = this.dateFormat.format(date);

        this.logFileName = logRoot + "C" + timestamp + ".txt";
        this.log = new File(this.logFileName);
        try {
            if (!this.log.exists()) {
                this.log.createNewFile();
            }
            this.fileWriter = new FileWriter(this.log, true);
        } catch (Exception e) {
            e.printStackTrace();
        }
        this.bufferedWriter = new BufferedWriter(fileWriter);
    }

    public void log(Log type, String entry) {
        String timestamp = this.timeFormat.format(new Date());
        try {
            if (type == Log.CALLBACK) {
                this.bufferedWriter.write(timestamp + entry + "\n");
                this.bufferedWriter.flush();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void close() {
        try {
            if (this.bufferedWriter != null) {
                this.bufferedWriter.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}