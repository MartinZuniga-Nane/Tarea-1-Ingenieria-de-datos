from app.extractors.python_extractor import PythonExtractor



def test_python_extractor_detects_function_async_and_method() -> None:
    source = '''
def simple_func():
    pass

async def async_worker():
    return 1

class UserService:
    def get_user_name(self):
        return "x"
'''
    names = PythonExtractor().extract_function_names(source)
    assert set(names) == {"simple_func", "async_worker", "get_user_name"}
