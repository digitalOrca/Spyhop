package utils;

/**
 * Created by meng on 3/13/18.
 */
public class Analyzer {

    public Analyzer() {

    }

    public static void HindenburgOmen() {
        String result = Helper.runCmd(new String[] {"python", "/home/meng/Projects/NeuroTrader/Models/HindenburgOmen/HindenburgOmen.py"});
        System.out.println(result);
    }

    public static void LPPL() {
        Helper.runCmd(new String[] {"python", "/home/meng/Projects/NeuroTrader/Models/LPPL/LPPL.py", "direct"}, false);
    }
}
