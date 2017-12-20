import com.ib.client.Contract;
import enums.Currency;
import enums.Exchange;
import enums.Log;
import enums.SecType;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import utils.DatabaseConn;
import utils.Helper;
import utils.Logger;
import utils.SocketComm;
import java.io.IOException;
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
        try {
            Document doc = Jsoup.connect("https://finance.google.com/finance?q=INDEXSP:.INX").get();
            double indices = Double.parseDouble(doc.getElementsByAttributeValue("id", "ref_626307_l").text().replace(",", ""));
            String update = "INSERT INTO benchmark (date, snp500) VALUES ('%s',%s)";
            String query = String.format(update, Helper.today(), indices);
            DatabaseConn.getInstance().execUpdate(query);
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}
