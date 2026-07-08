import runpy
import sys
import os
os.chdir(r'D:\OneDrive\桌面\bigdata\output')
sys.path.insert(0, r'D:\OneDrive\桌面\bigdata\output')
# Capture all output
import io
old_stdout = sys.stdout
sys.stdout = captured = io.StringIO()

try:
    exec(open(r"D:\OneDrive\桌面\bigdata\analyze_data.py", encoding='utf-8').read())
except Exception as e:
    import traceback
    traceback.print_exc()

sys.stdout = old_stdout
output = captured.getvalue()

with open(r'D:\OneDrive\桌面\bigdata\output\captured_output.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(f"Output written to captured_output.txt ({len(output)} chars)")
