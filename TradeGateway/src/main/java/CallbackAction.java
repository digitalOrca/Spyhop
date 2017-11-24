/**
 * Created by meng on 8/6/17.
 */

import com.ib.client.HistogramEntry;
import com.ib.client.TickType;
import utils.DatabaseConn;
import utils.Helper;

import java.sql.*;
import java.util.*;

class CallbackAction {

    private static Map<Integer, String> tickTypes = new HashMap<>();

    private static HashMap<String, String[]> register = new HashMap<>();

    static { // static initialization of tickTypes
        for (int tickId : EWrapperImpl.validTicks) {
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
        String query = "SELECT symbol FROM stocks WHERE active=TRUE ORDER BY symbol DESC";
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

    static void updateTickPrice_backup(String symbol, int field, double price) {
        if (price == -1) return;
        String type = tickTypes.get(field);
        String event = type.split("_")[0];
        String eventSize = event + "_size";
        String timestamp = Helper.timestampNow();
        // Duplicating the latest row
        String copyLatest = "INSERT INTO tick " +
                            "(timestamp, symbol, event,  bid_price, bid_size, bid_exchange, ask_price, ask_size, " +
                                "ask_exchange, last_price, last_size, last_exchange, last_time) " +
                            "SELECT timestamp, symbol, event, bid_price, bid_size, bid_exchange, ask_price, " +
                                "ask_size, ask_exchange, last_price, last_size, last_exchange, last_time " +
                            "FROM tick WHERE symbol = '%s' ORDER BY index DESC LIMIT 1 RETURNING index";
        String query1 = String.format(copyLatest, symbol);
        ResultSet resultSet1 = DatabaseConn.getInstance().execQuery(query1);
        int lastIndex = 0;
        boolean wasNull = true;
        try {
            if (resultSet1 != null && resultSet1.next()) {
                lastIndex = resultSet1.getInt("index");
                wasNull = resultSet1.wasNull();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        // Insert new row if not duplicated
        if (wasNull) {
            String firstRow = "INSERT INTO tick (symbol) VALUES ('%s') RETURNING index";
            String query0 = String.format(firstRow, symbol);
            ResultSet resultSet2 = DatabaseConn.getInstance().execQuery(query0);
            try {
                if (resultSet2 != null && resultSet2.next()) {
                    lastIndex = resultSet2.getInt("index");
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        // Update price tick and prepare NULL for size tick
        String updatePrice = "UPDATE tick SET timestamp='%s', event='%s', %s=%f, %s=NULL WHERE index=%d";
        String query2 = String.format(updatePrice, timestamp, event, type, price, eventSize, lastIndex);
        DatabaseConn.getInstance().execUpdate(query2);
    }

    static void updateTickPrice(String symbol, int field, double price) { //TODO: THIS IS NOT TESTED
        if (price == -1) return;
        String type = tickTypes.get(field);
        String event = type.split("_")[0];
        String eventSize = event + "_size";
        String timestamp = Helper.timestampNow();

        // update register
        if (register.containsKey(symbol)) {
            String[] r = register.get(symbol);
            r[field] = String.valueOf(price);
            register.put(symbol, r);
        } else {
            String[] r = {"NULL", "NULL", "NULL", "NULL", "NULL", "NULL"};
            r[field] = String.valueOf(price);
            register.put(symbol, r);
        }

        // prepare insertion statement
        String[] s = register.get(symbol);
        String values;
        switch (type) {
            case "bid_price":
                values = String.format("NULL, %s, %s, %s, %s, %s", s[1], s[2], s[3], s[4], s[5]);
                break;
            case "ask_price":
                values = String.format("%s, %s, %s, NULL, %s, %s", s[0], s[1], s[2], s[4], s[5]);
                break;
            default: // "last_price"
                values = String.format("%s, %s, %s, %s, %s, NULL", s[0], s[1], s[2], s[3], s[4]);
        }

        String insertion = "INSERT INTO tick (timestamp, symbol, event, bid_size, bid_price, " +
                           "ask_price, ask_size, last_price, last_size) VALUE ('%s', '%s', '%s', %s)";
        String statement = String.format(insertion, timestamp, symbol, event, values);
        DatabaseConn.getInstance().execUpdate(statement);
    }

    static void updateTickSize_backup(String symbol, int field, int size) {
        if (size == -1) return;
        String timestamp = Helper.timestampNow();
        String type = tickTypes.get(field);
        String event = type.split("_")[0];
        // Get previous size
        String lastRow = "SELECT index, %s from tick WHERE symbol='%s' ORDER BY index DESC LIMIT 1";
        String queryLastRow = String.format(lastRow, type, symbol);
        ResultSet resultSet1 = DatabaseConn.getInstance().execQuery(queryLastRow);
        int lastSize = 0;
        int lastIndex = 0;
        try {
            if (resultSet1 != null && resultSet1.next()) {
                lastSize = resultSet1.getInt(type);
                lastIndex = resultSet1.getInt("index");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        if (lastSize == 0) {
            // Update size after price tick
            String template = "UPDATE tick SET %s=%d, event='%s' WHERE index=%d";
            String query = String.format(template, type, size, event, lastIndex);
            DatabaseConn.getInstance().execUpdate(query);
        } else if (lastSize != size) {
            // Insert price update
            // Duplicate the last row
            String duplication = "INSERT INTO tick " +
                                 "(timestamp, symbol, event, bid_price, bid_size, bid_exchange, ask_price, ask_size, " +
                                     "ask_exchange, last_price, last_size, last_exchange, last_time) " +
                                 "SELECT timestamp, symbol, event, bid_price, bid_size, bid_exchange, ask_price, " +
                                     "ask_size, ask_exchange, last_price, last_size, last_exchange, last_time " +
                                 "FROM tick WHERE index=%d RETURNING index";
            String query1 = String.format(duplication, lastIndex);
            ResultSet resultSet2 = DatabaseConn.getInstance().execQuery(query1);
            int newIndex = 0;
            try {
                if (resultSet2 != null && resultSet2.next()) {
                    newIndex = resultSet2.getInt("index");
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
            // Update the duplicate row
            String updatePrice = "UPDATE tick SET event='%s', timestamp='%s', %s=%d WHERE index=%d";
            String query2 = String.format(updatePrice, event, timestamp, type, size, newIndex);
            DatabaseConn.getInstance().execUpdate(query2);
        } // Otherwise, it is a duplicated size tick
    }

    static void updateTickSize(String symbol, int field, int size) { //TODO: THIS IS NOT TESTED
        if (size == -1) return;
        String timestamp = Helper.timestampNow();
        String type = tickTypes.get(field);
        String event = type.split("_")[0];

        String[] r = register.get(symbol);
        if (r[field] == "NULL") { // size tick after price tick
            r[field] = Integer.toString(size);
            register.put(symbol, r);
            String update = "UPDATE tick SET %s=%d WHERE symbol='%s' ORDER BY index DESC LIMIT 1";
            String statement = String.format(update, type, size, symbol);
            DatabaseConn.getInstance().execUpdate(statement);
        } else if (size != Integer.parseInt(r[field])) { // not a duplicate size tick
            // update register
            r[field] = Integer.toString(size);
            register.put(symbol, r);
            String insertion = "INSERT INTO tick (timestamp, symbol, event, bid_size, bid_price, " +
                    "ask_price, ask_size, last_price, last_size) VALUE ('%s', '%s', '%s', %s, %s, %s, %s, %s, %s)";
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

    static void updateTickLastTime(String symbol, String time) { //TODO: BYPASS IF NOT USED LATER
        long unixTime = Long.parseLong(time);
        Timestamp timestamp = new Timestamp(unixTime * 1000);
        String template = "WITH lastRow AS (SELECT * FROM tick WHERE symbol = '%s' ORDER BY index DESC LIMIT 1) " +
                          "UPDATE tick SET %s='%s' FROM lastRow ";
        String column = "last_time";
        String query = String.format(template, symbol, column, timestamp.toString());
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
}
