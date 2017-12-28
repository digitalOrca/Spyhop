import com.ib.client.*;
import enums.Currency;
import enums.Exchange;
import enums.SecType;
import org.json.simple.parser.JSONParser;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import java.io.FileReader;
import java.util.HashMap;

/**
 * Created by meng on 6/7/17.
 */
public class StrategyExecutor implements Runnable {

    private static StrategyExecutor ourInstance = new StrategyExecutor();

    public static StrategyExecutor getInstance() {
        return ourInstance;
    }

    private StrategyExecutor() {
    }

    public static HashMap<String, Integer> buy_backlog = new HashMap<>();
    public static HashMap<String, Integer> sell_backlog = new HashMap<>();
    public static HashMap<String, Integer> buy_active = new HashMap<>();
    public static HashMap<String, Integer> sell_active = new HashMap<>();

    @SuppressWarnings("unchecked")
    public static void loadTask() {
        JSONParser parser = new JSONParser();
        try {
            JSONObject jsonObject = (JSONObject) parser.parse(
                    new FileReader("/home/meng/Projects/NeuroTrader/TradeQueue.json"));
            JSONArray buyList = (JSONArray)jsonObject.get("BUY");
            JSONArray sellList = (JSONArray)jsonObject.get("SELL");
            for (Object jsonObj : buyList) {
                String symbol =  (String)((JSONObject)jsonObj).get("symbol");
                Integer quantity = (int)(long)((JSONObject)jsonObj).get("quantity");
                buy_backlog.put(symbol, quantity);
            }
            for (Object jsonObj : sellList) {
                String symbol =  (String)((JSONObject)jsonObj).get("symbol");
                Integer quantity = (int)(long)((JSONObject)jsonObj).get("quantity");
                sell_backlog.put(symbol, quantity);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void trigger(int orderId, String symbol, String action) {
        if (action == "BUY") {
            buy_active.put(symbol, buy_backlog.remove(symbol));
        } else {
            sell_active.put(symbol, sell_backlog.remove(symbol));
        }
        Contract contract = OrderBuilder.makeContract(symbol, SecType.STK, Exchange.SMART, Currency.USD);
        Order order = OrderBuilder.createMarketOrder(action, buy_backlog.get(symbol));
        MainGateway.client.getClientSocket().placeOrder(orderId, contract, order);
    }

    @Override
    public void run() {

    }
}
