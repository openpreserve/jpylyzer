/**
 *   Class to test the integration of jpylyzer with java
 *   needs jython to work
 *   
 * Usage sample :
 *  javac CallJpylyzer.java
 *  CLASSPATH="jython-standalone-2.7.0.jar;." java CallJpylyzer . example_files/balloon.jp2

 */

import java.io.File;
import java.util.logging.Logger;

import javax.script.Invocable;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineFactory;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;

public class CallJpylyzer {

private static String jpylyzerHome = null;
private static final Logger LOGGER = Logger.getLogger(CallJpylyzer.class.getName());

private static void declarePythonFunctionInEngine(ScriptEngine engine) throws Exception {
    if (engine == null) {
        throw new Exception("Script Engine 'python' not found!");
    }

    final String pythonCharacterizeFunction = 
        "from jpylyzer.jpylyzer import checkOneFile\n"
        + "import xml.etree.ElementTree as ETree\n"
        + "\ndef pythonCharacterize(file):\n" 
        + "\txmlElement = checkOneFile(file)\n"
        + "\treturn ETree.tostring(xmlElement, encoding='utf8', method='xml')\n"
        + "\n";
    try {
        engine.eval(pythonCharacterizeFunction);
    } catch (ScriptException e) {
        throw new Exception("Definition of pythonCharacterize function could not be interpreted!", e);
    }
}

public static void main (String[] args) throws Exception{
    String jpylyzerPath = args[0];
    File jpylyzerDir = new File(jpylyzerPath);
    if (jpylyzerDir.exists() && jpylyzerDir.isDirectory()) {
        jpylyzerHome = jpylyzerPath;
    } else {
        LOGGER.severe("Invalid configuration jpylyzer: [" + jpylyzerPath + "] notFound");
        throw new IllegalArgumentException("Invalid configuration jpylyzer: [" + jpylyzerPath + "] notFound");
    }

    // Define the python.path property to make jpylyzer discoverable
    String path = System.getProperty("python.path");
    if (path == null || path.length() == 0) {
        System.setProperty("python.path", jpylyzerHome);
    } else {
        System.setProperty("python.path", jpylyzerHome + File.pathSeparator + path);
    }

    // First time initialization
    ScriptEngine engine = new ScriptEngineManager().getEngineByName("python");
    
    File inputFile = new File(args[1]);
    String filePath = inputFile.getAbsolutePath().replaceAll("\\\\", "/");

    declarePythonFunctionInEngine(engine);

    if (engine instanceof Invocable) {
        Invocable invocable = (Invocable) engine;
        Object docXml = invocable.invokeFunction("pythonCharacterize", filePath);
        System.out.println((String)docXml);
    } else {
        Object docXml = engine.eval("pythonCharacterize('" + filePath + "')");
        System.out.println((String)docXml);
    }

}

}