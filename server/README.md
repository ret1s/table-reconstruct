# Flask Backend

1. Create conda env.
2. Install dependencies
   
```bash
conda install pytorch torchvision torchaudio cpuonly -c pytorch
conda install -c conda-forge pillow opencv tesseract pytesseract psutil beautifulsoup4 numpy scipy tqdm matplotlib pandas seaborn gitpython gtk3 filelock
pip install "PyMuPDF>=1.16.0,!=1.18.11,!=1.18.12,!=1.19.5"
pip install "tf2onnx==1.13.0" "thop>=0.1.1"
pip install -e git+https://github.com/mindee/doctr.git#egg=python-doctr[tf]
```

3. Run `python server.py`
