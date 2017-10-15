import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * Created by meng on 6/7/17.
 */
public class StrategyExecutor implements Runnable {

    private static StrategyExecutor ourInstance = new StrategyExecutor();

    public static StrategyExecutor getInstance() {
        return ourInstance;
    }

    private int port;
    private ServerSocket serverSocket;
    private Socket clientSocket;
    private BufferedReader bufferedReader;
    private InputStreamReader inputStreamReader;

    private StrategyExecutor() {
        this.port = 8899;
    }

    public void end() {
        try {
            bufferedReader.close();
            clientSocket.close();
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private void restart() {
        end();
        System.out.println("StrategyCore connection interrupted...");
        run();
    }

    @Override
    public void run() {
        try {
            serverSocket = new ServerSocket(port);
            clientSocket = serverSocket.accept();
            System.out.println("StrategyCore started...");
            this.inputStreamReader = new InputStreamReader(this.clientSocket.getInputStream());
            bufferedReader = new BufferedReader(this.inputStreamReader);
        } catch (IOException e){
            e.printStackTrace();
        }
        String line;
        try {
            while ((line = bufferedReader.readLine()) != null) {
                System.out.println(line);
                //TODO: DO SOMETHING ABOUT THE STRATEGY RECEIVED


            }
            restart();
        } catch (IOException e) {
            e.printStackTrace();
            restart();
        }
    }
}
