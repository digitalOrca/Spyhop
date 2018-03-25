package utils;

/**
 * Triggers for python analysis model after market closing
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

    public static void Alpha_Beta_Movement() {
        String result = Helper.runCmd(new String[] {"python3", "/home/meng/Projects/NeuroTrader/Models/Synthesizer/Alpha_Beta_Movement.py"});
        System.out.println(result);
    }
}
