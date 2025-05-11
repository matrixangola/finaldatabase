import tkinter as tk
from tkinter import messagebox, ttk, font, colorchooser, filedialog
import sqlite3
import time
import os

DB_FILE = "usuarios.db"
TEXT_DIR = "textos_salvos"

if not os.path.exists(TEXT_DIR):
    os.makedirs(TEXT_DIR)

def inicializar_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nascimento TEXT NOT NULL,
            contacto TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def botao_arredondado(master, texto, comando):
    canvas = tk.Canvas(master, width=260, height=40, bg=master["bg"], highlightthickness=0)
    canvas.pack(pady=6)
    raio = 20
    canvas.create_arc((0, 0, raio*2, raio*2), start=90, extent=180, fill="#E0E0E0", outline="#E0E0E0")
    canvas.create_arc((260 - raio*2, 0, 260, raio*2), start=270, extent=180, fill="#E0E0E0", outline="#E0E0E0")
    canvas.create_rectangle((raio, 0, 260 - raio, 40), fill="#E0E0E0", outline="#E0E0E0")
    canvas.create_text(130, 20, text=texto, font=("Arial", 10, "bold"))
    canvas.bind("<Button-1>", lambda e: comando())

def fazer_cadastro():
    def confirmar():
        nome = nome_entry.get().strip()
        nascimento = nascimento_entry.get().strip()
        contacto = contacto_entry.get().strip()
        email = email_entry.get().strip()
        if not nome or not nascimento or not contacto or not email:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, nascimento, contacto, email) VALUES (?, ?, ?, ?)",
                       (nome, nascimento, contacto, email))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso.")
        cadastro_window.destroy()

    cadastro_window = tk.Toplevel(root)
    cadastro_window.title("Cadastro de Usuário")
    cadastro_window.geometry("500x400")
    cadastro_window.config(bg="#C0C0C0")

    campos = ["Nome", "Data de Nascimento (dd/mm/aaaa)", "Contacto", "Email"]
    entradas = []
    for campo in campos:
        tk.Label(cadastro_window, text=campo, bg="#C0C0C0").pack(pady=2)
        entrada = tk.Entry(cadastro_window)
        entrada.pack()
        entradas.append(entrada)

    nome_entry, nascimento_entry, contacto_entry, email_entry = entradas
    botao_arredondado(cadastro_window, "Cadastrar", confirmar)

