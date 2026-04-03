@echo off
:: Always use the project venv — avoids onnxruntime / wrong-Python errors
"D:\LLM_OPS\venv\python.exe" -m streamlit run app.py %*
