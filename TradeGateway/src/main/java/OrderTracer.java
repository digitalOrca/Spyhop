import enums.Action;
import enums.OrderStage;

/**
 * Created by meng on 1/6/18.
 */
public class OrderTracer {

    private int orderId;
    private String symbol;
    private Action action;
    private int quantity;
    private OrderStage status;

    public OrderTracer() {

    }

    public OrderTracer(String symbol, Action action, int quantity) {
        this.symbol = symbol;
        this.action = action;
        this.quantity = quantity;
        this.status = OrderStage.BACKLOG;
    }

    public void setOrderId(int orderId) {
        this.orderId = orderId;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public void setAction(Action action) {
        this.action = action;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public void setStatus(OrderStage status) {
        this.status = status;
    }

    public int getOrderId() {
        return this.orderId;
    }

    public String getSymbol() {
        return this.symbol;
    }

    public Action getAction() {
        return this.action;
    }

    public int getQuantity() {
        return this.quantity;
    }

    public OrderStage getStatus() {
        return this.status;
    }

    public String toString() {
        String template = "orderId: %s, symbol:%s, action:%s, quantity:%s, status:%s";
        String orderPrint = String.format(template, orderId, symbol, action, quantity, status);
        return orderPrint;
    }
}
