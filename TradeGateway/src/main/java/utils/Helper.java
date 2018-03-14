package utils;

import com.ib.client.EReader;
import com.ib.client.EWrapper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.LinkedList;
import java.util.concurrent.TimeUnit;

/**
 * Created by meng on 9/21/17.
 */
public class Helper {

    public static void pauseSec(int seconds) {
        try {
            TimeUnit.SECONDS.sleep(seconds);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void pauseMilli(int milliseconds) {
        try {
            TimeUnit.MILLISECONDS.sleep(milliseconds);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static String today() {
        Date today = Calendar.getInstance().getTime();
        SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd");
        return formatter.format(today);
    }

    public static String timestampToString(Timestamp timestamp) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyy-MM-dd HH:mm:ss.SSS");
        return dateFormat.format(timestamp);
    }

    public static String timestampNow() {
        return timestampToString(new Timestamp(new Date().getTime()));
    }

    public static void runCmd(String[] command, boolean wait) {
        Runtime runtime = Runtime.getRuntime();
        try {
            Process p = runtime.exec(command);
                if (wait) {
                    p.waitFor();
                }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static String runCmd(String[] command) {
        Runtime runtime = Runtime.getRuntime();
        StringBuilder result = new StringBuilder();
        try {
            Process p = runtime.exec(command);
            String s = null;
            BufferedReader stdin = new BufferedReader(new InputStreamReader(p.getInputStream()));
            BufferedReader stderr = new BufferedReader(new InputStreamReader(p.getErrorStream()));
            while ((s = stdin.readLine()) != null) {
                result.append(s + "\n");
            }
            while ((s = stderr.readLine()) != null) {
                result.append(s + "\n");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return result.toString();
    }

    public static LinkedList<String> resultToList(ResultSet resultSet, String column) {
        LinkedList<String> list = new LinkedList<>();
        try {
            while(resultSet != null && resultSet.next()) {
                String element = resultSet.getString(column);
                list.addFirst(element);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }
}
