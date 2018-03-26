package utils;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.nio.charset.Charset;
import java.util.HashMap;
/**
 * Socket communication utility class, not currently used
 */
public class SocketComm {
    private static SocketComm ourInstance = new SocketComm();

    public static SocketComm getInstance() {
        return ourInstance;
    }

    private int port;
    private ServerSocket serverSocket;
    private java.net.Socket clientSocket;
    private DataOutputStream dataOutputStream;
    private HashMap<Integer, String> reqMap = new HashMap<>();
    private HashMap<Integer, String> orderMap = new HashMap<>();

    private SocketComm() {
        port = 8888;
    }

    public void registerRequest(int reqId, String symbol) {
        this.reqMap.put(reqId, symbol);
    }

    public void unregisterRequest(int reqId) {
        this.reqMap.remove(reqId);
    }

    public void registerOrder(int orderId, String symbol) {
        this.orderMap.put(orderId, symbol);
    }

    public String getSymbol(int reqId) {
        if (this.reqMap.containsKey(reqId)) {
            return this.reqMap.get(reqId);
        }
        return "INVALID";
    }

    public String getOrder(int orderId) {
        if (this.orderMap.containsKey(orderId)) {
            return this.orderMap.get(orderId);
        }
        return "INVALID";
    }

    public void start() {
        try {
            serverSocket = new ServerSocket(this.port);
            System.out.println("utils.SocketComm waiting for connection from preprocessor...");
            clientSocket = serverSocket.accept();
            System.out.println("Preprocessor started...");
            dataOutputStream = new DataOutputStream(clientSocket.getOutputStream());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    public void end() {
        try {
            clientSocket.close();
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void restart() {
        end();
        System.out.println("Preprocessor connection interrupted...");
        start();
    }

    public void send(int reqId, String proc, String symbol, String msg) {
        try {
            String data = "@" + Integer.toString(reqId) + "|" + proc + "|" + symbol + "|" + msg + "&";
            byte[] encoded_data = data.getBytes(Charset.forName("UTF-8"));
            dataOutputStream.write(encoded_data);
            dataOutputStream.flush();
        } catch (IOException e) {
            restart();
        }
    }
}
