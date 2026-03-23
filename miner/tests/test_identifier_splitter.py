from app.identifier_splitter import split_identifier



def test_make_response() -> None:
    assert split_identifier("make_response") == ["make", "response"]



def test_retain_all() -> None:
    assert split_identifier("retainAll") == ["retain", "all"]



def test_get_user_name() -> None:
    assert split_identifier("GetUserName") == ["get", "user", "name"]



def test_parse_xml_file() -> None:
    assert split_identifier("parseXMLFile") == ["parse", "xml", "file"]



def test_to_json_v2() -> None:
    assert split_identifier("to_json_v2") == ["to", "json", "v2"]
