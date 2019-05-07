import shutil
import tempfile

class TemporaryDirectory(object):
    """
    Context manager for tempfile.mkdtemp().
    This class is available in python +v3.2.
    """
    def __init__(self):
        self.name = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __del__(self):
        self.cleanup()
		
    def __exit__(self):
        self.cleanup()
	
    def cleanup(self):
        shutil.rmtree(self.name)
