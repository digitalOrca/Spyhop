/**
 * Created by meng on 5/13/17.
 */
import java.sql.Timestamp;
import java.util.*;
import com.ib.client.*;
import enums.Log;
import utils.Logger;
import utils.SocketComm;

public class EWrapperImpl implements EWrapper {

    private EReaderSignal readSignal;
    private EClientSocket clientSocket;
    static Set<Integer> validTicks = new HashSet<>(Arrays.asList(0, 1, 2,3,4,5,32,33,45,84));

    EWrapperImpl(){
        readSignal = new EJavaSignal();
        clientSocket = new EClientSocket(this, readSignal);
    }

    void connect(String host, int port, int id, boolean async){
        clientSocket.setAsyncEConnect(async);
        clientSocket.eConnect(host, port, id);
    }

    EReaderSignal getReadSignal(){
        return readSignal;
    }

    EClientSocket getClientSocket(){
        return clientSocket;
    }

    public void tickPrice(int reqId, int field, double price, TickAttr tickAttr) {
        String symbol = SocketComm.getInstance().getSymbol(reqId);
        if (reqId >= MainGateway.reqIdUpdateBase) {
            switch (field) {
                case 9: // previous day's close price
                    CallbackAction.updateOpenClose(false, symbol, price);
                    Logger.getInstance().log(Log.ACTION, "[Callback] [9]" + symbol);
                    break;
                case 14: // today's opening price
                    CallbackAction.updateOpenClose(true, symbol, price);
                    Logger.getInstance().log(Log.ACTION, "[Callback] [14]" + symbol);
                    break;
                default:
                    System.out.println("reqId:" + Integer.toString(reqId) + " field:" + Integer.toString(field) + " price:" + Double.toString(price));
                    break;
            }
        } else if (validTicks.contains(field)) {
            CallbackAction.updateTickPrice(symbol, field, price);
        }
    }

    public void tickSize(int reqId, int field, int size) {
        if (reqId == MainGateway.reqIdUpdateBase)
            return;
        if (validTicks.contains(field)) {
            String symbol = SocketComm.getInstance().getSymbol(reqId);
            CallbackAction.updateTickSize(symbol, field, size);
        }
    }

    public void tickOptionComputation(int i, int i1, double v, double v1, double v2, double v3, double v4, double v5, double v6, double v7) {
        System.out.println("TEST1");
    }

    public void tickGeneric(int i, int i1, double v) {
        System.out.println("TEST2");
    }

    public void tickString(int reqId, int field, String value) {
        String symbol = SocketComm.getInstance().getSymbol(reqId);
        if (symbol.equals("INVALID"))
            return;
        if (reqId >= MainGateway.reqIdUpdateBase) {
            switch (field) {
                case 47: // fundamental ratio
                    CallbackAction.updateFundamentalRatios(symbol, value);
                    Logger.getInstance().log(Log.ACTION, "[Callback] [47]" + symbol);
                    MainGateway.recvFundRatio = true;
                    break;
                default:
                    System.out.println("reqId:" + Integer.toString(reqId) + " field:" + Integer.toString(field) + " value:" + value);
                    break;
            }
        }else if (validTicks.contains(field) && reqId < MainGateway.reqIdUpdateBase) {
            switch (field) {
                case 32: //bid exchange
                    CallbackAction.updateTickExchange(symbol, "bid_exchange", value);
                    break;
                case 33: //ask exchange
                    CallbackAction.updateTickExchange(symbol, "ask_exchange", value);
                    break;
                case 45: //last time
                    CallbackAction.updateTickLastTime(symbol, value);
                    break;
                case 84: //last exchange
                    CallbackAction.updateTickExchange(symbol, "last_exchange", value);
                    break;
                default:
                    System.out.println("reqId:" + Integer.toString(reqId) + " field:" + Integer.toString(field) + " value:" + value);
                    break;
            }
        }
    }

    public void tickEFP(int i, int i1, double v, String s, double v1, int i2, String s1, double v2, double v3) {
        System.out.println("TEST4");
    }

    public void orderStatus(int i, String s, double v, double v1, double v2, int i1, int i2, double v3, int i3, String s1) {
        System.out.println("TEST5");
    }

    public void openOrder(int i, Contract contract, Order order, OrderState orderState) {
        System.out.println("TEST6");
    }

    public void openOrderEnd() {
        System.out.println("TEST7");
    }

    public void updateAccountValue(String s, String s1, String s2, String s3) {
        System.out.println("TEST8");
    }

    public void updatePortfolio(Contract contract, double v, double v1, double v2, double v3, double v4, double v5, String s) {
        System.out.println("TEST9");
    }

    public void updateAccountTime(String s) {
        System.out.println("TEST10");
    }

    public void accountDownloadEnd(String s) {
        System.out.println("TEST11");
    }

    public void nextValidId(int id) {
        System.out.println("Next valid reqId: " + id);
    }

