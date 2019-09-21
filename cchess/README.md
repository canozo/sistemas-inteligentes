# Chess

Chess con AI integrado.

1. Crear un venv
```
python -m venv cchess-env
```

2. Source el env
```
.\cchess-env\Scripts\activate.bat
```

3. Clonar el repo
```
git clone https://github.com/canozo/cchess.git
cd cchess
```

4. Instalar dependencies
```
pip install -r requirements.txt
```

5. Conseguir PGNs de [PGN Mentor](https://www.pgnmentor.com/files.html) y entrenar el modelo
```
python main.py GiuocoPiano.pgn London2g6.pgn QueensIndian.pgn
```
