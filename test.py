from prettytable import PrettyTable

table = PrettyTable()

table.field_names = ['Важно и срочно', 'Важно и не срочно']
table.add_row(['1. 123213213', '1. 123123123'])
table.add_row(['2. 123213213', ''])
table.format = True

print(table.get_html_string())


# table.field_names = ['Не важно и срочно', 'Не важно и не срочно']
# table.add_row(['1. 123213213', '1. 123123123'])
# table.add_row(['2. 123213213', ''])
# table.padding_width = 1