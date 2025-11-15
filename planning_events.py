import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "Planning Events - Gestão de Eventos"

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_FILE = SCRIPT_DIR / "events.json"

eventos = {}
ID_CONTADOR = 1
DEFAULT_THEME = "vista"

# --- Configurações de Acesso ---
USER_ROLE = 'guest'
# Usuários autorizados com permissão de 'admin'
AUTHORIZED_USERS = ["Davi Oliveira", "John Lennon"]
AUTHORIZED_PASS = "admin"
# AVISO: Não altere AUTHORIZED_USERS/PASS ou USER_ROLE aqui. 
# A alteração no role deve ser feita apenas no processo de login.

def load_events():
    """Carrega os dados dos eventos do arquivo JSON."""
    global eventos, ID_CONTADOR
    if not DATA_FILE.exists():
        eventos = {}
        ID_CONTADOR = 1
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        # Garante que as chaves do dicionário de eventos são inteiros
        eventos = {int(k): v for k, v in payload.get("eventos", {}).items()}
        next_id = payload.get("next_id")
        if next_id is None:
            # Se 'next_id' não existir, calcula o próximo ID
            ID_CONTADOR = (max(eventos.keys()) + 1) if eventos else 1
        else:
            ID_CONTADOR = int(next_id)
    except Exception as e:
        messagebox.showwarning(APP_NAME, f"Falha ao carregar dados: {e}")
        eventos = {}
        ID_CONTADOR = 1

def save_events():
    """Salva os dados dos eventos no arquivo JSON."""
    try:
        # Garante que as chaves no JSON são strings
        payload = {"eventos": {str(k): v for k, v in eventos.items()}, "next_id": ID_CONTADOR}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        root = tk._get_default_root()
        if root:
            messagebox.showerror(APP_NAME, f"Falha ao salvar dados: {e}", parent=root)
        else:
            messagebox.showerror(APP_NAME, f"Falha ao salvar dados: {e}")

def apply_style(root, style):
    """Aplica o tema e o estilo padrão do ttk."""
    try:
        style.theme_use(DEFAULT_THEME)
        # Configurações básicas de estilo para o tema
        root.configure(bg=None)
        style.configure("TLabel", background=None, foreground=None)
        style.configure("TFrame", background=None)
        style.configure("TButton", background=None, foreground=None)
        style.configure("TEntry", fieldbackground=None, foreground=None)
        # Estilos para a Treeview (tabela)
        style.configure("Treeview", background=None, fieldbackground=None, foreground=None)
        style.configure("Treeview.Heading", background=None, foreground=None)
        style.map("Treeview", background=[("selected", style.lookup("TFrame", "background"))])
    except Exception:
        # Ignora erros de estilo se o tema padrão não for encontrado
        pass

def atualizar_treeview(tree):
    """Atualiza a Treeview com a lista atual de eventos."""
    tree.delete(*tree.get_children())
    for id_evento, dados in sorted(eventos.items()):
        tree.insert("", "end", iid=str(id_evento), text=str(id_evento), values=(
            dados.get("nome", ""),
            dados.get("data", ""),
            dados.get("local", ""),
            dados.get("telefone", ""),
            len(dados.get("inscricoes", []))
        ))

def abrir_adicionar_evento(parent, tree, style):
    """Abre janela para adicionar um novo evento (apenas Admin)."""
    win = tk.Toplevel(parent)
    win.title("Adicionar Evento")
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)
    win.lift()

    frm = ttk.Frame(win, padding=12)
    frm.grid()

    nome_var = tk.StringVar()
    data_var = tk.StringVar()
    local_var = tk.StringVar()
    tel_var = tk.StringVar()

    ttk.Label(frm, text="Nome do Evento:").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=nome_var, width=40).grid(row=0, column=1, pady=2)
    ttk.Label(frm, text="Data (DD/MM/AAAA):").grid(row=1, column=0, sticky="w")
    ttk.Entry(frm, textvariable=data_var, width=40).grid(row=1, column=1, pady=2)
    ttk.Label(frm, text="Local do Evento:").grid(row=2, column=0, sticky="w")
    ttk.Entry(frm, textvariable=local_var, width=40).grid(row=2, column=1, pady=2)
    ttk.Label(frm, text="Telefone para Contato:").grid(row=3, column=0, sticky="w")
    ttk.Entry(frm, textvariable=tel_var, width=40).grid(row=3, column=1, pady=2)

    def salvar():
        global ID_CONTADOR

        nonlocal nome_var, data_var, local_var, tel_var
        nome = nome_var.get().strip()
        data = data_var.get().strip()
        local = local_var.get().strip()
        tel = tel_var.get().strip()
        if not nome or not data or not local:
            messagebox.showerror("Erro", "Nome, Data e Local são obrigatórios.", parent=win)
            return
        
        # Cria novo evento com lista de inscrições vazia
        novo = {"nome": nome, "data": data, "local": local, "telefone": tel, "inscricoes": []}
        eventos[ID_CONTADOR] = novo
        ID_CONTADOR += 1
        save_events()
        atualizar_treeview(tree)
        messagebox.showinfo("Sucesso", f"Evento '{nome}' criado.", parent=win)
        win.destroy()

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=4, column=0, columnspan=2, pady=(8,0))
    ttk.Button(btn_frame, text="Salvar", command=salvar).grid(row=0, column=0, padx=6)
    ttk.Button(btn_frame, text="Cancelar", command=win.destroy).grid(row=0, column=1, padx=6)

