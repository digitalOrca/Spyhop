import enums.Action;
import org.junit.jupiter.api.Test;

import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 12/30/17.
 */
class StrategyExecutorTest {
    @Test
    void loadTask() {
        StrategyExecutor.loadTask();
        for (OrderTracer ot: StrategyExecutor.orderBook.values()) {
            System.out.println(ot.toString());
        }
    }
}