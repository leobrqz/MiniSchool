# MiniSchool - Sistema de Gerenciamento Escolar

Sistema desktop desenvolvido em Python para gerenciamento de cursos, matérias, alunos e notas. O software oferece uma interface intuitiva para controle acadêmico completo, permitindo cadastro, edição e visualização de informações escolares de forma organizada e eficiente.

## 🛠️ Stack

- **Tkinter**: Framework para interface gráfica desktop
- **PostgreSQL**: Banco de dados relacional
- **Psycopg2**: Driver para conexão com PostgreSQL

## 🎯 Objetivos

- Desenvolver um sistema de gestão escolar desktop usando Python para controle acadêmico
- Disponibilizar uma interface de fácil acesso para gerenciar cursos, matérias, alunos e notas
- Integrar um sistema de gestão completo que ofereça cadastro, edição e remoção de entidades
- Suportar conexão com banco de dados PostgreSQL

## Funcionalidades Principais

### 🎨 Interface

A interface foi desenvolvida utilizando Tkinter, organizada em uma estrutura de abas que separa as funcionalidades principais do sistema:

- **Navegação Principal**: Abas para Cursos, Matérias, Alunos e Notas
- **Painéis Laterais**: Formulários para entrada de dados e seleção de registros
- **Listagens Interativas**: Tabelas e árvores hierárquicas para visualização de dados
- **Filtros e Buscas**: Campos de busca para localização rápida de informações
- **Feedback Visual**: Mensagens de status para operações realizadas

### 📚 Gestão

Gerenciamento completo de entidades através de formulários e listagens:

- **Cursos**: Cadastro, edição e exclusão de cursos. Associação de matérias aos cursos através de checkboxes interativos com busca.
- **Matérias**: Cadastro, edição e exclusão de matérias. Listagem completa de todas as matérias disponíveis.
- **Alunos**: Cadastro completo (nome e curso), edição e exclusão. Vinculação de alunos aos cursos.
- **Notas**: Registro de notas por componente (Prova, Trabalho, Simulado 1, Simulado 2). Cálculo automático da nota final. Visualização hierárquica por aluno e matéria. Filtros por nome do aluno e curso.

### 📊 Sistema de Notas

Sistema completo de avaliação acadêmica:

- **Componentes de Avaliação**: Prova (0-5, obrigatória), Trabalho (0-5, obrigatório), Simulados (0-1, opcionais)
- **Cálculo Automático**: Nota final = Prova + Trabalho + Simulado 1 + Simulado 2 (máximo 10,0)
- **Status de Aprovação**: Cálculo automático de aprovação (nota mínima 6,0) ou reprovação
- **Validações**: Verificação de limites de notas e integridade dos dados
- **Visualização**: Lista hierárquica agrupada por aluno, mostrando todas as matérias e respectivas notas

## ⚙️ Setup

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

1. Crie um banco de dados PostgreSQL chamado `escola`:
```sql
CREATE DATABASE escola;
```

2. Edite as credenciais de conexão no arquivo `src/escola.py` (linhas 8-10):
```python
con = psycopg2.connect(
    dbname='escola',
    user='postgres',
    password='sua_senha_aqui',
    host='localhost'
)
```

### 3. Gerar Dados de Exemplo (Opcional)

Para popular o banco com dados de exemplo:
```bash
python src/mock.py
```

Este script criará:
- Cursos de exemplo (Ciência da Computação, Engenharia de Software, etc.)
- Matérias relacionadas aos cursos
- Alunos vinculados aos cursos
- Histórico de notas para os alunos

### 4. Executar a Aplicação

```bash
python src/escola.py
```

##  Scripts Auxiliares

### Remover Todas as Tabelas

Para limpar completamente o banco de dados:
```bash
python src/drop_all.py
```

