import java.util.*;
import com.ib.client.*;
import enums.*;
import enums.Currency;

import java.util.concurrent.TimeUnit;


/**
 * Created by meng on 5/14/17.
 */
final public class OrderBuilder { // Make final to prevent modification and extension

    //static MBLogger actionLogger = new MBLogger("../Logs/enums.Action");

    private OrderBuilder(){  }// Make private to prevent instantiation, only static methods are used

    /*
        Implement action logging for performance analysis
     */

    /*
    utils.Helper Identification Utilities
     */
    static int reqId = 0;
    static HashMap<Integer, String> currReqId = new HashMap<>();   // Bookkeeping for current request

    public static int getReqId(String symbol) { // Return a unique request id(ticker id)
        currReqId.put(++reqId, symbol);
        return reqId;
    }

    public static String verifyRequest(int reqId) {
        if(currReqId.containsKey(reqId)) {
            return currReqId.get(reqId);
        }
        return "";  //TODO: THINK ABOUT HOW TO REMOVE ONE THE CALL BACK IS DONE???
    }

    public static void requestMarketData(EWrapperImpl client, String symbol, SecType secType, Exchange exchange,
                                         Currency currency, int tickerId, String genericTickList, boolean snapshot,
                                         boolean regulatorySnapshot, List<TagValue>	mktDataOptions) {
        Contract contract = makeContract(symbol, secType, exchange, currency);
        client.getClientSocket().reqMktData(tickerId, contract, genericTickList, snapshot, regulatorySnapshot,
                mktDataOptions);
    }

    /*
    Batch Historical Data Request
     */
    public static void batchReqHistData(EWrapperImpl client, List<String> symbols, SecType secType, Exchange exchange,
                                        Currency currency, String endDateTime, String duration, String barSize,
                                        String whatToShow, int RTH, int formatDate, List<TagValue> chartOptions) {
        for(String symbol:symbols) {
            System.out.println("Requesting historical data for " + symbol);
            requestHistoricalData(client, symbol, secType, exchange, currency, getReqId(symbol), endDateTime, duration,
                    barSize, whatToShow, RTH, formatDate, chartOptions);
        }

    }


    /*
        STANDARD HISTORICAL DATA PULLING METHOD
     */
    public static void requestHistoricalData(EWrapperImpl client, String symbol, SecType secType, Exchange exchange,
                                             Currency currency, int tickerId, String endDateTime, String duration,
                                             String barSize, String whatToShow, int RTH, int formatDate,
                                             List<TagValue> chartOptions) {
        Contract contract = makeContract(symbol, secType, exchange, currency);
        //client.getClientSocket().reqHistoricalData(tickerId, contract, endDateTime, duration, barSize, whatToShow,
        //        RTH, formatDate, chartOptions);
    }

    /*
        STANDARD CONTRACT TEMPLATE
     */
    public static Contract makeContract(String symbol, SecType secType, Exchange exchange, enums.Currency currency){
        Contract contract = new Contract();
        contract.symbol(symbol);
        contract.secType(secType.toString());
        contract.exchange(exchange.toString());
        contract.currency(currency.toString());
        return contract;
    }

    public static void placeOrder(EWrapperImpl client, int orderId, Contract contract, Order order) {

        client.getClientSocket().reqIds(0);

        client.getClientSocket().placeOrder(orderId, contract, order);
        try {
            TimeUnit.MILLISECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    /*
        A Market On Open (MOO) combines a market order with the OPG time in force to create an order that is
        automatically submitted at the market's open and fills at the market price.
        Products: CFD, FUT, STK, WAR

        North America:
        American Stock enums.Exchange (NYSE AMEX)
        Arca (NYSE)
        BATS
        Chicago Board Options enums.Exchange (CBOE)
        CBOE C2
        INET (Island)
        MIAX Options enums.Exchange
        New York Stock enums.Exchange (NYSE)

        Europe:
        Euronext NL Stocks (AEB)
        Borsa Italiana (BVME)
        Swiss enums.Exchange (SWX)
        XETRA (IBIS)
        London Stock enums.Exchange (LSE)
        Euronext France (SBF)
        Swedish Stock enums.Exchange
        VIRT-X (VIRTX)

        Asia/Pacific:
        Hong Kong Stock enums.Exchange (SEHK)
        Singapore enums.Exchange (SGX)
        Tokyo Stock enums.Exchange (TSEJ)
     */
    public static Order makeMarketOrder(String action, int quantity, double price) {
        Order order = new Order();
        order.action(action);
        order.orderType("MIT");
        order.totalQuantity(quantity);
        order.auxPrice(price);
        return order;
    }

















    /*
    public static void requestData(EWrapperImpl client, int dataType, int tickerId, Contract contract, String genericTickList,
                                   boolean snapshot, boolean regulatorySnapshot, List<TagValue> mktDataOption){
        client.getClientSocket().reqMarketDataType(dataType);
        client.getClientSocket().reqMktData(tickerId, contract, genericTickList, snapshot, regulatorySnapshot, mktDataOption);
    }
    */

    /*
    public static Order makeOrder(enums.OrderType orderType, enums.Action action){
        Order order = new Order();
        order.orderType(orderType.toString());
        order.action(action.toString());
        return order;
    }
    */
    /*
    public static Order auctionOrder(String action, String tif, String orderType, int quantity, double limit){ //FUT, STK
        Order order = new Order();
        order.action(action);
        order.tif(tif);
        order.orderType(orderType);
        order.totalQuantity(quantity);
        order.lmtPrice(limit);
        return order;
    }

    public static Order discretionaryOrder(String action, String tif, String orderType, int quantity, double limit,
                                     double discretion){ //FUT, STK
        Order order = new Order();
        order.action(action);
        order.tif(tif);
        order.orderType(orderType);
        order.totalQuantity(quantity);
        order.lmtPrice(limit);
        order.discretionaryAmt(discretion);
        return order;
    }

    public static Order marketOrder(String action, String orderType, int quantity){
        Order order = new Order();
        order.action(action);
        order.orderType(orderType);
        order.totalQuantity(quantity);
        return order;
    }

    public static Order MITOrder(String action, String orderType, int quantity, double auxPrice){ //Market If Touched
        Order order = new Order();
        order.action(action);
        order.orderType(orderType);
        order.totalQuantity(quantity);
        order.auxPrice(auxPrice);
        return order;
    }

    public static Order MOCOrder(String action, String orderType, int quantity){ //Market On Close
        Order order = new Order();
        order.action(action);
        order.orderType(orderType);
        order.totalQuantity(quantity);
        return order;
    }

    public static Order MOOOrder(String action, String orderType, int quantity, String tif){ //Market On Open
        Order order = new Order();
        order.action(action);
        order.orderType(orderType);
        order.totalQuantity(quantity);
        order.tif(tif);
        return order;
    }
    */
}
