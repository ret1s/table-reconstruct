# Flask Backend

1. Create conda environment.

```bash
conda create -n myenv python=3.9 pip
conda activate myenv
```

2. Install libraries.

If GPU available (CUDA >= 11.7):

```bash
conda install -c "nvidia/label/cuda-11.7.1" cuda-toolkit
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
pip install paddlepaddle-gpu==2.4.2.post117 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html
pip install -r requirements.txt
pip install "paddleocr>=2.0.1"
```

Using CPU:

```bash
pip install torch torchvision torchaudio
pip install paddlepaddle==2.4.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
pip install "paddleocr>=2.0.1"
```

3. Run `python server.py`.
