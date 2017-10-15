package enums;

/**
 * Created by meng on 10/1/17.
 */
public enum OrderType {
    LMT("LMT"),
    MTL("MTL"),
    MKT_PRT("MKT PRT"),
    QUOTE("QUOTE"),
    STP("STP"),
    STP_LMT("STP LMT"),
    TRAIL_LIT("TRAIL LIT"),
    TRAIL_MIT("TRAIL MIT"),
    TRAIL("TRAIL"),
    TRAIL_LIMIT("TRAIL LIMIT"),
    MKT("MKT"),
    MIT("MIT"),
    MOC("MOC"),
    MOO("MOO"),
    PEG_MKT("PEG MKT"),
    REL("REL"),
    BOX_TOP("BOX TOP"),
    LOC("LOC"),
    LOO("LOO"),
    LIT("LIT"),
    PEG_MID("PEG MID"),
    VWAP("VWAP"),
    GAT("GAT"),
    GTD("GTD"),
    GTC("GTC"),
    IOC("IOC"),
    OCA("OCA"),
    VOL("VOL");

    private String orderType;

    OrderType(String orderType) {
        this.orderType = orderType;
    }
}