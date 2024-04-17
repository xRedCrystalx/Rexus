import sys, traceback
sys.dont_write_bytecode = True

class ErrorHelper:
    def full_traceback(self) -> str:
        return traceback.format_exc()
    
    def simple_error(self, error: Exception) -> str:
        return f"{type(error).__name__}: {error}"