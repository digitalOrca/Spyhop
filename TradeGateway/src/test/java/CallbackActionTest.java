import org.junit.jupiter.api.Test;
import utils.DatabaseConn;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedList;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 11/29/17.
 */
class CallbackActionTest {
    @Test
    void selectAllStocks() {
        LinkedList<String> allSymbols = CallbackAction.selectAllStocks();
        assertTrue(true);
    }

    @Test
    void test_selectActiveStocks() {
        LinkedList<String> symbols = CallbackAction.selectActiveStocks();
        assertEquals(symbols.size(), 95); //target depending on the database status column
    }

    @Test
    void test_updateDividend() {
        CallbackAction.updateDividend("TEST", "0.83,0.92,20130219,0.23");
        String validate_query = "SELECT COUNT(*) FROM dividend WHERE symbol='TEST'";
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(validate_query);
        try {
            resultSet.next();
            int count = resultSet.getInt("count");
            assertEquals(count, 1);
        } catch ( SQLException e) {
            e.printStackTrace();
        } finally {
            DatabaseConn.getInstance().execUpdate("DELETE FROM dividend WHERE symbol='TEST'");
        }
    }
}