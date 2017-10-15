import com.ib.client.Contract;
import enums.Currency;
import enums.Exchange;
import enums.Log;
import enums.SecType;
import utils.DatabaseConn;
import utils.Helper;
import utils.Logger;
import utils.SocketComm;

import java.sql.ResultSet;
import java.util.LinkedList;

/**
 * Created by meng on 9/10/17.
 */
class UpdateAction {

    private static void waitForFlag() {
        int timeout = 0;
        while(!MainGateway.recvFundRatio && timeout < MainGateway.updateTimeout) {
            Helper.pauseMilli(1);
            timeout++;
        }
    }

    static void updateAllSecurities() {
        String symbol_query = "SELECT symbol FROM security";
        String genericTicks = "258";
        ResultSet resultSet = DatabaseConn.getInstance().execQuery(symbol_query);
        LinkedList<String> allSymbols = Helper.resultToList(resultSet, "symbol");
        String prevSymbol = "";
        int reqIdUpdate = MainGateway.reqIdUpdateBase;
        for (String symbol : allSymbols) {
            MainGateway.client.getClientSocket().cancelMktData(reqIdUpdate); // error on first element: OK
            Logger.getInstance().log(Log.ACTION, "[Cancel] " + prevSymbol + "\n");
            // increment reqId for new Id-symbol pair
            SocketComm.getInstance().registerSymbol(++reqIdUpdate, symbol);
            Contract contract = OrderBuilder.makeContract(symbol, SecType.STK, Exchange.SMART, Currency.USD);
            MainGateway.recvFundRatio = false;
            MainGateway.client.getClientSocket().reqMktData(reqIdUpdate, contract, genericTicks, false, false, null);
            prevSymbol = symbol;
            waitForFlag();
            Logger.getInstance().log(Log.ACTION, "[Request] " + symbol);
        }

        MainGateway.client.getClientSocket().cancelMktData(reqIdUpdate);
        Logger.getInstance().log(Log.ACTION, "[Cancel] " + prevSymbol + "\n");
    }

    static void updateIndices() {
        Helper.runCmd(new String[] {"python", "/home/meng/Projects/NeuroTrader/TradeGateway/src/main/resources/python/updateIndex.py"}, false);
    }
}
