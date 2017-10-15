import enums.Exchange;
import org.junit.jupiter.api.Test;
import utils.DatabaseConn;
import utils.Helper;
import utils.SocketComm;

import java.sql.ResultSet;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 10/6/17.
 */
class EWrapperImplTest {
    @Test
    void tickPrice_9() {
        EWrapperImpl client = new EWrapperImpl();
        int reqId = 1001;
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
        }
    }

    @Test
    void tickPrice_14() {
        EWrapperImpl client = new EWrapperImpl();
        int reqId = 1001;
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
        }
    }

    @Test
    void tickSize() {
    }

}