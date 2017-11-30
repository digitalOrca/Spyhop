import org.junit.jupiter.api.Test;

import java.util.LinkedList;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 11/29/17.
 */
class CallbackActionTest {
    @Test
    void selectActiveStocks() {
        LinkedList<String> symbols = CallbackAction.selectActiveStocks();
        assertEquals(symbols.size(), 95); //target depending on the database status column
    }

}