def abrir_inscrever_participante(parent, tree):
    """Abre janela para inscrever um participante em um evento (apenas Admin)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(APP_NAME, "Selecione um evento.", parent=parent)
        return
    id_evento = int(selected[0])
    dados = eventos.get(id_evento)
    if dados is None:
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=parent)
        return

    win = tk.Toplevel(parent)
    win.title(f"Inscrever em: {dados.get('nome')}")
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)
    win.lift()

    frm = ttk.Frame(win, padding=12)
    frm.grid()
    nome_var = tk.StringVar()
    email_var = tk.StringVar()
    
    ttk.Label(frm, text="Nome Completo:").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=nome_var, width=40).grid(row=0, column=1, pady=2)
    ttk.Label(frm, text="Email:").grid(row=1, column=0, sticky="w")
    ttk.Entry(frm, textvariable=email_var, width=40).grid(row=1, column=1, pady=2)

    def salvar():
        nome = nome_var.get().strip()
        email = email_var.get().strip()
        if not nome or not email:
            messagebox.showerror("Erro", "Nome e Email são obrigatórios.", parent=win)
            return
        
        participante = {"nome": nome, "email": email}
        dados.setdefault("inscricoes", []).append(participante)
        save_events()
        atualizar_treeview(tree)
        messagebox.showinfo("Sucesso", f"{nome} inscrito(a).", parent=win)
        win.destroy()

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=(8,0))
    ttk.Button(btn_frame, text="Inscrever", command=salvar).grid(row=0, column=0, padx=6)
    ttk.Button(btn_frame, text="Cancelar", command=win.destroy).grid(row=0, column=1, padx=6)

def abrir_consultar_inscritos(parent, tree):
    """Abre janela para consultar inscritos de um evento (todos os usuários) em formato Treeview."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(APP_NAME, "Selecione um evento.", parent=parent)
        return
    id_evento = int(selected[0])
    dados = eventos.get(id_evento)
    if dados is None:
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=parent)
        return
        
    inscritos = dados.get("inscricoes", [])
    
    win = tk.Toplevel(parent)
    win.title(f"Inscritos em: {dados.get('nome')} (ID {id_evento})")
    win.transient(parent)
    win.grab_set()
    win.lift()

    # Frame principal usando .pack() (IMPORTANTE: Não misturar pack e grid)
    main_frm = ttk.Frame(win, padding=10)
    main_frm.pack(fill="both", expand=True)

    ttk.Label(main_frm, text=f"Evento: {dados.get('nome')}", font=(None, 12, "bold")).pack(pady=5)
    ttk.Label(main_frm, text=f"Total de inscritos: {len(inscritos)}").pack(pady=(0, 10))

    # Frame para Treeview e Scrollbar
    tree_sb_frame = ttk.Frame(main_frm)
    tree_sb_frame.pack(fill="both", expand=True, padx=5, pady=5)
    tree_sb_frame.columnconfigure(0, weight=1)
    tree_sb_frame.rowconfigure(0, weight=1)

    # Cria Treeview para exibir inscritos em formato de tabela
    cols = ("Nome", "Email")
    inscritos_tree = ttk.Treeview(tree_sb_frame, columns=cols, show="headings", selectmode="none")
    inscritos_tree.heading("Nome", text="Nome")
    inscritos_tree.heading("Email", text="Email")
    inscritos_tree.column("Nome", width=250, anchor="w")
    inscritos_tree.column("Email", width=250, anchor="w")

    for p in inscritos:
        # Aqui, os dados 'nome' e 'email' do participante são inseridos
        inscritos_tree.insert("", "end", values=(p.get("nome", "—"), p.get("email", "—")))

    vsb = ttk.Scrollbar(tree_sb_frame, orient="vertical", command=inscritos_tree.yview)
    inscritos_tree.configure(yscrollcommand=vsb.set)

    # Layout usando grid dentro de tree_sb_frame (para Treeview e Scrollbar)
    inscritos_tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    
    ttk.Button(main_frm, text="Fechar", command=win.destroy).pack(pady=10)

