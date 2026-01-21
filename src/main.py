import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Conexão e inicialização do banco

def inicializar_banco():
    db_password = os.getenv('db_password')
    if not db_password:
        raise ValueError('db_password não encontrado no arquivo .env')
    
    con = psycopg2.connect(
        dbname='escola', user='postgres', password=db_password, host='localhost',
        client_encoding='UTF8')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cursos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(50)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(50)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS curso_materia (
            curso_id INTEGER REFERENCES cursos(id),
            materia_id INTEGER REFERENCES materias(id),
            PRIMARY KEY(curso_id, materia_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100),
            curso_id INTEGER REFERENCES cursos(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id SERIAL PRIMARY KEY,
            aluno_id INTEGER REFERENCES alunos(id),
            materia_id INTEGER REFERENCES materias(id),
            trabalho DECIMAL(4,2) CHECK (trabalho >= 0 AND trabalho <= 5),
            simulado1 DECIMAL(4,2) CHECK (simulado1 >= 0 AND simulado1 <= 1),
            simulado2 DECIMAL(4,2) CHECK (simulado2 >= 0 AND simulado2 <= 1),
            prova DECIMAL(4,2) CHECK (prova >= 0 AND prova <= 5)
        )
    """)
    con.commit()
    return con

class MiniEscolaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MiniEscola')
        self.geometry('1280x720')
        self.con = inicializar_banco()
        # Largura padrão para o painel esquerdo
        self.largura_painel_esq = 300
        self.iniciar_interface()
        # Label de status para mensagens
        self.status_label = ttk.Label(self, text='', foreground='green', background='#f5f5f5', font=('Arial', 12, 'bold'), anchor='w')
        self.status_label.pack(side='bottom', fill='x')

    def iniciar_interface(self):
        # Frame principal que conterá o notebook
        frame_principal = ttk.Frame(self)
        frame_principal.pack(expand=True, fill='both')
        
        # Notebook dentro do frame principal
        nb = ttk.Notebook(frame_principal)
        nb.pack(expand=True, fill='both')
        
        nb.add(self.painel_cursos(), text='Cursos')
        nb.add(self.painel_materias(), text='Matérias')
        nb.add(self.painel_alunos(), text='Alunos')
        nb.add(self.painel_notas(), text='Notas')

    def painel_cursos(self):
        frame = ttk.Frame(self)
        # Painel esquerdo: lista de cursos
        esq = ttk.Frame(frame, width=self.largura_painel_esq)
        esq.pack(side='left', fill='y', padx=5, pady=5)
        esq.pack_propagate(False)  # Impede que o frame encolha
        
        # Botão de atualizar para cursos
        ttk.Button(esq, text='Atualizar', command=self.atualizar_cursos).pack(fill='x', pady=2)
        ttk.Separator(esq, orient='horizontal').pack(fill='x', pady=5)
        
        # Dropdown de cursos existentes
        ttk.Label(esq, text='Selecione o Curso:').pack(fill='x')
        self.combo_curso_edicao = ttk.Combobox(esq, state='readonly')
        self.combo_curso_edicao.pack(fill='x', pady=(0,5))
        self.combo_curso_edicao.bind('<<ComboboxSelected>>', self.preencher_curso_edicao)
        
        # Campo de nome
        ttk.Label(esq, text='Nome do Curso:').pack(fill='x')
        self.entrada_curso = ttk.Entry(esq)
        self.entrada_curso.pack(fill='x', pady=(0,5))
        
        # Botões de ação
        ttk.Button(esq, text='Adicionar Curso', command=self.adicionar_curso).pack(fill='x', pady=2)
        ttk.Button(esq, text='Salvar Alterações', command=self.salvar_alteracoes_curso).pack(fill='x', pady=2)
        ttk.Button(esq, text='Remover Curso', command=self.remover_curso).pack(fill='x', pady=2)
        
        # Criar Treeview para cursos
        self.lista_cursos = ttk.Treeview(esq, columns=('id', 'nome'), show='headings', height=15)
        self.lista_cursos.heading('id', text='ID')
        self.lista_cursos.heading('nome', text='Nome do Curso')
        self.lista_cursos.column('id', width=30, minwidth=10, stretch=False, anchor='center')
        self.lista_cursos.column('nome', width=250, stretch=True)
        self.lista_cursos.pack(fill='y', expand=True)
        
        # Bind para seleção
        self.lista_cursos.bind('<<TreeviewSelect>>', lambda _: self.carregar_materias_curso())

        # Painel direito: checkboxes de matérias
        self.frame_dir = ttk.LabelFrame(frame, text='Matérias do Curso')
        self.frame_dir.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        self.vars_check = {}  # materia_id -> IntVar
        self.botoes_check = {}
        self.carregar_cursos_combo_edicao()
        return frame

    def atualizar_cursos(self):
        self.carregar_cursos()
        self.carregar_materias_curso()

    def carregar_cursos(self):
        self.carregar_lista(
            self.lista_cursos,
            'SELECT id, nome FROM cursos ORDER BY nome'
        )

    def carregar_cursos_combo_edicao(self):
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM cursos ORDER BY nome')
        self.combo_curso_edicao['values'] = [f"{id_}: {nome}" for id_, nome in cur.fetchall()]
        self.combo_curso_edicao.set('')
        self.entrada_curso.delete(0, tk.END)

    def preencher_curso_edicao(self, event=None):
        sel = self.combo_curso_edicao.get()
        if not sel:
            self.entrada_curso.delete(0, tk.END)
            return
        curso_id = sel.split(':')[0]
        cur = self.con.cursor()
        cur.execute('SELECT nome FROM cursos WHERE id=%s', (curso_id,))
        res = cur.fetchone()
        if res:
            nome = res[0]
            self.entrada_curso.delete(0, tk.END)
            self.entrada_curso.insert(0, nome)

    def salvar_alteracoes_curso(self):
        sel = self.combo_curso_edicao.get()
        if not sel:
            self.mostrar_status('Selecione um curso para editar.', 'red')
            return
        curso_id = sel.split(':')[0]
        nome = self.validar_entrada(self.entrada_curso.get())
        if not nome:
            self.mostrar_status('Nome inválido.', 'red')
            return
        if self.operacao_banco('UPDATE cursos SET nome=%s WHERE id=%s', (nome, curso_id)):
            self.carregar_cursos()
            self.carregar_cursos_combo_edicao()
            self.mostrar_status('Curso atualizado com sucesso!')

    def adicionar_curso(self):
        nome = self.validar_entrada(self.entrada_curso.get())
        if not nome:
            self.mostrar_status('Nome inválido.', 'red')
            return
        if self.operacao_banco('INSERT INTO cursos(nome) VALUES(%s)', (nome,)):
            self.entrada_curso.delete(0, tk.END)
            self.carregar_cursos()
            self.carregar_cursos_combo_edicao()
            self.mostrar_status('Curso adicionado com sucesso!')

    def remover_curso(self):
        sel = self.combo_curso_edicao.get()
        if not sel:
            self.mostrar_status('Selecione um curso para remover.', 'red')
            return
        curso_id = sel.split(':')[0]
        # Executa as remoções em cascata na ordem correta
        if self.operacao_banco('DELETE FROM notas WHERE aluno_id IN (SELECT id FROM alunos WHERE curso_id=%s)', (curso_id,)) and \
           self.operacao_banco('UPDATE alunos SET curso_id = NULL WHERE curso_id = %s', (curso_id,)) and \
           self.operacao_banco('DELETE FROM curso_materia WHERE curso_id=%s', (curso_id,)) and \
           self.operacao_banco('DELETE FROM cursos WHERE id=%s', (curso_id,)):
            self.carregar_cursos()
            self.carregar_cursos_combo_edicao()
            # Limpa os checkboxes de matérias
            for cb in self.botoes_check.values():
                cb.destroy()
            self.vars_check.clear()
            self.botoes_check.clear()
            self.mostrar_status('Curso removido!','red')

    def carregar_materias_curso(self):
        sel = self.lista_cursos.selection()
        if not sel: return
        id_curso = self.lista_cursos.item(sel[0])['values'][0]
        
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM materias ORDER BY nome')
        cur.execute('SELECT materia_id FROM curso_materia WHERE curso_id=%s', (id_curso,))
        ligadas = {row[0] for row in cur.fetchall()}
        
        # Limpar frame_dir completamente
        for widget in self.frame_dir.winfo_children():
            widget.destroy()
        
        # Limpar variáveis de controle
        self.vars_check.clear()
        self.botoes_check.clear()
        
        # Frame para a lista de matérias com scrollbar
        frame_materias = ttk.Frame(self.frame_dir)
        frame_materias.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Campo de busca
        frame_busca = ttk.Frame(frame_materias)
        frame_busca.pack(fill='x', pady=(0,5))
        ttk.Label(frame_busca, text='Buscar matéria:').pack(side='left')
        self.busca_materia = ttk.Entry(frame_busca)
        self.busca_materia.pack(side='left', fill='x', expand=True, padx=(5,0))
        self.busca_materia.bind('<KeyRelease>', lambda e: self.filtrar_materias_curso(id_curso, ligadas))
        
        # Frame para scrollbar e lista
        frame_lista = ttk.Frame(frame_materias)
        frame_lista.pack(fill='both', expand=True)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(frame_lista)
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)
        self.frame_checkboxes = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack dos elementos
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Criar janela no canvas
        canvas_frame = canvas.create_window((0, 0), window=self.frame_checkboxes, anchor="nw")
        
        # Configurar scroll
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.frame_checkboxes.bind('<Configure>', configure_scroll)
        
        # Configurar redimensionamento
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        # Inserir checkboxes iniciais
        self.filtrar_materias_curso(id_curso, ligadas)

    def filtrar_materias_curso(self, id_curso, ligadas):
        # Limpar checkboxes existentes
        for widget in self.frame_checkboxes.winfo_children():
            widget.destroy()
        self.vars_check.clear()
        self.botoes_check.clear()
        
        # Obter texto de busca
        texto_busca = self.busca_materia.get().lower()
        
        # Buscar matérias
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM materias ORDER BY nome')
        materias = cur.fetchall()
        
        # Criar checkboxes filtrados
        for m_id, m_nome in materias:
            if texto_busca in m_nome.lower():
                var = tk.IntVar(value=1 if m_id in ligadas else 0)
                cb = ttk.Checkbutton(self.frame_checkboxes, text=m_nome, variable=var,
                                   command=lambda m_id=m_id, var=var: self.toggle_materia(id_curso, m_id, var.get()))
                cb.pack(anchor='w')
                self.vars_check[m_id] = var
                self.botoes_check[m_id] = cb

    def toggle_materia(self, curso_id, materia_id, ativo):
        cur = self.con.cursor()
        if ativo:
            cur.execute('INSERT INTO curso_materia(curso_id,materia_id) VALUES(%s,%s) ON CONFLICT DO NOTHING',
                       (curso_id, materia_id))
        else:
            cur.execute('DELETE FROM curso_materia WHERE curso_id=%s AND materia_id=%s',
                        (curso_id, materia_id))
        self.con.commit()

    def painel_materias(self):
        f = ttk.Frame(self)
        
        # Painel esquerdo: entrada e botões
        esq = ttk.Frame(f, width=self.largura_painel_esq)
        esq.pack(side='left', fill='y', padx=5, pady=5)
        esq.pack_propagate(False)  # Impede que o frame encolha
        
        # Botão de atualizar para matérias
        ttk.Button(esq, text='Atualizar', command=self.atualizar_materias).pack(fill='x', pady=2)
        ttk.Separator(esq, orient='horizontal').pack(fill='x', pady=5)
        
        # Dropdown de matérias existentes
        ttk.Label(esq, text='Selecione a Matéria:').pack(fill='x')
        self.combo_mat_edicao = ttk.Combobox(esq, state='readonly')
        self.combo_mat_edicao.pack(fill='x', pady=(0,5))
        self.combo_mat_edicao.bind('<<ComboboxSelected>>', self.preencher_mat_edicao)
        
        # Campo de nome
        ttk.Label(esq, text='Nome da Matéria:').pack(fill='x')
        self.entrada_mat = ttk.Entry(esq)
        self.entrada_mat.pack(fill='x', pady=(0,5))
        
        # Botões de ação
        ttk.Button(esq, text='Adicionar Matéria', command=self.adicionar_materia).pack(fill='x', pady=2)
        ttk.Button(esq, text='Salvar Alterações', command=self.salvar_alteracoes_materia).pack(fill='x', pady=2)
        ttk.Button(esq, text='Remover Matéria', command=self.remover_materia).pack(fill='x', pady=2)
        
        # Painel direito: lista de matérias
        dir = ttk.Frame(f)
        dir.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Criar Treeview para matérias
        self.lista_materias = ttk.Treeview(dir, columns=('id', 'nome'), show='headings', height=15)
        self.lista_materias.heading('id', text='ID')
        self.lista_materias.heading('nome', text='Nome da Matéria')
        self.lista_materias.column('id', width=30, minwidth=10, stretch=False, anchor='center')
        self.lista_materias.column('nome', width=200, stretch=True)
        self.lista_materias.pack(fill='both', expand=True)
        
        self.carregar_materias_combo_edicao()
        self.carregar_materias()
        return f

    def atualizar_materias(self):
        self.carregar_materias()

    def carregar_materias(self):
        self.carregar_lista(
            self.lista_materias,
            'SELECT id, nome FROM materias ORDER BY nome'
        )

    def carregar_materias_combo_edicao(self):
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM materias ORDER BY nome')
        self.combo_mat_edicao['values'] = [f"{id_}: {nome}" for id_, nome in cur.fetchall()]
        self.combo_mat_edicao.set('')
        self.entrada_mat.delete(0, tk.END)

    def preencher_mat_edicao(self, event=None):
        sel = self.combo_mat_edicao.get()
        if not sel:
            self.entrada_mat.delete(0, tk.END)
            return
        mat_id = sel.split(':')[0]
        cur = self.con.cursor()
        cur.execute('SELECT nome FROM materias WHERE id=%s', (mat_id,))
        res = cur.fetchone()
        if res:
            nome = res[0]
            self.entrada_mat.delete(0, tk.END)
            self.entrada_mat.insert(0, nome)

    def salvar_alteracoes_materia(self):
        sel = self.combo_mat_edicao.get()
        if not sel:
            self.mostrar_status('Selecione uma matéria para editar.', 'red')
            return
        mat_id = sel.split(':')[0]
        nome = self.validar_entrada(self.entrada_mat.get())
        if not nome:
            self.mostrar_status('Nome inválido.', 'red')
            return
        if self.operacao_banco('UPDATE materias SET nome=%s WHERE id=%s', (nome, mat_id)):
            self.carregar_materias()
            self.carregar_materias_combo_edicao()
            self.mostrar_status('Matéria atualizada com sucesso!')

    def adicionar_materia(self):
        nome = self.validar_entrada(self.entrada_mat.get())
        if not nome:
            self.mostrar_status('Nome inválido.', 'red')
            return
        if self.operacao_banco('INSERT INTO materias(nome) VALUES(%s)', (nome,)):
            self.entrada_mat.delete(0, tk.END)
            self.carregar_materias()
            self.carregar_materias_combo_edicao()
            self.carregar_mat_combo()
            self.carregar_materias_curso()
            self.mostrar_status('Matéria adicionada com sucesso!')

    def remover_materia(self):
        sel = self.combo_mat_edicao.get()
        if not sel:
            self.mostrar_status('Selecione uma matéria para remover.', 'red')
            return
        mat_id = sel.split(':')[0]
        # Executa as remoções em cascata na ordem correta
        if self.operacao_banco('DELETE FROM notas WHERE materia_id=%s', (mat_id,)) and \
           self.operacao_banco('DELETE FROM curso_materia WHERE materia_id=%s', (mat_id,)) and \
           self.operacao_banco('DELETE FROM materias WHERE id=%s', (mat_id,)):
            self.carregar_materias()
            self.carregar_materias_combo_edicao()
            self.carregar_mat_combo()
            self.carregar_materias_curso()
            self.mostrar_status('Matéria removida!','red')

    def painel_alunos(self):
        f = ttk.Frame(self)
        
        # Painel esquerdo: entrada e botões
        esq = ttk.Frame(f, width=self.largura_painel_esq)
        esq.pack(side='left', fill='y', padx=5, pady=5)
        esq.pack_propagate(False)  # Impede que o frame encolha
        
        # Botão de atualizar para alunos
        ttk.Button(esq, text='Atualizar', command=self.atualizar_alunos).pack(fill='x', pady=2)
        ttk.Separator(esq, orient='horizontal').pack(fill='x', pady=5)
        
        # Dropdown de alunos existentes
        ttk.Label(esq, text='Selecione o Aluno:').pack(fill='x')
        self.combo_aluno_edicao = ttk.Combobox(esq, state='readonly')
        self.combo_aluno_edicao.pack(fill='x', pady=(0,5))
        self.combo_aluno_edicao.bind('<<ComboboxSelected>>', self.preencher_aluno_edicao)
        
        # Campo de nome
        ttk.Label(esq, text='Nome do Aluno:').pack(fill='x')
        self.entrada_aluno = ttk.Entry(esq)
        self.entrada_aluno.pack(fill='x', pady=(0,5))
        
        # Dropdown de cursos
        ttk.Label(esq, text='Selecione o Curso:').pack(fill='x')
        self.combo_cursos = ttk.Combobox(esq, state='readonly')
        self.combo_cursos.pack(fill='x', pady=(0,5))
        
        # Botões de ação
        ttk.Button(esq, text='Adicionar Aluno', command=self.adicionar_aluno).pack(fill='x', pady=2)
        ttk.Button(esq, text='Salvar Alterações', command=self.salvar_alteracoes_aluno).pack(fill='x', pady=2)
        ttk.Button(esq, text='Remover Aluno', command=self.remover_aluno).pack(fill='x', pady=2)
        
        # Painel direito: lista de alunos
        dir = ttk.Frame(f)
        dir.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Criar Treeview para alunos
        self.lista_alunos = ttk.Treeview(dir, columns=('id', 'nome', 'curso'), show='headings', height=15)
        self.lista_alunos.heading('id', text='ID')
        self.lista_alunos.heading('nome', text='Nome do Aluno')
        self.lista_alunos.heading('curso', text='Curso')
        self.lista_alunos.column('id', width=30, minwidth=10, stretch=False, anchor='center')
        self.lista_alunos.column('nome', width=100, stretch=True)
        self.lista_alunos.column('curso', width=200, stretch=True)
        self.lista_alunos.pack(fill='both', expand=True)
        
        self.carregar_cursos_combo()
        self.carregar_alunos()
        self.carregar_alunos_combo_edicao()
        return f

    def atualizar_alunos(self):
        self.carregar_alunos()
        self.carregar_cursos_combo()

    def carregar_cursos_combo(self):
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM cursos ORDER BY nome')
        self.combo_cursos['values'] = [f"{id_}: {nome}" for id_, nome in cur.fetchall()]

    def carregar_alunos(self):
        self.carregar_lista(
            self.lista_alunos,
            '''
            SELECT a.id, a.nome, c.nome 
            FROM alunos a 
            LEFT JOIN cursos c ON a.curso_id = c.id 
            ORDER BY a.id
            '''
        )

    def carregar_alunos_combo_edicao(self):
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM alunos ORDER BY nome')
        self.combo_aluno_edicao['values'] = [f"{id_}: {nome}" for id_, nome in cur.fetchall()]
        self.combo_aluno_edicao.set('')
        self.entrada_aluno.delete(0, tk.END)
        self.combo_cursos.set('')

    def preencher_aluno_edicao(self, event=None):
        sel = self.combo_aluno_edicao.get()
        if not sel:
            self.entrada_aluno.delete(0, tk.END)
            self.combo_cursos.set('')
            return
        aluno_id = sel.split(':')[0]
        cur = self.con.cursor()
        cur.execute('SELECT nome, curso_id FROM alunos WHERE id=%s', (aluno_id,))
        res = cur.fetchone()
        if res:
            nome, curso_id = res
            self.entrada_aluno.delete(0, tk.END)
            self.entrada_aluno.insert(0, nome)
            if curso_id:
                cur.execute('SELECT nome FROM cursos WHERE id=%s', (curso_id,))
                curso_nome = cur.fetchone()
                if curso_nome:
                    for v in self.combo_cursos['values']:
                        if v.endswith(curso_nome[0]):
                            self.combo_cursos.set(v)
                            break
            else:
                self.combo_cursos.set('')

    def salvar_alteracoes_aluno(self):
        sel = self.combo_aluno_edicao.get()
        if not sel:
            self.mostrar_status('Selecione um aluno para editar.', 'red')
            return
        aluno_id = sel.split(':')[0]
        nome = self.validar_entrada(self.entrada_aluno.get())
        curso = self.combo_cursos.get().split(':')[0] if self.combo_cursos.get() else None
        if not nome:
            self.mostrar_status('Nome inválido.', 'red')
            return
        if self.operacao_banco('UPDATE alunos SET nome=%s, curso_id=%s WHERE id=%s', (nome, curso, aluno_id)):
            self.carregar_alunos()
            self.carregar_alunos_combo_edicao()
            self.filtrar_notas()
            self.mostrar_status('Aluno atualizado com sucesso!')

    def adicionar_aluno(self):
        nome = self.validar_entrada(self.entrada_aluno.get())
        curso = self.combo_cursos.get().split(':')[0] if self.combo_cursos.get() else None
        if not nome:
            self.mostrar_status('Nome inválido.', 'red')
            return
        if self.operacao_banco('INSERT INTO alunos(nome,curso_id) VALUES(%s,%s)', (nome, curso)):
            self.entrada_aluno.delete(0, tk.END)
            self.carregar_alunos()
            self.carregar_alunos_combo_edicao()
            self.filtrar_notas()
            self.mostrar_status('Aluno adicionado com sucesso!')

    def remover_aluno(self):
        sel = self.combo_aluno_edicao.get()
        if not sel:
            self.mostrar_status('Selecione um aluno para remover.', 'red')
            return
        aluno_id = sel.split(':')[0]
        if self.operacao_banco('DELETE FROM notas WHERE aluno_id=%s', (aluno_id,)) and \
           self.operacao_banco('DELETE FROM alunos WHERE id=%s', (aluno_id,)):
            self.carregar_alunos()
            self.carregar_alunos_combo_edicao()
            self.filtrar_notas()
            self.entrada_aluno.delete(0, tk.END)
            self.combo_cursos.set('')
            self.combo_aluno_edicao.set('')
            self.mostrar_status('Aluno removido!','red')

    def painel_notas(self):
        f = ttk.Frame(self)
        
        # Painel esquerdo: seleções e botões
        esq = ttk.Frame(f, width=self.largura_painel_esq)
        esq.pack(side='left', fill='y', padx=5, pady=5)
        esq.pack_propagate(False)  # Impede que o frame encolha
        
        # Botão de atualizar para notas
        ttk.Button(esq, text='Atualizar', command=self.atualizar_notas).pack(fill='x', pady=2)
        ttk.Separator(esq, orient='horizontal').pack(fill='x', pady=5)
        
        ttk.Label(esq, text='Selecione o Aluno:').pack(fill='x')
        self.combo_aluno = ttk.Combobox(esq, state='readonly')
        self.combo_aluno.pack(fill='x', pady=(0,5))
        self.combo_aluno.bind('<<ComboboxSelected>>', self.atualizar_materias_aluno)
        self.combo_aluno.bind('<<ComboboxSelected>>', self.carregar_notas_edicao, add='+')
        
        ttk.Label(esq, text='Selecione a Matéria:').pack(fill='x')
        self.combo_mat = ttk.Combobox(esq, state='readonly')
        self.combo_mat.pack(fill='x', pady=(0,5))
        self.combo_mat.bind('<<ComboboxSelected>>', self.carregar_notas_edicao)
        
        ttk.Label(esq, text='Trabalho (0-5):').pack(fill='x')
        self.entrada_trabalho = ttk.Entry(esq)
        self.entrada_trabalho.pack(fill='x', pady=(0,5))
        ttk.Label(esq, text='Simulado 1 (0-1):').pack(fill='x')
        self.entrada_sim1 = ttk.Entry(esq)
        self.entrada_sim1.pack(fill='x', pady=(0,5))
        ttk.Label(esq, text='Simulado 2 (0-1):').pack(fill='x')
        self.entrada_sim2 = ttk.Entry(esq)
        self.entrada_sim2.pack(fill='x', pady=(0,5))
        ttk.Label(esq, text='Prova (0-5):').pack(fill='x')
        self.entrada_prova = ttk.Entry(esq)
        self.entrada_prova.pack(fill='x', pady=(0,5))
        
        # Botões Salvar e Remover Notas (vertical)
        ttk.Button(esq, text='Salvar Notas', command=self.adicionar_nota).pack(fill='x', pady=2)
        ttk.Button(esq, text='Remover Notas', command=self.remover_notas).pack(fill='x', pady=(0,5))
        
        # Caixa de explicação da equação da nota final
        frame_equacao = ttk.LabelFrame(esq, text='Cálculo da Nota Final')
        frame_equacao.pack(fill='x', pady=(10, 0), padx=2)
        texto_eq = (
            'a = Prova (0 a 5)          [Obrigatório]\n'
            'b = Trabalho (0 a 5)       [Obrigatório]\n'
            'c = Simulado 1 (0 a 1)     [Opcional]\n'
            'd = Simulado 2 (0 a 1)     [Opcional]\n'
            '\n'
            'Nota Final = a + b + c + d\n'
            '\n'
            'A nota final mínima para aprovação é 6,0.\n'
            '* A nota final máxima é 10,0.'
        )
        label_eq = ttk.Label(
            frame_equacao,
            text=texto_eq,
            justify='left',
            anchor='w',
            font=('Consolas', 8)
        )
        label_eq.pack(fill='x', padx=5, pady=5)
        
        # Painel direito: lista de notas
        dir = ttk.Frame(f)
        dir.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Frame para filtros
        frame_filtros = ttk.Frame(dir)
        frame_filtros.pack(fill='x', pady=(0,5))
        
        # Campo de busca por nome
        ttk.Label(frame_filtros, text='Buscar aluno:').pack(side='left')
        self.busca_aluno = ttk.Entry(frame_filtros)
        self.busca_aluno.pack(side='left', fill='x', expand=True, padx=(5,10))
        self.busca_aluno.bind('<KeyRelease>', self.filtrar_notas)
        
        # Combobox para filtrar por curso
        ttk.Label(frame_filtros, text='Filtrar por curso:').pack(side='left')
        self.filtro_curso = ttk.Combobox(frame_filtros, state='readonly', width=20)
        self.filtro_curso.pack(side='left', padx=(5,0))
        self.filtro_curso.bind('<<ComboboxSelected>>', self.filtrar_notas)
        
        # Criar Treeview para notas
        self.lista_notas = ttk.Treeview(dir, columns=('status', 'materia', 'prova', 'trabalho', 'sim1', 'sim2', 'final'), show='tree headings')
        self.lista_notas.heading('#0', text='Aluno')
        self.lista_notas.heading('status', text='Status')
        self.lista_notas.heading('materia', text='Matéria')
        self.lista_notas.heading('prova', text='Prova')
        self.lista_notas.heading('trabalho', text='Trabalho')
        self.lista_notas.heading('sim1', text='Simulado 1')
        self.lista_notas.heading('sim2', text='Simulado 2')
        self.lista_notas.heading('final', text='Nota Final')
        self.lista_notas.column('#0', width=200)
        self.lista_notas.column('status', width=30, anchor='center')
        self.lista_notas.column('materia', width=150)
        self.lista_notas.column('prova', width=30, anchor='center')
        self.lista_notas.column('trabalho', width=30, anchor='center')
        self.lista_notas.column('sim1', width=30, anchor='center')
        self.lista_notas.column('sim2', width=30, anchor='center')
        self.lista_notas.column('final', width=30, anchor='center')
        
        self.lista_notas.pack(fill='both', expand=True)
        
        self.carregar_filtro_cursos()
        self.filtrar_notas()
        self.carregar_aluno_combo()
        self.carregar_mat_combo()
        return f

    def atualizar_notas(self):
        self.carregar_filtro_cursos()
        self.filtrar_notas()
        self.carregar_aluno_combo()
        self.carregar_mat_combo()

    def atualizar_materias_aluno(self, event=None):
        self.combo_mat.set('')  # Limpa seleção atual
        self.carregar_mat_combo()

    def carregar_aluno_combo(self):
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM alunos ORDER BY nome')
        self.combo_aluno['values'] = [f"{id_}: {nome}" for id_, nome in cur.fetchall()]

    def carregar_mat_combo(self):
        aluno_id = self.combo_aluno.get().split(':')[0] if self.combo_aluno.get() else None
        if not aluno_id:
            self.combo_mat['values'] = []
            return
            
        cur = self.con.cursor()
        cur.execute('SELECT curso_id FROM alunos WHERE id=%s', (aluno_id,))
        result = cur.fetchone()
        if not result or not result[0]:
            self.combo_mat['values'] = []
            return
            
        curso_id = result[0]
        cur.execute('''
            SELECT m.id, m.nome 
            FROM materias m 
            JOIN curso_materia cm ON m.id = cm.materia_id 
            WHERE cm.curso_id = %s 
            ORDER BY m.nome
        ''', (curso_id,))
        self.combo_mat['values'] = [f"{id_}: {nome}" for id_, nome in cur.fetchall()]

    def carregar_filtro_cursos(self):
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM cursos ORDER BY nome')
        cursos = [('', 'Todos os cursos')] + cur.fetchall()
        self.filtro_curso['values'] = [nome for _, nome in cursos]
        self.filtro_curso.set('Todos os cursos')

    def filtrar_notas(self, event=None):
        # Limpar lista atual
        for item in self.lista_notas.get_children():
            self.lista_notas.delete(item)
        texto_busca = self.busca_aluno.get().lower()
        curso_filtro = self.filtro_curso.get()
        cur = self.con.cursor()
        query = """
            SELECT DISTINCT a.id, a.nome, c.nome as curso_nome
            FROM alunos a 
            INNER JOIN notas n ON a.id = n.aluno_id 
            LEFT JOIN cursos c ON a.curso_id = c.id
            WHERE a.nome ILIKE %s
        """
        params = [f'%{texto_busca}%']
        if curso_filtro != 'Todos os cursos':
            query += " AND c.nome = %s"
            params.append(curso_filtro)
        query += " ORDER BY a.nome"
        cur.execute(query, params)
        alunos = cur.fetchall()
        for i, (aluno_id, aluno_nome, curso_nome) in enumerate(alunos):
            bg_color = '#f0f0f0' if i % 2 == 0 else 'white'
            def sigla_curso(nome):
                stopwords = {'de', 'da', 'do', 'das', 'dos', 'e'}
                palavras = [p for p in nome.split() if p not in stopwords]
                if not palavras:
                    return ''
                if len(palavras) == 1:
                    return palavras[0][:3]
                return f"{palavras[0][:3]}. {palavras[1]}"
            sigla = sigla_curso(curso_nome)
            nome_exibicao = f"{aluno_nome} ({sigla})"
            aluno_item = self.lista_notas.insert('', 'end', text=nome_exibicao, values=('', '', '', '', '', ''))
            self.lista_notas.item(aluno_item, tags=(f'aluno_{i}',))
            self.lista_notas.tag_configure(f'aluno_{i}', background=bg_color)
            cur.execute("""
                SELECT m.nome, n.trabalho, n.simulado1, n.simulado2, n.prova, n.id
                FROM notas n
                INNER JOIN materias m ON n.materia_id = m.id
                WHERE n.aluno_id = %s
                ORDER BY m.nome
            """, (aluno_id,))
            notas = cur.fetchall()
            nota_geral = 0
            for materia_nome, trabalho, sim1, sim2, prova, nota_id in notas:
                t = trabalho or 0
                s1 = sim1 or 0
                s2 = sim2 or 0
                p = prova or 0
                status = ''
                if trabalho is None or prova is None:
                    status = 'Pendente'
                else:
                    nota_final = t + s1 + s2 + p
                    if nota_final > 10:
                        nota_final = 10
                    if nota_final > 6:
                        status = 'Aprovado'
                    else:
                        status = 'Reprovado'
                nota_final = t + s1 + s2 + p
                if nota_final > 10:
                    nota_final = 10
                nota_geral += nota_final
                valor_final = f'{nota_final:.1f}' if nota_final > 0 else ''
                nota_item = self.lista_notas.insert(aluno_item, 'end', text='', values=(
                    status, materia_nome, p if p else '', t if t else '', s1 if s1 else '', s2 if s2 else '', valor_final
                ))
                self.lista_notas.item(nota_item, tags=(f'aluno_{i}',))
            self.lista_notas.item(aluno_item, open=True)

    def adicionar_nota(self):
        a = self.combo_aluno.get().split(':')[0]
        m = self.combo_mat.get().split(':')[0]
        t = self.entrada_trabalho.get()
        s1 = self.entrada_sim1.get()
        s2 = self.entrada_sim2.get()
        p = self.entrada_prova.get()
        if not a or not m:
            messagebox.showwarning('Aviso', 'Selecione aluno e matéria')
            return
        if not any(self.validar_entrada(v, tipo) for v, tipo in [
            (t, 'trabalho'), (s1, 'simulado'), (s2, 'simulado'), (p, 'prova')]):
            messagebox.showwarning('Aviso', 'Insira pelo menos uma nota válida')
            return
        cur = self.con.cursor()
        cur.execute('''
            SELECT 1 FROM curso_materia cm
            JOIN alunos a ON a.curso_id = cm.curso_id
            WHERE a.id = %s AND cm.materia_id = %s
        ''', (a, m))
        if not cur.fetchone():
            messagebox.showerror('Erro', 'Matéria não pertence ao curso do aluno')
            return
        if self.operacao_banco('DELETE FROM notas WHERE aluno_id=%s AND materia_id=%s', (a, m)) and \
           self.operacao_banco(
               'INSERT INTO notas(aluno_id,materia_id,trabalho,simulado1,simulado2,prova) VALUES(%s,%s,%s,%s,%s,%s)',
               (a, m, 
                float(t.replace(',', '.')) if self.validar_entrada(t, 'trabalho') else None,
                float(s1.replace(',', '.')) if self.validar_entrada(s1, 'simulado') else None,
                float(s2.replace(',', '.')) if self.validar_entrada(s2, 'simulado') else None,
                float(p.replace(',', '.')) if self.validar_entrada(p, 'prova') else None
               )
           ):
            self.entrada_trabalho.delete(0, tk.END)
            self.entrada_sim1.delete(0, tk.END)
            self.entrada_sim2.delete(0, tk.END)
            self.entrada_prova.delete(0, tk.END)
            self.filtrar_notas()
            self.mostrar_status('Nota salva com sucesso!')

    def remover_notas(self):
        a = self.combo_aluno.get().split(':')[0]
        m = self.combo_mat.get().split(':')[0]
        if not a or not m:
            messagebox.showwarning('Aviso', 'Selecione aluno e matéria')
            return
        cur = self.con.cursor()
        cur.execute('DELETE FROM notas WHERE aluno_id=%s AND materia_id=%s', (a, m))
        self.con.commit()
        self.filtrar_notas()
        self.entrada_trabalho.delete(0, tk.END)
        self.entrada_sim1.delete(0, tk.END)
        self.entrada_sim2.delete(0, tk.END)
        self.entrada_prova.delete(0, tk.END)
        self.mostrar_status('Nota removida!','red')

    def carregar_lista(self, treeview, query, params=None):
        """Função utilitária para carregar dados em um Treeview"""
        for item in treeview.get_children():
            treeview.delete(item)
        cur = self.con.cursor()
        cur.execute(query, params or ())
        for valores in cur.fetchall():
            treeview.insert('', 'end', values=valores)

    def validar_entrada(self, valor, tipo='texto'):
        """Função utilitária para validação de entradas"""
        if tipo == 'texto':
            if not valor or not valor.strip():
                return False
            # Validação de tamanho baseada no contexto
            if hasattr(self, 'entrada_aluno'):
                if len(valor) > 100:
                    return False
            elif len(valor) > 50:
                return False
            return valor.strip()
        elif tipo == 'trabalho':
            try:
                v = float(valor.replace(',', '.'))
                return 0 <= v <= 5
            except:
                return False
        elif tipo == 'simulado':
            try:
                v = float(valor.replace(',', '.'))
                return 0 <= v <= 1
            except:
                return False
        elif tipo == 'prova':
            try:
                v = float(valor.replace(',', '.'))
                return 0 <= v <= 5
            except:
                return False

    def operacao_banco(self, query, params=None, commit=True):
        """Função utilitária para operações no banco de dados"""
        cur = self.con.cursor()
        try:
            cur.execute(query, params or ())
            if commit:
                self.con.commit()
            return True
        except Exception as e:
            if commit:
                self.con.rollback()
            messagebox.showerror('Erro', str(e))
            return False

    def carregar_notas_edicao(self, event=None):
        a = self.combo_aluno.get().split(':')[0] if self.combo_aluno.get() else None
        m = self.combo_mat.get().split(':')[0] if self.combo_mat.get() else None
        # Limpa campos se não houver seleção
        if not a or not m:
            self.entrada_trabalho.delete(0, tk.END)
            self.entrada_sim1.delete(0, tk.END)
            self.entrada_sim2.delete(0, tk.END)
            self.entrada_prova.delete(0, tk.END)
            return
        cur = self.con.cursor()
        cur.execute('SELECT trabalho, simulado1, simulado2, prova FROM notas WHERE aluno_id=%s AND materia_id=%s', (a, m))
        resultado = cur.fetchone()
        # Preenche campos se houver nota, senão limpa
        if resultado:
            t, s1, s2, p = resultado
            self.entrada_trabalho.delete(0, tk.END)
            self.entrada_trabalho.insert(0, str(t) if t is not None else '')
            self.entrada_sim1.delete(0, tk.END)
            self.entrada_sim1.insert(0, str(s1) if s1 is not None else '')
            self.entrada_sim2.delete(0, tk.END)
            self.entrada_sim2.insert(0, str(s2) if s2 is not None else '')
            self.entrada_prova.delete(0, tk.END)
            self.entrada_prova.insert(0, str(p) if p is not None else '')
        else:
            self.entrada_trabalho.delete(0, tk.END)
            self.entrada_sim1.delete(0, tk.END)
            self.entrada_sim2.delete(0, tk.END)
            self.entrada_prova.delete(0, tk.END)

    def mostrar_status(self, mensagem, cor='green', tempo=4000):
        self.status_label.config(text=mensagem, foreground=cor, background='#f5f5f5')
        self.after(tempo, lambda: self.status_label.config(text='', background='#f5f5f5', foreground='green'))

if __name__ == '__main__':
    app = MiniEscolaApp()
    app.mainloop()

