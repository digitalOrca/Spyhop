import org.junit.jupiter.api.Test;
import utils.Helper;

import java.io.File;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 9/30/17.
 */
class helperTest {
    @Test
    void runCmd_1() {
        Helper.runCmd(new String[] {"touch", "/home/meng/Projects/NeuroTrader/TradeGateway/build/test/TESTFILE"}, true);
        File test_file = new File("/home/meng/Projects/NeuroTrader/TradeGateway/build/test/TESTFILE");
        if (test_file.exists()) {
            Helper.runCmd(new String[] {"rm", "-f", "/home/meng/Projects/NeuroTrader/TradeGateway/build/test/TESTFILE"}, true);
        } else {
            fail("Shell operation failed");
        }
    }

    @Test
    void runCmd_2() {
        String result = Helper.runCmd(new String[] {"ls", "/home/meng/Projects"});
        if (result != null || result != "") {
            System.out.println(result);
        } else {
            fail("Invalid shell command return");
        }
    }

}