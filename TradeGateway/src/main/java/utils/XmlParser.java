package utils;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.IOException;
import java.io.StringReader;

/**
 * XML parsing utility, not currently used
 */
public class XmlParser {

    private static DocumentBuilderFactory documentBuilderFactory = DocumentBuilderFactory.newInstance();
    private static DocumentBuilder documentBuilder = null;

    public XmlParser() {}

    public static String getText(String xml, String structure) {
        try {
            documentBuilder = documentBuilderFactory.newDocumentBuilder();
            InputSource inputSource = new InputSource(new StringReader(xml));
            Document document = documentBuilder.parse(inputSource);
            Node currNode = document.getDocumentElement();
            for (String pair : structure.split(";")) {
                String tag = pair.split(":")[0];
                int index = Integer.parseInt(pair.split(":")[1]);
                currNode = ((Element)currNode).getElementsByTagName(tag).item(index);
            }
            return currNode.getTextContent();
        } catch (ParserConfigurationException | SAXException | IOException e) {
            e.printStackTrace();
        }
        return "";
    }
}
