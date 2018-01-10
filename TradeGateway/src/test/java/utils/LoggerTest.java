package utils;

import enums.Log;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 12/30/17.
 */
class LoggerTest {
    @Test
    void log() {
        Logger.getInstance().setLogMode("TEST");
        Logger.getInstance().log(Log.ACTION, "UNITTEST ACTION LOG");
        Logger.getInstance().log(Log.CALLBACK, "UNITTEST CALLBACK LOG");
    }

}