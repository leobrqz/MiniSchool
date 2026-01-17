import psycopg2

def drop_all_tables():
    con = psycopg2.connect(dbname='escola', user='postgres', password='quack', host='localhost')
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS notas CASCADE;')
    cur.execute('DROP TABLE IF EXISTS alunos CASCADE;')
    cur.execute('DROP TABLE IF EXISTS curso_materia CASCADE;')
    cur.execute('DROP TABLE IF EXISTS materias CASCADE;')
    cur.execute('DROP TABLE IF EXISTS cursos CASCADE;')
    con.commit()
    con.close()
    print('Todas as tabelas foram removidas com sucesso!')

if __name__ == '__main__':
    drop_all_tables() 