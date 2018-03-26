package utils;

import enums.Log;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * log utility singleton class
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

    private Logger() {  }

    private Logger(String prefix) {
        Date date = new Date();
        String timestamp = this.dateFormat.format(date);
        this.logFileName = logRoot + prefix + timestamp + ".csv";
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

    /*set log filename prefix*/
    public void setLogMode(String mode) {
        ourInstance = new Logger(mode);
    }

    /*append log entry*/
    public void log(Log type, String entry) {
        String timestamp = this.timeFormat.format(new Date());
        try {
            String logType = String.format("%1$-10s","[" + type.toString() + "]");
            this.bufferedWriter.write(logType + "," + timestamp + "," + entry + "\n");
            this.bufferedWriter.flush();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /*close file buffer*/
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