from app.extractors.java_extractor import JavaExtractor



def test_java_extractor_detects_methods() -> None:
    source = '''
public class Demo {
    public void retainAll() {}
    private int parseXMLFile() { return 1; }
}
'''
    names = JavaExtractor().extract_method_names(source)
    assert set(names) == {"retainAll", "parseXMLFile"}