def ver_usuarios():
    ver_window = tk.Toplevel(root)
    ver_window.title("Lista de Usuários")
    ver_window.geometry("700x300")
    ver_window.config(bg="#C0C0C0")

    tree = ttk.Treeview(ver_window, columns=("Nome", "Nascimento", "Contacto", "Email"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, nascimento, contacto, email FROM usuarios")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()
    tree.pack(padx=10, pady=10, fill="both", expand=True)

def remover_usuario():
    def confirmar():
        nome = nome_entry.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Digite um nome para remover.")
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE nome = ?", (nome,))
        if cursor.rowcount > 0:
            conn.commit()
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' removido.")
        else:
            messagebox.showinfo("Info", f"Usuário '{nome}' não encontrado.")
        conn.close()
        remover_window.destroy()

    remover_window = tk.Toplevel(root)
    remover_window.title("Remover Usuário")
    remover_window.geometry("300x150")
    remover_window.config(bg="#C0C0C0")

    tk.Label(remover_window, text="Nome do Usuário:", bg="#C0C0C0").pack(pady=10)
    nome_entry = tk.Entry(remover_window)
    nome_entry.pack(pady=5)
    botao_arredondado(remover_window, "Remover", confirmar)

def atualizar_horas():
    hora_atual = time.strftime("%H:%M:%S")
    hora_label.config(text=hora_atual)
    root.after(1000, atualizar_horas)

def abrir_editor_texto():
    editor = tk.Toplevel(root)
    editor.title("Editor de Texto")
    editor.geometry("900x600")
    editor.config(bg="#F0F0F0")

    fonte_atual = tk.StringVar(value="Comic Sans MS")
    tamanho_atual = tk.IntVar(value=12)
    cor_atual = "#000000"

    def aplicar_estilos():
        text_area.config(font=(fonte_atual.get(), tamanho_atual.get()), fg=cor_atual)

    def escolher_cor():
        nonlocal cor_atual
        cor_atual = colorchooser.askcolor(title="Escolha a cor da fonte")[1]
        aplicar_estilos()

    def salvar_texto():
        texto = text_area.get("1.0", tk.END).strip()
        if texto:
            filename = filedialog.asksaveasfilename(defaultextension=".txt", initialdir=TEXT_DIR,
                                                    filetypes=[("Text files", "*.txt")])
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(texto)
                messagebox.showinfo("Salvo", f"Texto salvo em:\n{filename}")
        else:
            messagebox.showwarning("Aviso", "Área de texto vazia!")

    control_frame = tk.Frame(editor, bg="#F0F0F0")
    control_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(control_frame, text="Fonte:", bg="#F0F0F0").pack(side="left")
    ttk.Combobox(control_frame, textvariable=fonte_atual, values=font.families(), width=20).pack(side="left", padx=5)

    tk.Label(control_frame, text="Tamanho:", bg="#F0F0F0").pack(side="left")
    tk.Spinbox(control_frame, from_=8, to=72, textvariable=tamanho_atual, width=5).pack(side="left", padx=5)

    tk.Button(control_frame, text="Cor da Fonte", command=escolher_cor).pack(side="left", padx=5)
    tk.Button(control_frame, text="Aplicar", command=aplicar_estilos).pack(side="left", padx=5)
    tk.Button(control_frame, text="Salvar", command=salvar_texto).pack(side="left", padx=5)

    text_area = tk.Text(editor, wrap="word")
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    aplicar_estilos()

def gerenciar_textos_salvos():
    def deletar_arquivo():
        item = lista.curselection()
        if item:
            arquivo = lista.get(item[0])
            caminho = os.path.join(TEXT_DIR, arquivo)
            if messagebox.askyesno("Confirmação", f"Deseja excluir '{arquivo}'?"):
                os.remove(caminho)
                lista.delete(item)

    janela = tk.Toplevel(root)
    janela.title("Arquivos de Texto Salvos")
    janela.geometry("500x300")
    janela.config(bg="#E0E0E0")

    lista = tk.Listbox(janela, width=80)
    lista.pack(padx=10, pady=10, fill="both", expand=True)

    for f in os.listdir(TEXT_DIR):
        if f.endswith(".txt"):
            lista.insert(tk.END, f)

    botao_arredondado(janela, "Excluir Selecionado", deletar_arquivo)

def iniciar_app():
    global root, hora_label
    root = tk.Tk()
    root.title("Base de Dados de Usuários")
    root.geometry("400x500")
    root.config(bg="#C0C0C0")

    titulo_frame = tk.Frame(root, bg="#E0E0E0", bd=2, relief="solid", padx=10, pady=5)
    titulo_frame.pack(pady=(10, 5))
    tk.Label(titulo_frame, text="AYPO\nDataBase", font=("Arial", 16, "bold"), bg="#E0E0E0", justify="center").pack()

    hora_label = tk.Label(root, text="", font=("Arial", 12), bg="#C0C0C0")
    hora_label.pack(pady=5)
    atualizar_horas()

    botoes_frame = tk.Frame(root, bg="#C0C0C0")
    botoes_frame.pack(expand=True)

    botoes = [
        ("Cadastrar Usuário", fazer_cadastro),
        ("Ver Lista de Usuários", ver_usuarios),
        ("Remover Usuário", remover_usuario),
        ("Editor de Texto", abrir_editor_texto),
        ("Ver Textos Salvos", gerenciar_textos_salvos),
        ("Sair", root.destroy)
    ]

    for texto, comando in botoes:
        botao_arredondado(botoes_frame, texto, comando)

def mostrar_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.attributes("-alpha", 0.0)  # Transparente no início

    width, height = 400, 250
    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    pos_x = (screen_w - width) // 2
    pos_y = (screen_h - height) // 2
    splash.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    splash.config(bg="#FFFFFF")

    frame = tk.Frame(splash, bg="#FFFFFF")
    frame.pack(expand=True)

    box = tk.Frame(frame, bg="#000000", padx=10, pady=5)
    box.pack(pady=20)
    tk.Label(box, text="Hamir Studios", font=("Comic Sans MS", 18, "bold"),
             bg="#000000", fg="#FFFFFF", justify="center").pack()
    tk.Label(frame, text="+244929480891", font=("Comic Sans MS", 12),
             bg="#FFFFFF", fg="#000000", justify="center").pack(pady=10)

    def fade_in(alpha=0.0):
        alpha += 0.05
        if alpha <= 1.0:
            splash.attributes("-alpha", alpha)
            splash.after(100, lambda: fade_in(alpha))
        else:
            splash.after(4000, lambda: (splash.destroy(), iniciar_app()))

    fade_in()
    splash.mainloop()

inicializar_db()
mostrar_splash()