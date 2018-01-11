/**
 * Created by meng on 8/6/17.
 */

import com.ib.client.HistogramEntry;
import utils.DatabaseConn;
import utils.Helper;

import java.sql.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

class CallbackAction {

    private static Map<Integer, String> tickTypes = new HashMap<>();

    private static HashMap<String, String[]> register = new HashMap<>(); //tick value cache

    private static HashMap<String, Integer> lastPtr = new HashMap<>();

    static { // static initialization of tickTypes
        for (int tickId : EWrapperImpl.repeatTicks) {
            String TickQuery = "SELECT name FROM tick_type WHERE id=%d";
            String query = String.format(TickQuery, tickId);
            ResultSet resultSet = DatabaseConn.getInstance().execQuery(query);
            try {
                while (resultSet.next()) {
                    tickTypes.put(tickId, resultSet.getString("name"));
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    static void consolidateTicks(String srcTable, String destTable) {
        String query_template = "INSERT INTO %s SELECT * FROM %s";
        String clearTable = "DELETE FROM %s";
        String move = String.format(query_template, destTable, srcTable);
        String clear = String.format(clearTable, srcTable);
        DatabaseConn.getInstance().execUpdate(move);
        DatabaseConn.getInstance().execUpdate(clear);
    }

    static LinkedList<String> selectActiveStocks() {
        String query = "SELECT symbol FROM security WHERE status=1 ORDER BY symbol ASC";
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(query);
        return Helper.resultToList(resultSet, "symbol");
    }

    static LinkedList<String> selectAllStocks() {
        String query = "SELECT symbol FROM security ORDER BY symbol ASC";
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(query);
        return Helper.resultToList(resultSet, "symbol");
    }

    static void updateHistogram(String symbol, List<HistogramEntry> pricePoints, String literal) {

        String timestamp = Helper.timestampNow();
        double total_value = 0;
        long volume = 0;
        double min = Double.MAX_VALUE;
        double max = Double.MIN_VALUE;
        double median = 0;
        double threshold = 0;
        double half;

        Collections.sort(pricePoints);
        LinkedList<HistogramEntry> price_queue = new LinkedList<>();

        if (pricePoints.size() != 0)
            median = pricePoints.get(0).price;

        for (HistogramEntry pricePoint: pricePoints) {
            price_queue.addFirst(pricePoint);
            total_value += pricePoint.price * pricePoint.size;
            volume += pricePoint.size;
            if (pricePoint.price > max)
                max = pricePoint.price;
            if (pricePoint.price < min)
                min = pricePoint.price;
            half = Double.parseDouble(String.valueOf(volume))/2.0;
            while (half > threshold) {
                HistogramEntry entry = price_queue.removeLast();
                threshold += entry.size;
                median = entry.price;
            }
        }

        double mean = total_value/Double.parseDouble(String.valueOf(volume));
        double variance = 0;

        for (HistogramEntry pricePoint: pricePoints) {
            variance += Math.pow(pricePoint.price - mean, 2) * pricePoint.size;
        }
        double stdev = Math.sqrt(variance);

        String template = "INSERT INTO histogram (timestamp, symbol, mean, median, min, max, stdev, volume, histogram)" +
                "VALUES (TIMESTAMP '%s', '%s', %f, %f, %f, %f, %f, %d, '%s')";
        String query = String.format(template, timestamp, symbol, mean, median, min, max, stdev, volume, literal);
        DatabaseConn.getInstance().execUpdate(query);
    }

    static void updateRealTimeBar(String symbol, long time, double open, double close, double high,
                                               double low, long volume, double wap, int count) {
        String template = "INSERT INTO bar (timestamp, symbol, open, close, high, low, volume, wap, count) " +
                "VALUES (TIMESTAMP '%s', '%s', %f, %f, %f, %f, %d, %f, %d)";
        String timestamp = Helper.timestampToString(new Timestamp(time * 1000));
        String query = String.format(template, timestamp, symbol, open, close, high, low, volume, wap, count);
        DatabaseConn.getInstance().execUpdate(query);
    }

    static void updateTickPrice(String symbol, int field, double price) {
        if (price == -1) return;
        String type = tickTypes.get(field);
        String event = type.split("_")[0];
        String timestamp = Helper.timestampNow();

        // prepare register: bid_size, bid_price, ask_price, ask_size, last_price, last_size, last_time
        String[] s = {"NULL", "NULL", "NULL", "NULL", "NULL", "NULL"};
        if (register.containsKey(symbol)) {
            s = register.get(symbol);
            s[field] = String.valueOf(price);
        } else {
            s[field] = String.valueOf(price);
            register.put(symbol, s);
        }

        // prepare insertion statement
        String values = "";
        switch (field) {
            case 1: //bid_price
                s[0] = "NULL";
                values = String.format("NULL, %s, %s, %s, %s, %s", s[1], s[2], s[3], s[4], s[5]);
                break;
            case 2: //ask_price
                s[3] = "NULL";
                values = String.format("%s, %s, %s, NULL, %s, %s", s[0], s[1], s[2], s[4], s[5]);
                break;
            case 4: // "last_price"
                s[5] = "NULL";
                values = String.format("%s, %s, %s, %s, %s, NULL", s[0], s[1], s[2], s[3], s[4]);
                break;
            default:
                // nothing
        }
        // update register
        register.put(symbol, s);
        String insertion = "INSERT INTO tick (timestamp, symbol, event, bid_size, bid_price, " +
                           "ask_price, ask_size, last_price, last_size) VALUES ('%s', '%s', '%s', %s)";
        if (field == 4) { //only update last index for last price
            insertion += " RETURNING index";
            String statement = String.format(insertion, timestamp, symbol, event, values);
            ResultSet resultSet = DatabaseConn.getInstance().execSync(statement);
            if (resultSet == null) return; // this is triggered by using simulated trading
            try {
                resultSet.next();
                int index = resultSet.getInt("index");
                lastPtr.put(symbol, index);
            } catch (SQLException e) {
                e.printStackTrace();
            }
        } else {
            String statement = String.format(insertion, timestamp, symbol, event, values);
            DatabaseConn.getInstance().execUpdate(statement);
        }
    }

    static void updateTickSize(String symbol, int field, int size) {
        if (size == -1) return;
        String timestamp = Helper.timestampNow();
        String type = tickTypes.get(field);
        String event = type.split("_")[0];

        String[] r = register.get(symbol);
        if (r[field] == "NULL") { // size tick after price tick
            r[field] = Integer.toString(size);
            register.put(symbol, r);
            String update = "WITH latest AS (SELECT * FROM tick WHERE symbol='%s' ORDER BY index DESC LIMIT 1) " +
                            "UPDATE tick SET %s=%d FROM latest WHERE tick.index=latest.index;";
            String statement = String.format(update, symbol, type, size);
            DatabaseConn.getInstance().execUpdate(statement);
        } else if (size != Integer.parseInt(r[field])) { // not a duplicate size tick
            // update register
            r[field] = Integer.toString(size);
            register.put(symbol, r);
            String insertion = "INSERT INTO tick (timestamp, symbol, event, bid_size, bid_price, " +
                    "ask_price, ask_size, last_price, last_size) VALUES ('%s', '%s', '%s', %s, %s, %s, %s, %s, %s)";
            String statement = String.format(insertion, timestamp, symbol, event, r[0], r[1], r[2], r[3], r[4], r[5]);
            DatabaseConn.getInstance().execUpdate(statement);
        } // otherwise, duplicate size tick
    }

    static void updateTickExchange(String symbol, String column, String exchange) { //TODO: IGNORE EXCHANGE FOR SPEED
        //String template = "WITH lastRow AS (SELECT * FROM tick WHERE symbol = '%s' ORDER BY index DESC LIMIT 1) " +
        //                  "UPDATE tick SET %s='%s' FROM lastRow ";
        //String query = String.format(template, symbol, column, exchange);
        //DatabaseConn.getInstance().execUpdate(query);
    }

    static void updateTickLastTime(String symbol, String time) {
        long unixTime = Long.parseLong(time);
        Timestamp timestamp = new Timestamp(unixTime * 1000);
        int lastIndex = lastPtr.get(symbol);
        String template = "UPDATE tick SET last_time='%s' WHERE index=%s";
        String query = String.format(template, timestamp.toString(), lastIndex);
        DatabaseConn.getInstance().execUpdate(query);
    }

    static void updateFundamentalRatios(String symbol, String ratios) {
        String date = Helper.today();
        StringBuilder fields = new StringBuilder();
        StringBuilder entries = new StringBuilder();
        LinkedList<String> columns = new LinkedList<>();
        LinkedList<String> values = new LinkedList<>();
        for (String ratio : ratios.split(";")) {
            if (ratio.contains("=")) {
                String[] pair = ratio.toLowerCase().split("=");
                columns.add((pair[0]).trim());
                if (pair[0].trim().equals("currency") || pair[0].trim().equals("latestadate")) {
                    values.add(String.format("'%s'",pair[1].trim()));
                } else {
                    if (pair[1].trim().equals("-99999.99")) {
                        values.add("NULL");
                    } else {
                        values.add(pair[1].trim());
                    }
                }
            }
        }

        while (!columns.isEmpty()) {
            fields.append(columns.pop());
            fields.append(",");
        }

        while (!values.isEmpty()) {
            entries.append(values.pop());
            entries.append(",");
        }

        String fields_query = fields.toString();
        String entries_query = entries.toString();
        fields_query = fields_query.substring(0, fields_query.length()-1);
        entries_query = entries_query.substring(0, entries_query.length()-1);
        String query_template = "INSERT INTO fundamental_ratios (symbol, date, %s) VALUES ('%s', '%s', %s)";
        String query = String.format(query_template, fields_query, symbol, date, entries_query);
        DatabaseConn.getInstance().execUpdate(query);
    }

    static void updateOpenClose(boolean isOpen, String symbol, double price) {
        String column = isOpen?"open":"lastclose";
        String strPrice = Double.toString(price);
        String date = Helper.today();
        String query_template = "DO $$ BEGIN " +
                                "IF EXISTS (SELECT * FROM open_close WHERE symbol='%s' AND date='%s') THEN " +
                                    "UPDATE open_close SET %s=%s WHERE symbol='%s' AND date='%s'; " +
                                "ELSE " +
                                    "INSERT INTO open_close (date, symbol, %s) VALUES ('%s', '%s', %s); " +
                                "END IF; " +
                                "END $$";
        String query = String.format(query_template, symbol, date,
                                        column, strPrice, symbol, date,
                                        column, date, symbol, strPrice);
        DatabaseConn.getInstance().execUpdate(query);
    }

    static void updateHistoricBar(String symbol, String timestamp, double open, double high, double low, double close, long volume, int count, double wap) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMdd  HH:mm:ss");
        String dateTime = LocalDateTime.parse(timestamp, formatter).toString();
        String insertion = "INSERT INTO bar_history(symbol, timestamp, open, high, low, close, volume, count, wap) " +
                           "VALUES ('%s', '%s', %s, %s, %s, %s, %s, %s, %s)";
        String statement = String.format(insertion, symbol, dateTime, open, high, low, close, volume, count, wap);
        DatabaseConn.getInstance().execUpdate(statement);
    }

    static void updateHighLow(String symbol, int field, double price) {
        String column = "";
        switch (field) {
            case 15: //13-week low
                column = "low13"; break;
            case 16: //13-week high
                column = "high13"; break;
            case 17: //26-week low
                column = "low26"; break;
            case 18: //26-week high
                column = "high26"; break;
            case 19: //52-week low
                column = "low52"; break;
            case 20: //52-week high
                column = "high52"; break;
            case 21: //90-days average daily volume(multiple of 100)
                column = "vol90"; break;
            default:
        }
        String update = "INSERT INTO high_low(symbol, %s) VALUES('%s', %s) ON CONFLICT (symbol) DO UPDATE SET %s = %s";
        String statement = String.format(update, column, symbol, price, column, price);
        DatabaseConn.getInstance().execUpdate(statement);
    }
}
