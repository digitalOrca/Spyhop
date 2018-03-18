import com.ib.client.EReader;
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
    void callbackTrackBitmap() {
        EWrapperImpl client = new EWrapperImpl();
        MainGateway.callbackTracker = 0; //reset bits
        MainGateway.callbackTracker |= 1;
        assertEquals(MainGateway.callbackTracker, 1);
        for (int field = 15; field < 22; field++) {
            MainGateway.callbackTracker |= (int) Math.pow(2, (field - 14));
        }
        assertEquals(MainGateway.callbackTracker, 255);
    }

    @Test
    void updateBenchmark() {
        UpdateAction.updateBenchmark();
    }

}