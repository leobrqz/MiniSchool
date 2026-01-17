import unittest
import psycopg2
from escola import MiniEscolaApp, inicializar_banco
import tkinter as tk

class TestMiniEscola(unittest.TestCase):
    _total_testes = 0  # Contador de testes
    _teste_atual = 0   # Contador do teste atual

    @classmethod
    def setUpClass(cls):
        # Conta o total de testes antes de começar
        cls._total_testes = len([m for m in dir(cls) if m.startswith('test_')])

    def setUp(self):
        TestMiniEscola._teste_atual += 1
        # Define o tamanho total desejado da linha
        tamanho_total = 80
        # Calcula quantos '=' são necessários para preencher o espaço restante
        espaco_restante = tamanho_total - len(self._testMethodName) - 4  # 4 para os espaços
        num_iguais = espaco_restante // 2
        # Cria o header com o número calculado de '='
        header = f"\n{'='*num_iguais} {self._testMethodName} {'='*num_iguais}"
        print(header)
        # Inicializa o banco de dados
        self.con = inicializar_banco()
        self.app = MiniEscolaApp()
        
        # Inicializa os widgets necessários para os testes
        self.app.painel_notas()  # Isso criará self.busca_aluno e self.filtro_curso
        self.app.painel_cursos()  # Isso criará self.busca_materia
        
        
        
        # Adiciona um curso e uma matéria para os testes
        cur = self.con.cursor()
        cur.execute('INSERT INTO cursos(nome) VALUES(%s) RETURNING id', ('Curso Teste',))
        self.curso_id = cur.fetchone()[0]
        cur.execute('INSERT INTO materias(nome) VALUES(%s) RETURNING id', ('Matéria Teste',))
        self.materia_id = cur.fetchone()[0]
        cur.execute('INSERT INTO curso_materia(curso_id, materia_id) VALUES(%s, %s)', 
                   (self.curso_id, self.materia_id))
        self.con.commit()
        print(f"Setup: Curso (ID: {self.curso_id}) e Matéria (ID: {self.materia_id}) criados")
        
        # Seleciona o curso na lista para criar o busca_materia
        self.app.lista_cursos.insert('', 'end', values=(self.curso_id, 'Curso Teste'))
        self.app.lista_cursos.selection_set(self.app.lista_cursos.get_children()[0])
        self.app.carregar_materias_curso()
        
    def tearDown(self):
        # Limpa o banco após os testes
        cur = self.con.cursor()
        cur.execute('DELETE FROM notas')
        cur.execute('DELETE FROM alunos')
        cur.execute('DELETE FROM curso_materia')
        cur.execute('DELETE FROM materias')
        cur.execute('DELETE FROM cursos')
        self.con.commit()
        self.con.close()
        self.app.destroy()
        print("="*80)
        
        # Se for o último teste, mostra a mensagem de limpeza
        if TestMiniEscola._teste_atual == TestMiniEscola._total_testes:
            print("\nBanco de dados limpo com sucesso!")

    def criar_curso_teste(self):
        """Cria um curso para testes e retorna seu ID"""
        cur = self.con.cursor()
        cur.execute('INSERT INTO cursos(nome) VALUES(%s) RETURNING id', ('Curso Teste',))
        curso_id = cur.fetchone()[0]
        self.con.commit()
        return curso_id

    def test_crud_completo_aluno(self):
        """Teste completo de operações CRUD para Alunos"""
        print("\n=== Teste CRUD Aluno ===")
        
        # 1. CREATE
        print("1. Testando criação de aluno...")
        # Teste de criação normal
        self.app.entrada_aluno.insert(0, 'Aluno Teste')
        self.app.adicionar_aluno()
        
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM alunos WHERE nome = %s', ('Aluno Teste',))
        resultado = cur.fetchone()
        self.assertIsNotNone(resultado)
        aluno_id = resultado[0]
        self.assertEqual(resultado[1], 'Aluno Teste')
        print("✅ Aluno criado com sucesso")
        
        # Teste de nome vazio
        self.app.entrada_aluno.delete(0, tk.END)
        self.app.entrada_aluno.insert(0, '')
        self.app.adicionar_aluno()
        
        cur.execute('SELECT COUNT(*) FROM alunos WHERE nome = %s', ('',))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Nome vazio rejeitado")
        
        # 2. READ
        print("\n2. Testando leitura de aluno...")
        # Teste de listagem
        self.app.carregar_alunos()
        items = self.app.lista_alunos.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Listagem de alunos funcionando")
        
        # Adiciona notas para o aluno para testar o filtro
        cur.execute('INSERT INTO notas(aluno_id, materia_id, trabalho, simulado1, simulado2, prova) VALUES(%s, %s, %s, %s, %s, %s)',
                   (aluno_id, self.materia_id, 3.0, 1.0, None, 5.0))
        self.con.commit()
        
        # Teste de filtro por nome
        self.app.busca_aluno.delete(0, tk.END)
        self.app.busca_aluno.insert(0, 'Aluno Teste')
        self.app.filtrar_notas()
        
        items = self.app.lista_notas.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Filtro por nome funcionando")
        
        # 3. DELETE
        print("\n3. Testando remoção de aluno...")
        # Limpa a lista de alunos e adiciona apenas o aluno que queremos remover
        for item in self.app.lista_alunos.get_children():
            self.app.lista_alunos.delete(item)
        self.app.lista_alunos.insert('', 'end', values=(aluno_id, 'Aluno Teste'))
        
        # Seleciona o aluno
        self.app.lista_alunos.selection_set(self.app.lista_alunos.get_children()[0])
        
        # Remove o aluno
        self.app.remover_aluno()
        
        # Verifica se o aluno foi removido
        cur.execute('SELECT id FROM alunos WHERE id = %s', (aluno_id,))
        self.assertIsNone(cur.fetchone())
        print("✅ Aluno removido com sucesso")
        
        # 4. Casos de Erro
        print("\n4. Testando casos de erro...")
        # Teste de nome muito longo
        nome_longo = 'A' * 150
        self.app.entrada_aluno.delete(0, tk.END)
        self.app.entrada_aluno.insert(0, nome_longo)
        self.app.adicionar_aluno()
        
        cur.execute('SELECT nome FROM alunos WHERE nome = %s', (nome_longo,))
        self.assertIsNone(cur.fetchone())
        print("✅ Nome longo rejeitado corretamente")

    def test_crud_completo_curso(self):
        """Teste completo de operações CRUD para Cursos"""
        print("\n=== Teste CRUD Curso ===")
        
        # 1. CREATE
        print("1. Testando criação de curso...")
        # Teste de criação normal
        self.app.entrada_curso.insert(0, 'Curso Teste')
        self.app.adicionar_curso()
        
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM cursos WHERE nome = %s', ('Curso Teste',))
        resultado = cur.fetchone()
        self.assertIsNotNone(resultado)
        curso_id = resultado[0]
        self.assertEqual(resultado[1], 'Curso Teste')
        print("✅ Curso criado com sucesso")
        
        # Teste de nome vazio
        self.app.entrada_curso.delete(0, tk.END)
        self.app.entrada_curso.insert(0, '')
        self.app.adicionar_curso()
        
        cur.execute('SELECT COUNT(*) FROM cursos WHERE nome = %s', ('',))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Nome vazio rejeitado")
        
        # 2. READ
        print("\n2. Testando leitura de curso...")
        # Teste de listagem
        self.app.carregar_cursos()
        items = self.app.lista_cursos.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Listagem de cursos funcionando")
        
        # Teste de filtro de matérias
        self.app.lista_cursos.insert('', 'end', values=(curso_id, 'Curso Teste'))
        self.app.lista_cursos.selection_set(self.app.lista_cursos.get_children()[0])
        self.app.carregar_materias_curso()
        
        # Adiciona uma matéria para testar
        cur.execute('INSERT INTO materias(nome) VALUES(%s) RETURNING id', ('Matéria Teste',))
        materia_id = cur.fetchone()[0]
        self.con.commit()
        
        # Testa toggle de matéria
        self.app.toggle_materia(curso_id, materia_id, 1)
        cur.execute('SELECT 1 FROM curso_materia WHERE curso_id = %s AND materia_id = %s', (curso_id, materia_id))
        self.assertIsNotNone(cur.fetchone())
        print("✅ Matéria adicionada ao curso")
        
        # 3. DELETE
        print("\n3. Testando remoção de curso...")
        # Limpa a lista de cursos e adiciona apenas o curso que queremos remover
        for item in self.app.lista_cursos.get_children():
            self.app.lista_cursos.delete(item)
        self.app.lista_cursos.insert('', 'end', values=(curso_id, 'Curso Teste'))
        
        # Seleciona o curso
        self.app.lista_cursos.selection_set(self.app.lista_cursos.get_children()[0])
        
        # Remove o curso
        self.app.remover_curso()
        
        # Verifica se o curso foi removido
        cur.execute('SELECT id FROM cursos WHERE id = %s', (curso_id,))
        self.assertIsNone(cur.fetchone())
        print("✅ Curso removido com sucesso")
        
        # Teste de remoção com alunos
        # Cria novo curso
        curso_id = self.criar_curso_teste()
        
        # Adiciona aluno ao curso
        cur.execute('INSERT INTO alunos(nome, curso_id) VALUES(%s, %s) RETURNING id', ('Aluno Teste', curso_id))
        aluno_id = cur.fetchone()[0]
        self.con.commit()
        
        # Limpa a lista de cursos e adiciona apenas o curso que queremos remover
        for item in self.app.lista_cursos.get_children():
            self.app.lista_cursos.delete(item)
        self.app.lista_cursos.insert('', 'end', values=(curso_id, 'Curso Teste'))
        
        # Seleciona o curso
        self.app.lista_cursos.selection_set(self.app.lista_cursos.get_children()[0])
        
        # Remove o curso
        self.app.remover_curso()
        
        # Verifica se o aluno ficou sem curso (curso_id = NULL)
        cur.execute('SELECT curso_id FROM alunos WHERE id = %s', (aluno_id,))
        resultado = cur.fetchone()
        self.assertIsNotNone(resultado)
        self.assertIsNone(resultado[0])
        print("✅ Aluno ficou sem curso (curso_id = NULL)")
        
        # Verifica se as notas do aluno foram removidas
        cur.execute('SELECT COUNT(*) FROM notas WHERE aluno_id = %s', (aluno_id,))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Notas do aluno foram removidas")
        
        # 4. Casos de Erro
        print("\n4. Testando casos de erro...")
        # Teste de nome muito longo
        nome_longo = 'A' * 150
        self.app.entrada_curso.delete(0, tk.END)
        self.app.entrada_curso.insert(0, nome_longo)
        self.app.adicionar_curso()
        
        cur.execute('SELECT nome FROM cursos WHERE nome = %s', (nome_longo,))
        self.assertIsNone(cur.fetchone())
        print("✅ Nome longo rejeitado")

    def test_crud_completo_materia(self):
        """Teste completo de operações CRUD para Matérias"""
        print("\n=== Teste CRUD Matéria ===")
        
        # 1. CREATE
        print("1. Testando criação de matéria...")
        # Teste de criação normal
        self.app.entrada_mat.insert(0, 'Matéria Teste')
        self.app.adicionar_materia()
        
        cur = self.con.cursor()
        cur.execute('SELECT id, nome FROM materias WHERE nome = %s', ('Matéria Teste',))
        resultado = cur.fetchone()
        self.assertIsNotNone(resultado)
        materia_id = resultado[0]
        self.assertEqual(resultado[1], 'Matéria Teste')
        print("✅ Matéria criada com sucesso")
        
        # Teste de nome vazio
        self.app.entrada_mat.delete(0, tk.END)
        self.app.entrada_mat.insert(0, '')
        self.app.adicionar_materia()
        
        cur.execute('SELECT COUNT(*) FROM materias WHERE nome = %s', ('',))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Nome vazio rejeitado")
        
        # 2. READ
        print("\n2. Testando leitura de matéria...")
        # Teste de listagem
        self.app.carregar_materias()
        items = self.app.lista_materias.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Listagem de matérias funcionando")
        
        # Teste de filtro por nome
        self.app.busca_materia.delete(0, tk.END)
        self.app.busca_materia.insert(0, 'Teste')
        self.app.filtrar_materias_curso(self.curso_id, set())
        
        items = self.app.lista_materias.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Filtro por nome funcionando")
        
        # 3. DELETE
        print("\n3. Testando remoção de matéria...")
        # Limpa a lista de matérias e adiciona apenas a matéria que queremos remover
        for item in self.app.lista_materias.get_children():
            self.app.lista_materias.delete(item)
        self.app.lista_materias.insert('', 'end', values=(materia_id, 'Matéria Teste'))
        
        # Seleciona a matéria
        self.app.lista_materias.selection_set(self.app.lista_materias.get_children()[0])
        
        # Remove a matéria
        self.app.remover_materia()
        
        # Verifica se a matéria foi removida
        cur.execute('SELECT id FROM materias WHERE id = %s', (materia_id,))
        self.assertIsNone(cur.fetchone())
        print("✅ Matéria removida com sucesso")
        
        # Teste de remoção com notas
        # Cria nova matéria
        cur.execute('INSERT INTO materias(nome) VALUES(%s) RETURNING id', ('Matéria Teste',))
        materia_id = cur.fetchone()[0]
        
        # Cria aluno e curso para teste
        cur.execute('INSERT INTO cursos(nome) VALUES(%s) RETURNING id', ('Curso Teste',))
        curso_id = cur.fetchone()[0]
        cur.execute('INSERT INTO alunos(nome, curso_id) VALUES(%s, %s) RETURNING id', ('Aluno Teste', curso_id))
        aluno_id = cur.fetchone()[0]
        
        # Adiciona nota para a matéria
        cur.execute('INSERT INTO notas(aluno_id, materia_id, trabalho, simulado1, simulado2, prova) VALUES(%s, %s, %s, %s, %s, %s)',
                   (aluno_id, materia_id, 2.0, None, 1.0, 4.0))
        self.con.commit()
        
        # Limpa a lista de matérias e adiciona apenas a matéria que queremos remover
        for item in self.app.lista_materias.get_children():
            self.app.lista_materias.delete(item)
        self.app.lista_materias.insert('', 'end', values=(materia_id, 'Matéria Teste'))
        
        # Seleciona a matéria
        self.app.lista_materias.selection_set(self.app.lista_materias.get_children()[0])
        
        # Remove a matéria
        self.app.remover_materia()
        
        # Verifica se a matéria foi removida
        cur.execute('SELECT id FROM materias WHERE id = %s', (materia_id,))
        self.assertIsNone(cur.fetchone())
        print("✅ Matéria removida com sucesso")
        
        # Verifica se as notas foram removidas
        cur.execute('SELECT COUNT(*) FROM notas WHERE materia_id = %s', (materia_id,))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Notas da matéria foram removidas")
        
        # 4. Casos de Erro
        print("\n4. Testando casos de erro...")
        # Teste de nome muito longo
        nome_longo = 'A' * 150
        self.app.entrada_mat.delete(0, tk.END)
        self.app.entrada_mat.insert(0, nome_longo)
        self.app.adicionar_materia()
        
        cur.execute('SELECT nome FROM materias WHERE nome = %s', (nome_longo,))
        self.assertIsNone(cur.fetchone())
        print("✅ Nome longo rejeitado")

    def test_crud_completo_notas(self):
        """Teste completo de operações CRUD para Notas"""
        print("\n=== Teste CRUD Notas ===")
        
        # 1. CREATE
        print("1. Testando criação de notas...")
        # Cria aluno para teste
        self.app.entrada_aluno.insert(0, 'Aluno Notas Teste')
        # Seleciona o curso no combo de cursos
        self.app.combo_cursos.set(f"{self.curso_id}: Curso Teste")
        self.app.adicionar_aluno()
        
        cur = self.con.cursor()
        cur.execute('SELECT id FROM alunos WHERE nome = %s', ('Aluno Notas Teste',))
        aluno_id = cur.fetchone()[0]
        
        # Verifica se o aluno foi criado com o curso correto
        cur.execute('SELECT curso_id FROM alunos WHERE id = %s', (aluno_id,))
        self.assertEqual(cur.fetchone()[0], self.curso_id)
        print("✅ Aluno criado com curso corretamente")
        
        # Seleciona aluno no combo
        self.app.combo_aluno.set(f"{aluno_id}: Aluno Notas Teste")
        self.app.atualizar_materias_aluno()
        
        # Seleciona matéria no combo
        self.app.combo_mat.set(f"{self.materia_id}: Matéria Teste")
        
        # Adiciona notas
        self.app.entrada_trabalho.insert(0, '3.0')
        self.app.entrada_sim1.insert(0, '1.0')
        self.app.entrada_sim2.insert(0, '')
        self.app.entrada_prova.insert(0, '5.0')
        self.app.adicionar_nota()
        
        # Verifica se as notas foram salvas
        cur.execute('SELECT trabalho, simulado1, simulado2, prova FROM notas WHERE aluno_id = %s AND materia_id = %s',
                   (aluno_id, self.materia_id))
        resultado = cur.fetchone()
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado[0], 3.0)
        self.assertEqual(resultado[1], 1.0)
        self.assertIsNone(resultado[2])
        self.assertEqual(resultado[3], 5.0)
        print("✅ Notas criadas com sucesso")
        
        # 2. READ
        print("\n2. Testando leitura e filtros...")
        # Teste de listagem
        self.app.filtrar_notas()
        items = self.app.lista_notas.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Listagem de notas funcionando")
        
        # Teste de filtro por nome
        self.app.busca_aluno.delete(0, tk.END)
        self.app.busca_aluno.insert(0, 'Aluno Notas Teste')
        self.app.filtrar_notas()
        
        items = self.app.lista_notas.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Filtro por nome funcionando")
        
        # Teste de filtro por curso
        self.app.filtro_curso.set('Curso Teste')
        self.app.filtrar_notas()
        
        items = self.app.lista_notas.get_children()
        self.assertGreater(len(items), 0)
        print("✅ Filtro por curso funcionando")
        
        # 3. DELETE
        print("\n3. Testando remoção de notas...")
        # Seleciona aluno e matéria
        self.app.combo_aluno.set(f"{aluno_id}: Aluno Notas Teste")
        self.app.combo_mat.set(f"{self.materia_id}: Matéria Teste")
        
        # Remove as notas
        self.app.remover_notas()
        
        # Verifica se as notas foram removidas
        cur.execute('SELECT COUNT(*) FROM notas WHERE aluno_id = %s AND materia_id = %s',
                   (aluno_id, self.materia_id))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Notas removidas com sucesso")
        
        # 4. Casos de Erro
        print("\n4. Testando casos de erro...")
        # Teste de notas inválidas
        self.app.entrada_trabalho.insert(0, '-1')
        self.app.entrada_sim1.insert(0, '2')
        self.app.entrada_sim2.insert(0, 'abc')
        self.app.entrada_prova.insert(0, '11')
        self.app.adicionar_nota()
        
        cur.execute('SELECT COUNT(*) FROM notas WHERE aluno_id = %s AND materia_id = %s',
                   (aluno_id, self.materia_id))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Notas inválidas rejeitadas")
        
        # Limpa campos
        self.app.entrada_trabalho.delete(0, tk.END)
        self.app.entrada_sim1.delete(0, tk.END)
        self.app.entrada_sim2.delete(0, tk.END)
        self.app.entrada_prova.delete(0, tk.END)
        
        # Teste sem aluno selecionado
        self.app.combo_aluno.set('')
        self.app.adicionar_nota()
        
        cur.execute('SELECT COUNT(*) FROM notas WHERE aluno_id = %s AND materia_id = %s',
                   (aluno_id, self.materia_id))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Erro sem aluno selecionado")
        
        # Teste sem matéria selecionada
        self.app.combo_aluno.set(f"{aluno_id}: Aluno Notas Teste")
        self.app.combo_mat.set('')
        self.app.adicionar_nota()
        
        cur.execute('SELECT COUNT(*) FROM notas WHERE aluno_id = %s AND materia_id = %s',
                   (aluno_id, self.materia_id))
        self.assertEqual(cur.fetchone()[0], 0)
        print("✅ Erro sem matéria selecionada")

if __name__ == '__main__':
    unittest.main() 