def abrir_remover_participante(parent, tree):
    """Abre janela para remover um participante de um evento (apenas Admin)."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(APP_NAME, "Selecione um evento.", parent=parent)
        return
    id_evento = int(selected[0])
    dados = eventos.get(id_evento)
    if dados is None:
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=parent)
        return

    inscritos = dados.get("inscricoes", [])
    if not inscritos:
        messagebox.showinfo("Sem inscritos", "Este evento não possui inscritos.", parent=parent)
        return

    win = tk.Toplevel(parent)
    win.title(f"Remover Inscrito - {dados.get('nome')}")
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)
    win.lift()

    frm = ttk.Frame(win, padding=12)
    frm.grid(row=0, column=0)

    ttk.Label(frm, text=f"Selecione o inscrito ({len(inscritos)}):").grid(row=0, column=0, sticky="w")

    listbox = tk.Listbox(frm, width=60, height=12, exportselection=False)
    for p in inscritos:
        listbox.insert("end", f"{p.get('nome')} ({p.get('email')})")
    listbox.grid(row=1, column=0, pady=(6,0))

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=2, column=0, pady=(8,0))

    def remover_selecionado():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione um inscrito para remover.", parent=win)
            return
        idx = sel[0]
        participante = inscritos[idx]
        nome = participante.get("nome", "—")
        if messagebox.askyesno("Confirmar", f"Remover {nome} do evento?", parent=win):
            try:
                dados["inscricoes"].pop(idx)
                save_events()
                atualizar_treeview(tree)
                messagebox.showinfo("Removido", f"{nome} foi removido.", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao remover participante: {e}", parent=win)

    def cancelar():
        win.destroy()

    ttk.Button(btn_frame, text="Remover Selecionado", command=remover_selecionado).grid(row=0, column=0, padx=6)
    ttk.Button(btn_frame, text="Cancelar", command=cancelar).grid(row=0, column=1, padx=6)

def remover_evento(tree):
    """Remove o evento selecionado (apenas Admin)."""
    selected = tree.selection()
    if not selected:
        root = tree.winfo_toplevel()
        messagebox.showwarning(APP_NAME, "Selecione um evento para remover.", parent=root)
        return
    id_evento = int(selected[0])
    ev = eventos.get(id_evento)
    if not ev:
        root = tree.winfo_toplevel()
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=root)
        return
    root = tree.winfo_toplevel()
    if messagebox.askyesno(APP_NAME, f"Remover '{ev.get('nome')}' (ID {id_evento})?\nEsta ação é irreversível.", parent=root):
        del eventos[id_evento]
        save_events()
        atualizar_treeview(tree)

def setup_main_interface(root, user_role):
    """Configura a interface principal da aplicação após o login."""
    
    # Limpa widgets da tela de login (se estiver reutilizando a root)
    for widget in root.winfo_children():
        widget.destroy()

    root.title(APP_NAME)
    root.geometry("940x540")
    # Tenta centralizar a janela principal, mantendo a possibilidade de redimensionar
    root_width = 940
    root_height = 540
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (root_width / 2)
    y = (screen_height / 2) - (root_height / 2)
    root.geometry(f'{root_width}x{root_height}+{int(x)}+{int(y)}')
    root.resizable(True, True)

    style = ttk.Style(root)
    apply_style(root, style)

    header = ttk.Frame(root, padding=(12,8))
    header.pack(fill="x")
    ttk.Label(header, text=APP_NAME, font=(None, 16, "bold")).pack(anchor="w")
    
    if user_role == 'admin':
        ttk.Label(header, text="Modo: Administrador (Acesso Total)", foreground="#006600").pack(anchor="w")
    else:
        ttk.Label(header, text="Modo: Visualizador (Acesso Restrito)", foreground="#CC0000").pack(anchor="w")
    
    ttk.Label(header, text="Gerencie ou visualize eventos e participantes.").pack(anchor="w")


    bar = ttk.Frame(root, padding=(8,6))
    bar.pack(fill="x")

    tree_frame = ttk.Frame(root, padding=8)
    tree_frame.pack(fill="both", expand=True)

    cols = ("Nome", "Data", "Local", "Contato", "Inscritos")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

    tree.heading("#0", text="ID")
    tree.column("#0", width=60, minwidth=40, anchor="center", stretch=tk.NO)

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="w")

    tree.column("Nome", width=360)
    tree.column("Data", width=120, anchor="center")
    tree.column("Local", width=220)
    tree.column("Contato", width=160)
    tree.column("Inscritos", width=100, anchor="center")

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)
    
    # --- Configuração dos Botões com base no Papel (Role) ---
    
    # Botões de Gerenciamento (Apenas Admin)
    if user_role == 'admin':
        ttk.Button(bar, text="Adicionar Evento", command=lambda: abrir_adicionar_evento(root, tree, style)).pack(side="left", padx=6)
        ttk.Button(bar, text="Remover Evento", command=lambda: remover_evento(tree)).pack(side="left", padx=6)
        ttk.Label(bar, text="|").pack(side="left", padx=2)
        ttk.Button(bar, text="Inscrever Participante", command=lambda: abrir_inscrever_participante(root, tree)).pack(side="left", padx=6)
        ttk.Button(bar, text="Remover Participante", command=lambda: abrir_remover_participante(root, tree)).pack(side="left", padx=6)
    else:
        # Adiciona um marcador visual para o modo de visualização
        ttk.Label(bar, text="Funções de Edição Bloqueadas", foreground="#CC0000", font=(None, 10, "italic")).pack(side="left", padx=6)
        
    # Botão de Visualização (Ambos os Papéis)
    ttk.Button(bar, text="Consultar Inscritos", command=lambda: abrir_consultar_inscritos(root, tree)).pack(side="left", padx=6)

    ttk.Button(bar, text="Sair", command=root.quit).pack(side="right", padx=6)

    atualizar_treeview(tree)

def show_login(root):
    """Exibe a tela de login inicial."""
    global USER_ROLE

    # Configuração inicial da janela de login
    root.title("Acesso ao Sistema")
    root_width = 380
    root_height = 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (root_width / 2)
    y = (screen_height / 2) - (root_height / 2)
    root.geometry(f'{root_width}x{root_height}+{int(x)}+{int(y)}')
    root.resizable(False, False)

    style = ttk.Style(root)
    apply_style(root, style)

    frm = ttk.Frame(root, padding="20 20 20 20")
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Acesso ao Planning Events", font=(None, 14, "bold")).pack(pady=(0, 15))

    # Frame para as entradas
    entry_frame = ttk.Frame(frm)
    entry_frame.pack(pady=5)
    
    user_var = tk.StringVar()
    pass_var = tk.StringVar()

    ttk.Label(entry_frame, text="Usuário (Nome):", width=15, anchor="w").grid(row=0, column=0, pady=5, sticky="w")
    user_entry = ttk.Entry(entry_frame, textvariable=user_var, width=30)
    user_entry.grid(row=0, column=1, pady=5)

    ttk.Label(entry_frame, text="Senha:", width=15, anchor="w").grid(row=1, column=0, pady=5, sticky="w")
    pass_entry = ttk.Entry(entry_frame, textvariable=pass_var, show="*", width=30)
    pass_entry.grid(row=1, column=1, pady=5)
    
    user_entry.focus_set()

    def authenticate(event=None):
        """Verifica as credenciais e inicia a interface principal."""
        global USER_ROLE
        
        username = user_var.get().strip()
        password = pass_var.get().strip()
        
        # --- Lógica de Múltiplos Usuários Admin Corrigida ---
        if username in AUTHORIZED_USERS and password == AUTHORIZED_PASS:
            USER_ROLE = 'admin'
        elif username or password:
            USER_ROLE = 'guest'
            messagebox.showwarning("Acesso Negado", "Credenciais incorretas. Você será logado como Visualizador (Convidado).", parent=root)
        else:
             USER_ROLE = 'guest'
             
        # Limpa e configura a interface principal com o papel definido
        setup_main_interface(root, USER_ROLE)

    def login_as_guest():
        """Inicia a interface principal com o papel de Convidado."""
        global USER_ROLE
        USER_ROLE = 'guest'
        setup_main_interface(root, USER_ROLE)

    pass_entry.bind('<Return>', authenticate) # Liga a tecla Enter ao botão Entrar

    # Frame para os botões
    btn_frame = ttk.Frame(frm)
    btn_frame.pack(pady=15)
    
    ttk.Button(btn_frame, text="Entrar", command=authenticate).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Acessar como Convidado", command=login_as_guest).grid(row=0, column=1, padx=10)

def main_app_flow():
    """Função principal para iniciar o fluxo da aplicação: carregar dados -> login -> interface."""
    load_events()
    root = tk.Tk()
    
    show_login(root)

    def on_close():
        save_events()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main_app_flow()