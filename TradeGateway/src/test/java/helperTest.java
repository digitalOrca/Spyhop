import org.junit.jupiter.api.Test;
import utils.Helper;

import java.io.File;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 9/30/17.
 */
class helperTest {
    @Test
    void runCmd() {
        Helper.runCmd(new String[] {"touch", "/home/meng/Projects/NeuroTrader/TradeGateway/build/test/TESTFILE"}, true);
        File test_file = new File("/home/meng/Projects/NeuroTrader/TradeGateway/build/test/TESTFILE");
        if (test_file.exists()) {
            Helper.runCmd(new String[] {"rm", "-f", "/home/meng/Projects/NeuroTrader/TradeGateway/build/test/TESTFILE"}, true);
        } else {
            fail("Shell operation failed");
        }
    }

}