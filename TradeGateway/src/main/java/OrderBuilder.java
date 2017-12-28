import com.ib.client.*;
import enums.*;


/**
 * Created by meng on 5/14/17.
 */
final public class OrderBuilder { // Make final to prevent modification and extension

    private OrderBuilder(){  }// Make private to prevent instantiation, only static methods are used

    /* generic contract template */
    public static Contract makeContract(String symbol, SecType secType, Exchange exchange, enums.Currency currency){
        Contract contract = new Contract();
        contract.symbol(symbol);
        contract.secType(secType.toString());
        contract.exchange(exchange.toString());
        contract.currency(currency.toString());
        return contract;
    }

    public static Order createMarketOrder(String action, int quantity) {
        Order order = new Order();
        order.action(action);
        order.orderType("MKT");
        order.totalQuantity(quantity);
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
