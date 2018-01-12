import com.ib.client.*;
import enums.*;
import enums.OrderStage;
import org.json.simple.parser.JSONParser;
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import utils.Helper;
import utils.Logger;
import utils.SocketComm;

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

    public static int orderId;
    public static HashMap<String, OrderTracer> orderBook = new HashMap<>();

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
                OrderTracer orderTracer = new OrderTracer(symbol, Action.BUY, quantity);
                orderBook.put(symbol, orderTracer);
            }
            for (Object jsonObj : sellList) {
                String symbol =  (String)((JSONObject)jsonObj).get("symbol");
                Integer quantity = (int)(long)((JSONObject)jsonObj).get("quantity");
                OrderTracer orderTracer = new OrderTracer(symbol, Action.BUY, quantity);
                orderBook.put(symbol, orderTracer);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void trigger(int orderId, String symbol) {
        SocketComm.getInstance().registerOrder(orderId, symbol);
        OrderTracer orderTracer = orderBook.get(symbol);
        orderTracer.setOrderId(orderId);
        orderTracer.setStatus(OrderStage.SUBMITTED);
        orderBook.put(symbol, orderTracer); // update order book
        Contract contract = OrderBuilder.makeContract(symbol, SecType.STK, Exchange.SMART, Currency.USD);
        Order order = OrderBuilder.createMarketOrder(orderTracer.getAction(), orderTracer.getQuantity());
        Logger.getInstance().log(Log.ACTION, "ORDER, Placed," + symbol + "," + orderTracer.getQuantity());
        MainGateway.client.getClientSocket().placeOrder(orderId, contract, order);
    }

    @Override
    public void run() {
        MainGateway.client.nextValidId(0); //to retrieve next valid order id
        loadTask();

        if (MainGateway.simulated) { // paper trading
            while (!orderBook.isEmpty()) {
                for (OrderTracer ot : orderBook.values() ) {
                    if (ot.getStatus() == OrderStage.BACKLOG ) {
                        Logger.getInstance().log(Log.ACTION, "ORDER, Triggered," + ot.getSymbol());
                        trigger(orderId++, ot.getSymbol());
                        Helper.pauseSec(60);
                    }
                }
            }
        }
    }
}
