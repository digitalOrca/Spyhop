import com.ib.client.EReader;

/**
 * Created by meng on 5/14/17.
 */
public class QueueProcessor extends Thread{

    private EWrapperImpl client;
    private EReader reader;

    public QueueProcessor(EWrapperImpl client, EReader reader){
        this.client = client;
        this.reader = reader;
    }

    @Override
    public void run(){
        while(client.getClientSocket().isConnected()){
            client.getReadSignal().waitForSignal();
            try{
                reader.processMsgs();
            }catch (Exception e){
                System.out.println("Exception: " + e.getMessage());
            }

        }
    }
}