    public void contractDetails(int i, ContractDetails contractDetails) {
        /*
        System.out.println(contractDetails.contract().symbol());
        String symbol = contractDetails.contract().symbol();
        String template = "UPDATE security SET status=1 WHERE symbol='%s'";
        String query = String.format(template, symbol);
        CallbackAction.getInstance().execUpdate(query);
        */
        System.out.println(contractDetails.toString());
    }

    public void bondContractDetails(int i, ContractDetails contractDetails) {
        System.out.println(contractDetails.toString());
    }

    public void contractDetailsEnd(int i) {
        System.out.println("contractDetailsEnd");
    }

    public void execDetails(int i, Contract contract, Execution execution) {
        System.out.println("TEST16");
    }

    public void execDetailsEnd(int i) {
        System.out.println("TEST17");
    }

    public void updateMktDepth(int i, int i1, int i2, int i3, double v, int i4) {
        System.out.println("TEST18");
    }

    public void updateMktDepthL2(int i, int i1, String s, int i2, int i3, double v, int i4) {
        System.out.println("TEST19");
    }

    public void updateNewsBulletin(int i, int i1, String s, String s1) {
        System.out.println("TEST20");
    }

    public void managedAccounts(String accounts) {
        System.out.println("ManagedAccounts: " + accounts);
    }

    public void receiveFA(int i, String s) {
        System.out.println("TEST22");
    }

    public void historicalData(int reqId, Bar bar) {
        CallbackAction.updateHistoricBar(SocketComm.getInstance().getSymbol(reqId), bar.time(), bar.open(), bar.high(), bar.low(), bar.close(), bar.volume(), bar.count(), bar.wap());
    }

    public void scannerParameters(String s) {
        System.out.println("TEST24");
    }

    public void scannerData(int i, int i1, ContractDetails contractDetails, String s, String s1, String s2, String s3) {
        System.out.println("TEST25");
    }

    public void scannerDataEnd(int i) {
        System.out.println("TEST26");
    }

    public void realtimeBar(int reqId, long time, double open, double high, double low, double close, long volume, double wap, int count) {
        consolePrint(reqId, "realtimeBar");
        CallbackAction.updateRealTimeBar(SocketComm.getInstance().getSymbol(reqId), time, open, close, high, low, volume, wap, count);
    }

    public void currentTime(long time) {
        Timestamp timestamp = new Timestamp(time*1000);
        System.out.println("Current time: " + timestamp );
    }

    public void fundamentalData(int reqId, String data) {
        //String TICKER = utils.XmlParser.getText(data, "Issues:0;Issue:0;IssueID:1");
        //String MKTCAP = utils.XmlParser.getText(data, "Ratios:0;Group:1;Ratio:0");
        //String EMPLY = utils.XmlParser.getText(data, "Ratios:0;Group:3;Ratio:5");
        //String query_template = "UPDATE security SET mkt_cap=%s, num_emply=%s WHERE symbol='%s'";
        //String query = String.format(query_template, MKTCAP, EMPLY, TICKER);
        //CallbackAction.getInstance().execUpdate(query);
    }

    public void deltaNeutralValidation(int i, DeltaNeutralContract deltaNeutralContract) {
        System.out.println("TEST30");
    }

    public void tickSnapshotEnd(int i) {
        System.out.println("TEST31");
    }

    public void marketDataType(int i, int i1) {
        System.out.println("TEST32");
    }

    public void commissionReport(CommissionReport commissionReport) {
        System.out.println("TEST33");
    }

    public void position(String s, Contract contract, double v, double v1) {
        System.out.println("TEST34");
    }

    public void positionEnd() {
        System.out.println("TEST35");
    }

    public void accountSummary(int i, String s, String s1, String s2, String s3) {
        System.out.println("TEST36");
    }

    public void accountSummaryEnd(int i) {
        System.out.println("TEST37");
    }

    public void verifyMessageAPI(String s) {
        System.out.println("verifyMessageAPI");
    }

    public void verifyCompleted(boolean b, String s) {
        System.out.println("verifyCompleted");
    }

    public void verifyAndAuthMessageAPI(String s, String s1) {
        System.out.println("verifyAndAuthMessageAPI");
    }

    public void verifyAndAuthCompleted(boolean b, String s) {
        System.out.println("verifyAndAuthCompleted");
    }

    public void displayGroupList(int i, String s) {
        System.out.println("TEST42");
    }

    public void displayGroupUpdated(int i, String s) {
        System.out.println("TEST43");
    }

    public void error(Exception e) {
        System.out.println("Error Message: " + e.getMessage());
    }

    public void error(String errorMsg) {
        System.out.println("Error Message: " + errorMsg);
    }

