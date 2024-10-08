import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import os
import re
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract
import hashlib

def extrair_data_com_pdfplumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                match = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
                if match:
                    return match.group(1)
    return None

def extrair_data_com_ocr(pdf_path):
    imagens = convert_from_path(pdf_path)
    for imagem in imagens:
        texto = pytesseract.image_to_string(imagem)
        match = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
        if match:
            return match.group(1)
    return None

def extrair_data_pagamento(pdf_path):
    data = extrair_data_com_pdfplumber(pdf_path)
    if data:
        return data

    return extrair_data_com_ocr(pdf_path)

def calcular_hash_arquivo(caminho_pdf):
    hasher = hashlib.md5()
    with open(caminho_pdf, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def arquivos_sao_iguais(arquivo1, arquivo2):
    return calcular_hash_arquivo(arquivo1) == calcular_hash_arquivo(arquivo2)

def renomear_arquivos_por_data(diretorio):
    arquivos_processados = {} 

    for arquivo in os.listdir(diretorio):
        if arquivo.lower().endswith('.pdf'):
            caminho_pdf = os.path.join(diretorio, arquivo)
            data_pagamento = extrair_data_pagamento(caminho_pdf)

            if data_pagamento:
                data_formatada = datetime.strptime(data_pagamento, '%d/%m/%Y').strftime('%Y-%m-%d')
                novo_nome = f'{data_formatada}.pdf'
                caminho_novo_arquivo = os.path.join(diretorio, novo_nome)

                if data_formatada in arquivos_processados:
                    arquivo_existente = arquivos_processados[data_formatada]
                    if arquivos_sao_iguais(caminho_pdf, arquivo_existente):
                        os.remove(caminho_pdf)
                        print(f'Arquivo duplicado removido: {arquivo}')
                    else:
                        print(f'Erro: o arquivo {novo_nome} já existe com conteúdo diferente.')
                else:
                    try:
                        os.rename(caminho_pdf, caminho_novo_arquivo)
                        arquivos_processados[data_formatada] = caminho_novo_arquivo
                        print(f'Arquivo renomeado: {arquivo} -> {novo_nome}')
                    except FileExistsError:
                        print(f'Erro: o arquivo {novo_nome} já existe.')
                    except Exception as e:
                        print(f'Erro ao renomear {arquivo}: {e}')
            else:
                print(f'Data não encontrada no arquivo: {arquivo}')

    messagebox.showinfo("Sucesso", "Holerites renomeados com sucesso! ✔")

def selecionar_pasta():
    diretorio = filedialog.askdirectory()
    if diretorio:
        renomear_arquivos_por_data(diretorio)

app = tk.Tk()
app.title("Renomear Holerites")

frame = tk.Frame(app, padx=20, pady=20)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="Renomeador de Holerites", font=("Arial", 14))
label.pack(pady=10)

botao = tk.Button(frame, text="Selecionar Pasta", command=selecionar_pasta, width=20, height=2)
botao.pack(pady=10)

app.geometry("400x200")
app.mainloop()
