
from kanbatryoshka.app import KanbatryoshkaApp
import sys

if __name__ == "__main__":
    app = KanbatryoshkaApp()
    exit_code = app.run()
    sys.exit(exit_code)