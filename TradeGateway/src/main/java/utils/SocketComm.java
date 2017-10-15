package utils;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.nio.charset.Charset;
import java.util.HashMap;
/**
 * Created by meng on 5/31/17.
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
    private HashMap<Integer, String> map = new HashMap<>();

    private SocketComm() {
        port = 8888;
    }

    public void registerSymbol(int reqId, String symbol) {
        this.map.put(reqId, symbol);
    }

    public void unregisterSymbol(int reqId) {
        this.map.remove(reqId);
    }

    public String getSymbol(int reqId) {
        if (this.map.containsKey(reqId)) {
            return this.map.get(reqId);
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
