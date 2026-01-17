import psycopg2
from escola import inicializar_banco

def inserir_dados_mock():
    # Conectar ao banco de dados
    con = inicializar_banco()
    cur = con.cursor()
    
    # Limpar dados existentes
    cur.execute('DELETE FROM notas')
    cur.execute('DELETE FROM alunos')
    cur.execute('DELETE FROM curso_materia')
    cur.execute('DELETE FROM materias')
    cur.execute('DELETE FROM cursos')
    
    # Inserir cursos
    cursos = [
        ('Ciência da Computação',),
        ('Engenharia de Software',),
        ('Sistemas de Informação',),
        ('Análise e Desenvolvimento de Sistemas',)
    ]
    
    # Inserir cursos um por um para obter os IDs
    curso_ids = []
    for curso in cursos:
        cur.execute('INSERT INTO cursos(nome) VALUES(%s) RETURNING id', curso)
        curso_ids.append(cur.fetchone()[0])
    
    # Inserir matérias
    materias = [
        ('Programação I',),
        ('Banco de Dados',),
        ('Redes de Computadores',),
        ('Engenharia de Software',),
        ('Algoritmos',),
        ('Estrutura de Dados',),
        ('Sistemas Operacionais',),
        ('Inteligência Artificial',),
        ('Desenvolvimento Web',),
        ('Segurança da Informação',)
    ]
    
    # Inserir matérias uma por uma para obter os IDs
    materia_ids = []
    for materia in materias:
        cur.execute('INSERT INTO materias(nome) VALUES(%s) RETURNING id', materia)
        materia_ids.append(cur.fetchone()[0])
    
    # Associar matérias aos cursos
    # Ciência da Computação
    for materia_id in materia_ids[:8]:  # Todas as matérias exceto as duas últimas
        cur.execute('INSERT INTO curso_materia(curso_id, materia_id) VALUES(%s, %s)', 
                   (curso_ids[0], materia_id))
    
    # Engenharia de Software
    for materia_id in [materia_ids[0], materia_ids[1], materia_ids[3], materia_ids[4], 
                      materia_ids[5], materia_ids[8], materia_ids[9]]:
        cur.execute('INSERT INTO curso_materia(curso_id, materia_id) VALUES(%s, %s)', 
                   (curso_ids[1], materia_id))
    
    # Sistemas de Informação
    for materia_id in [materia_ids[0], materia_ids[1], materia_ids[3], materia_ids[4], 
                      materia_ids[5], materia_ids[8], materia_ids[9]]:
        cur.execute('INSERT INTO curso_materia(curso_id, materia_id) VALUES(%s, %s)', 
                   (curso_ids[2], materia_id))
    
    # Análise e Desenvolvimento de Sistemas
    for materia_id in [materia_ids[0], materia_ids[1], materia_ids[3], materia_ids[4], 
                      materia_ids[5], materia_ids[8], materia_ids[9]]:
        cur.execute('INSERT INTO curso_materia(curso_id, materia_id) VALUES(%s, %s)', 
                   (curso_ids[3], materia_id))
    
    # Inserir alunos
    alunos = [
        ('João Silva', curso_ids[0]),
        ('Maria Oliveira', curso_ids[0]),
        ('Pedro Santos', curso_ids[1]),
        ('Ana Costa', curso_ids[1]),
        ('Carlos Ferreira', curso_ids[2]),
        ('Juliana Lima', curso_ids[2]),
        ('Lucas Souza', curso_ids[3]),
        ('Fernanda Pereira', curso_ids[3])
    ]
    
    # Inserir alunos um por um para obter os IDs
    aluno_ids = []
    for aluno in alunos:
        cur.execute('INSERT INTO alunos(nome, curso_id) VALUES(%s, %s) RETURNING id', aluno)
        aluno_ids.append(cur.fetchone()[0])
    
    # Inserir notas
    # João Silva - Ciência da Computação
    notas_joao = [
        (aluno_ids[0], materia_ids[0], 4.5, 1.0, 1.0, 4.5),  # Aprovado
        (aluno_ids[0], materia_ids[1], 2.0, None, None, 3.0),  # Reprovado
        (aluno_ids[0], materia_ids[2], 3.0, 1.0, None, 2.0),  # Reprovado
        (aluno_ids[0], materia_ids[3], 4.0, None, 1.0, 4.5),  # Aprovado
        (aluno_ids[0], materia_ids[4], 5.0, 1.0, 1.0, None),  # Prova ausente
        (aluno_ids[0], materia_ids[5], None, 1.0, 1.0, 5.0),  # Trabalho ausente
        (aluno_ids[0], materia_ids[6], 4.0, None, None, None),  # Só trabalho
        (aluno_ids[0], materia_ids[7], None, None, None, 5.0)   # Só prova
    ]
    
    # Maria Oliveira - Ciência da Computação
    notas_maria = [
        (aluno_ids[1], materia_ids[0], 5.0, 1.0, 1.0, 5.0),  # Aprovado
        (aluno_ids[1], materia_ids[1], 2.0, None, 1.0, 2.0),  # Reprovado
        (aluno_ids[1], materia_ids[2], 4.0, 1.0, None, 5.0),  # Aprovado
        (aluno_ids[1], materia_ids[3], 5.0, None, None, 5.0),  # Aprovado
        (aluno_ids[1], materia_ids[4], None, 1.0, 1.0, 5.0),  # Trabalho ausente
        (aluno_ids[1], materia_ids[5], 4.5, 1.0, None, None),  # Prova ausente
        (aluno_ids[1], materia_ids[6], None, None, 1.0, 2.0),  # Reprovado
        (aluno_ids[1], materia_ids[7], 5.0, None, None, None)   # Só trabalho
    ]
    
    # Pedro Santos - Engenharia de Software
    notas_pedro = [
        (aluno_ids[2], materia_ids[0], 3.5, 1.0, 1.0, 4.5),  # Aprovado
        (aluno_ids[2], materia_ids[1], 2.0, None, 1.0, 2.0),  # Reprovado
        (aluno_ids[2], materia_ids[3], 5.0, 1.0, None, 5.0),  # Aprovado
        (aluno_ids[2], materia_ids[4], None, 1.0, 1.0, 5.0),  # Trabalho ausente
        (aluno_ids[2], materia_ids[5], 4.5, None, None, 4.5),  # Aprovado
        (aluno_ids[2], materia_ids[8], 2.0, 1.0, 1.0, 2.0),  # Reprovado
        (aluno_ids[2], materia_ids[9], None, None, None, 5.0)   # Só prova
    ]
    
    # Ana Costa - Engenharia de Software
    notas_ana = [
        (aluno_ids[3], materia_ids[0], 5.0, 1.0, 1.0, 5.0),
        (aluno_ids[3], materia_ids[1], 4.0, None, 1.0, 4.0),
        (aluno_ids[3], materia_ids[3], 5.0, 1.0, None, 5.0),
        (aluno_ids[3], materia_ids[4], None, 1.0, 1.0, 5.0),
        (aluno_ids[3], materia_ids[5], 4.5, None, None, 4.5),
        (aluno_ids[3], materia_ids[8], 5.0, 1.0, 1.0, None),
        (aluno_ids[3], materia_ids[9], None, None, None, 5.0)
    ]
    
    # Carlos Ferreira - Sistemas de Informação
    notas_carlos = [
        (aluno_ids[4], materia_ids[0], 4.0, 1.0, 1.0, 4.0),
        (aluno_ids[4], materia_ids[1], 5.0, None, 1.0, 5.0),
        (aluno_ids[4], materia_ids[3], 4.5, 1.0, None, 4.5),
        (aluno_ids[4], materia_ids[4], None, 1.0, 1.0, 5.0),
        (aluno_ids[4], materia_ids[5], 4.0, None, None, 4.0),
        (aluno_ids[4], materia_ids[8], 5.0, 1.0, 1.0, None),
        (aluno_ids[4], materia_ids[9], None, None, None, 5.0)
    ]
    
    # Juliana Lima - Sistemas de Informação
    notas_juliana = [
        (aluno_ids[5], materia_ids[0], 5.0, 1.0, 1.0, 5.0),
        (aluno_ids[5], materia_ids[1], 4.5, None, 1.0, 4.5),
        (aluno_ids[5], materia_ids[3], 4.0, 1.0, None, 5.0),
        (aluno_ids[5], materia_ids[4], None, 1.0, 1.0, 5.0),
        (aluno_ids[5], materia_ids[5], 4.5, None, None, 4.5),
        (aluno_ids[5], materia_ids[8], 5.0, 1.0, 1.0, None),
        (aluno_ids[5], materia_ids[9], None, None, None, 5.0)
    ]
    
    # Lucas Souza - Análise e Desenvolvimento de Sistemas
    notas_lucas = [
        (aluno_ids[6], materia_ids[0], 4.0, 1.0, 1.0, 4.0),
        (aluno_ids[6], materia_ids[1], 5.0, None, 1.0, 5.0),
        (aluno_ids[6], materia_ids[3], 4.5, 1.0, None, 4.5),
        (aluno_ids[6], materia_ids[4], None, 1.0, 1.0, 5.0),
        (aluno_ids[6], materia_ids[5], 4.0, None, None, 4.0),
        (aluno_ids[6], materia_ids[8], 5.0, 1.0, 1.0, None),
        (aluno_ids[6], materia_ids[9], None, None, None, 5.0)
    ]
    
    # Fernanda Pereira - Análise e Desenvolvimento de Sistemas
    notas_fernanda = [
        (aluno_ids[7], materia_ids[0], 5.0, 1.0, 1.0, 5.0),
        (aluno_ids[7], materia_ids[1], 4.5, None, 1.0, 4.5),
        (aluno_ids[7], materia_ids[3], 4.0, 1.0, None, 5.0),
        (aluno_ids[7], materia_ids[4], None, 1.0, 1.0, 5.0),
        (aluno_ids[7], materia_ids[5], 4.5, None, None, 4.5),
        (aluno_ids[7], materia_ids[8], 5.0, 1.0, 1.0, None),
        (aluno_ids[7], materia_ids[9], None, None, None, 5.0)
    ]
    
    # Inserir todas as notas
    todas_notas = (notas_joao + notas_maria + notas_pedro + notas_ana + 
                  notas_carlos + notas_juliana + notas_lucas + notas_fernanda)
    
    # Inserir notas uma por uma
    for nota in todas_notas:
        cur.execute('''
            INSERT INTO notas(aluno_id, materia_id, trabalho, simulado1, simulado2, prova) 
            VALUES(%s, %s, %s, %s, %s, %s)
        ''', nota)
    
    # Commit das alterações
    con.commit()
    con.close()
    
    print("Dados de exemplo inseridos com sucesso!")

if __name__ == '__main__':
    inserir_dados_mock() 