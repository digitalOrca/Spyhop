package utils;
import java.sql.*;

/**
 * databse utility singleton class
 */
public class DatabaseConn {
    private static DatabaseConn ourInstance = new DatabaseConn();

    public static DatabaseConn getInstance() {
        return ourInstance;
    }

    private Connection connection = null;
    private boolean simulated = false;


    private DatabaseConn() {
        this.connect("localhost", "interactive_brokers",
                "neurotrader", "profit");
    }

    public void disableWrite() {
        this.simulated = true;
    }

    private void connect(String host, String database, String username, String password) {
        // while loading, the driver will automatically register itself with JDBC
        try {
            Class.forName("org.postgresql.Driver");
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
        try {
            this.connection = DriverManager.getConnection("jdbc:postgresql://"+host+"/"+database, username, password);
        } catch (SQLException e) {
            e.printStackTrace();
            System.out.println(e.getMessage());
        }
    }

    /*update databse content*/
    public void execUpdate(String query) {
        System.out.println("[U] " + query);
        if (simulated) return; // if doing simulated trading
        try {
            Statement statement = this.connection.createStatement();
            statement.executeUpdate(query);
            statement.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    /*update database content and return*/
    public ResultSet execSync(String query) {  // an update statement with return
        System.out.println("[S] " + query);
        if (simulated) return null; // if doing simulated trading
        try {
            Statement statement = this.connection.createStatement();
            return statement.executeQuery(query);
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return null;
    }

    /*query to database*/
    public ResultSet execQuery(String query) {
        System.out.println("[Q] " + query);
        try {
            Statement statement = this.connection.createStatement();
            return statement.executeQuery(query);
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return null;
    }
}
