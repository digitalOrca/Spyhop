package utils;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Created by meng on 3/13/18.
 */
class AnalyzerTest {
    @Test
    void hindenburgOmen() {
        Analyzer.HindenburgOmen();
    }

    @Test
    void lppl() {
        Analyzer.LPPL();
    }

    @Test
    void alpha_beta_movement() {
        Analyzer.Alpha_Beta_Movement();
    }

}