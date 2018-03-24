package enums;

/**
 * BACKLOG: order pending to be executed
 * SUBMITTED: submitted pending order
 * FILLED(not implemented): once filled, order will be removed from list
 */
public enum OrderStage {
    BACKLOG, SUBMITTED
}
