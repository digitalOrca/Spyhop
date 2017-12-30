import enums.Exchange;
import org.junit.jupiter.api.Test;
import utils.DatabaseConn;
import utils.Helper;
import utils.SocketComm;

import java.sql.ResultSet;
import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 10/6/17.
 */
class EWrapperImplTest {
    @Test
    void tickPrice_9() {
        EWrapperImpl client = new EWrapperImpl();
        int reqId = MainGateway.reqIdUpdateBase+1;
        SocketComm.getInstance().registerSymbol(reqId, "TEST");
        String today = Helper.today();
        // backup current entry
        String backup_query_template = "UPDATE open_close SET date='1990-10-03' WHERE date='%s'";
        String backup_query = String.format(backup_query_template, today);
        DatabaseConn.getInstance().execUpdate(backup_query);
        // callback for previous day's close price
        client.tickPrice(reqId, 9, 1.1, null);
        // validate database entry
        String validate_query_template = "SELECT COUNT(*) FROM open_close WHERE date='%s'";
        String validate_query = String.format(validate_query_template, today);
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(validate_query);
        try {
            resultSet.next();
            int count = resultSet.getInt("count");
            assertEquals(1, count);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            String restore_query_template = "UPDATE open_close SET date='%s' WHERE date='1990-10-03'";
            String restore_query = String.format(restore_query_template, today);
            DatabaseConn.getInstance().execUpdate(restore_query);
            String clear_test = "DELETE FROM open_close WHERE symbol='TEST'";
            DatabaseConn.getInstance().execUpdate(clear_test);
        }
    }

    @Test
    void tickPrice_14() {
        EWrapperImpl client = new EWrapperImpl();
        int reqId = MainGateway.reqIdUpdateBase + 1;
        SocketComm.getInstance().registerSymbol(reqId, "TEST");
        String today = Helper.today();
        // backup current entry
        String backup_query_template = "UPDATE open_close SET date='1990-10-03' WHERE date='%s'";
        String backup_query = String.format(backup_query_template, today);
        DatabaseConn.getInstance().execUpdate(backup_query);
        // callback for previous day's close price
        client.tickPrice(reqId, 14, 1.1, null);
        // validate database entry
        String validate_query_template = "SELECT COUNT(*) FROM open_close WHERE date='%s'";
        String validate_query = String.format(validate_query_template, today);
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(validate_query);
        try {
            resultSet.next();
            int count = resultSet.getInt("count");
            assertEquals(1, count);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            String restore_query_template = "UPDATE open_close SET date='%s' WHERE date='1990-10-03'";
            String restore_query = String.format(restore_query_template, today);
            DatabaseConn.getInstance().execUpdate(restore_query);
            String clear_test = "DELETE FROM open_close WHERE symbol='TEST'";
            DatabaseConn.getInstance().execUpdate(clear_test);
        }
    }

    @Test
    void tickPriceSize() {
        EWrapperImpl client = new EWrapperImpl();
        SocketComm.getInstance().registerSymbol(1, "TEST");
        client.tickPrice(1, 1, 0.1, null);
        client.tickSize(1, 0, 1);
        client.tickPrice(1, 2, 0.2, null);
        client.tickSize(1, 3, 2);
        client.tickPrice(1, 4, 0.3, null);
        client.tickSize(1, 5, 3);
        client.tickSize(1, 5, 4);
        String validate_query_1 = "SELECT COUNT(*) FROM tick";
        String validate_query_2 = "SELECT bid_size, bid_price, ask_price, ask_size, last_price, last_size FROM tick " +
                                  "ORDER BY timestamp DESC LIMIT 1";
        ResultSet resultSet1 = DatabaseConn.getInstance().execQuery(validate_query_1);
        ResultSet resultSet2 = DatabaseConn.getInstance().execQuery(validate_query_2);
        try {
            resultSet1.next();
            resultSet2.next();
            int count = resultSet1.getInt("count");
            int bid_size = resultSet2.getInt("bid_size");
            float bid_price = resultSet2.getFloat("bid_price");
            int ask_size = resultSet2.getInt("ask_size");
            float ask_price = resultSet2.getFloat("ask_price");
            int last_size = resultSet2.getInt("last_size");
            float last_price = resultSet2.getFloat("last_price");
            assertEquals(4, count);
            assertEquals(1, bid_size);
            assertEquals((float)0.1, bid_price);
            assertEquals((float)0.2, ask_price);
            assertEquals(2, ask_size);
            assertEquals((float)0.3, last_price);
            assertEquals(4, last_size);
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            DatabaseConn.getInstance().execUpdate("DELETE FROM tick");
        }
    }

    @Test
    void lastTime() {
        EWrapperImpl client = new EWrapperImpl();
        SocketComm.getInstance().registerSymbol(1, "TEST");
        client.tickPrice(1, 4, 0.1, null);
        client.tickString(1, 45, "654912000");
        client.tickPrice(1, 4, 0.2, null);
        client.tickString(1, 45, "686448000");
        String validate_query = "SELECT COUNT(DISTINCT last_time) FROM tick";
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(validate_query);
        try {
            resultSet.next();
            int count = resultSet.getInt("count");
            assertEquals(count, 2);
        } catch ( SQLException e) {
            e.printStackTrace();
        } finally {
            DatabaseConn.getInstance().execUpdate("DELETE FROM tick");
        }
    }

}