    public void error(int id, int errorCode, String errorMsg) {
        switch (errorCode) {
            case 162:
                MainGateway.pendingHistReq--;
                break;
            case 200:
                MainGateway.pendingHistReq--;
                break;
            default:
        }
        String error = String.format("[E]pending: %d, id: %d, errorCode: %d, message: %s", MainGateway.pendingHistReq, id, errorCode, errorCode);
        Logger.getInstance().log(Log.CALLBACK, error);
        System.out.println("reqId: " + id + ", Error Code: " + errorCode + ", Error Message: " + errorMsg);
    }

    public void connectionClosed() {
        System.out.println("Connection Closed");
    }

    public void connectAck() {
        if (clientSocket.isAsyncEConnect()) {
            System.out.println("Connection Acknowledged");
            clientSocket.startAPI();
        }
    }

    public void positionMulti(int i, String s, String s1, Contract contract, double v, double v1) {
        System.out.println("TEST48");
    }

    public void positionMultiEnd(int i) {
        System.out.println("TEST49");
    }

    public void accountUpdateMulti(int i, String s, String s1, String s2, String s3, String s4) {
        System.out.println("TEST50");
    }

    public void accountUpdateMultiEnd(int i) {
        System.out.println("TEST51");
    }

    public void securityDefinitionOptionalParameter(int i, String s, int i1, String s1, String s2, Set<String> set, Set<Double> set1) {
        System.out.println("TEST52");
    }

    public void securityDefinitionOptionalParameterEnd(int i) {
        System.out.println("TEST53");
    }

    public void softDollarTiers(int i, SoftDollarTier[] softDollarTiers) {
        System.out.println("TEST54");
    }

    public void familyCodes(FamilyCode[] familyCodes) {
        System.out.println("TEST55");
    }

    public void symbolSamples(int i, ContractDescription[] contractDescriptions) {
        System.out.println("TEST56");
    }

    public void historicalDataEnd(int reqId, String s, String s1) {
        MainGateway.pendingHistReq--;
        String end = String.format("[N]pending: %d, id: %d, s: %s, s1: %s", MainGateway.pendingHistReq, reqId, s, s1);
        Logger.getInstance().log(Log.CALLBACK, end);
        System.out.println("Closing ReqId:"+reqId+", Pending requests:"+MainGateway.pendingHistReq);
    }

    public void mktDepthExchanges(DepthMktDataDescription[] depthMktDataDescriptions) {
        System.out.println("TEST58");
    }

    public void tickNews(int i, long l, String s, String s1, String s2, String s3) {
        System.out.println("TEST59");
    }

    public void smartComponents(int i, Map<Integer, Map.Entry<String, Character>> map) {
        System.out.println("TEST60");
    }

    public void tickReqParams(int i, double v, String s, int i1) {
        System.out.println("[C] tickReqParams -> tickerId: " + i + ", minTick: " + v + ", bboExchange: " + s + ", snapshotPermission: " + i1);
    }

    public void newsProviders(NewsProvider[] newsProviders) {
        System.out.println("TEST62");
    }

    public void newsArticle(int i, int i1, String s) {
        System.out.println("TEST63");
    }

    public void historicalNews(int i, String s, String s1, String s2, String s3) {
        System.out.println("TEST64");
    }

    public void historicalNewsEnd(int i, boolean b) {
        System.out.println("TEST65");
    }

    public void headTimestamp(int i, String timestamp) {
        System.out.println(timestamp);
    }

    public void histogramData(int reqId, List<HistogramEntry> pricePoints) {
        Collections.sort(pricePoints);
        StringBuilder literal = new StringBuilder();
        literal.append("{");
        for (HistogramEntry pricePoint : pricePoints) {
            literal.append(pricePoint.price);
            literal.append(":");
            literal.append(pricePoint.size);
            literal.append(",");
        }
        literal.append("}");
        String literal_str = literal.toString();
        CallbackAction.updateHistogram(SocketComm.getInstance().getSymbol(reqId), pricePoints, literal_str);
        //utils.GatewayLogger.getInstance().log(enums.Log.CALLBACK, "[" + reqId + "]" + literal_str);
        consolePrint(reqId, "histogramData");
        //utils.SocketComm.getInstance().send(reqId,"histogram", utils.SocketComm.getInstance().getSymbol(reqId), literal_str);
    }

    public void historicalDataUpdate(int i, Bar bar) {
        System.out.println("TEST68");
    }

    public void rerouteMktDataReq(int i, int i1, String s) {
        System.out.println("TEST69");
    }

    public void rerouteMktDepthReq(int i, int i1, String s) {
        System.out.println("TEST70");
    }

    public void marketRule(int i, PriceIncrement[] priceIncrements) {
        System.out.println("TEST71");
    }

    public void pnl(int i, double v, double v1) {
        System.out.println("TEST72");
    }

    public void pnlSingle(int i, int i1, double v, double v1, double v2) {
        System.out.println("TEST73");
    }

    private void consolePrint(int reqId, String callback) {
        System.out.println("reqId: " + Integer.toString(reqId) + ", Symbol: " + SocketComm.getInstance().getSymbol(reqId) + ", Callback: " + callback);
    }

}