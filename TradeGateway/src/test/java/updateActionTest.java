import org.junit.jupiter.api.Test;
import utils.DatabaseConn;
import utils.Helper;

import java.sql.ResultSet;
import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 9/30/17.
 */
class updateActionTest {
    @Test
    void updateIndices() {
        // backup any existing data
        String today = Helper.today();
        String query_template_1 = "UPDATE benchmark SET date='1990-10-03' WHERE date='%s'";
        String query_1 = String.format(query_template_1, today);
        DatabaseConn.getInstance().execUpdate(query_1);
        // run test subject
        UpdateAction.updateIndices();
        // verify database entry
        int count = 0;
        String query_template_2 = "SELECT COUNT(*) FROM benchmark WHERE date='%s'";
        String query_2 = String.format(query_template_2, today);
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(query_2);
        try {
            resultSet.next();
            count = resultSet.getInt("count");
        } catch (SQLException e) {
            e.printStackTrace();
        }
        if (count == 0) {
            fail("updateIndices failed");
        } else {
            String query_template_3 = "DELETE FROM benchmark WHERE date='1990-10-03'";
            String query_3 = String.format(query_template_3, today);
            DatabaseConn.getInstance().execUpdate(query_3);
        }
    }

}