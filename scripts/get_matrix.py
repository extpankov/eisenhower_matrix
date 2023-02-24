from prettytable import PrettyTable

async def get_matrix(user_id):
    # db.get ... 
    table1 = PrettyTable()
    table1.field_names(['Важно и срочно', 'Важно и не срочно'])
    table1.header = False
