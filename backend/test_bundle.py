import sys, os
print("MEIPASS:", getattr(sys, '_MEIPASS', 'None'))
if hasattr(sys, '_MEIPASS'):
    for root, dirs, files in os.walk(sys._MEIPASS):
        for f in files:
            print(os.path.join(root, f).replace(sys._MEIPASS, ''))
