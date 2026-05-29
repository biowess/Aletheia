import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unittest.mock import MagicMock
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['app.core.database'] = MagicMock()

try:
    import app.export.pdf_service as pdf
    print("LOGO_PATH:", pdf.LOGO_PATH)
    print("FONT_DIR:", pdf.FONT_DIR)
    print("Logo exists:", os.path.exists(pdf.LOGO_PATH))
    print("_r exists:", pdf._font_path("texgyretermes-regular"))
    print("frozen:", getattr(sys, 'frozen', False))
    print("MEIPASS:", getattr(sys, '_MEIPASS', 'None'))
except Exception as e:
    import traceback
    traceback.print_exc()
