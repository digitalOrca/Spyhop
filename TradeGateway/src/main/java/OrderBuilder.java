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

    public static Order createAuctionOrder(Action action, int quantity, double price) {  //for pre-market opening period
        Order order = new Order();
        order.action(action.toString());
        order.tif("AUC");
        order.orderType("MTL");
        order.totalQuantity(quantity);
        order.lmtPrice(price);
        return order;
    }

    public static Order createDiscretionaryOrder(Action action, int quantity, double price, double discretionaryAmt) {
        Order order = new Order();
        order.action(action.toString());
        order.orderType("LMT");
        order.totalQuantity(quantity);
        order.lmtPrice(price);
        order.discretionaryAmt(discretionaryAmt);
        return order;
    }

    public static Order createMarketOrder(Action action, int quantity) {
        Order order = new Order();
        order.action(action.toString());
        order.orderType("MKT");
        order.totalQuantity(quantity);
        return order;
    }
}
