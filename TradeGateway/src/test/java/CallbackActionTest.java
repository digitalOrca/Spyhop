import org.junit.jupiter.api.Test;
import utils.DatabaseConn;

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
}