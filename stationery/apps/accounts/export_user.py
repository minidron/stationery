from io import BytesIO

from django.core.files.storage import FileSystemStorage

import xlsxwriter


class XlsxUserExport:
    """
    Список пользователей в формате xlsx.
    """
    fields = {
        '': ['username'],
        'Имя': ['first_name'],
        'Фамилия': ['last_name'],
        'Оптовик': 'is_opt',
        'Тип цены': ['profile', 'price_type', 'title'],
        'Компания': ['profile', 'company'],
        'Юридический адрес': ['profile', 'company_address'],
        'ИНН': ['profile', 'inn'],
        'Телефон': ['profile', 'phone'],
    }

    def __init__(self, user_list):
        self.user_list = user_list or []
        self.row = 0

    def _fill_headers(self, worksheet):
        """
        Проставляем заголовки.
        """
        for col, title in enumerate(self.fields):
            worksheet.write_string(self.row, col, title)

        self.row += 1

    def _is_opt(self, user):
        """
        Оптовик пользователь или нет.
        """
        if user.groups.filter(name='Оптовик').exists():
            return 'Да'
        else:
            return 'Нет'

    def _fill_data(self, worksheet):
        """
        Проставляем заголовки.
        """
        for user in self.user_list:
            for col, field_path in enumerate(self.fields.values()):
                if field_path == 'is_opt':
                    value = self._is_opt(user)
                else:
                    value = user
                    for field in field_path:
                        try:
                            value = getattr(value, field)
                        except AttributeError:
                            value = ''
                worksheet.write_string(self.row, col, value or '')

            self.row += 1

    def generate(self):
        """
        Создание файла.
        """
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        self._fill_headers(worksheet)
        self._fill_data(worksheet)

        workbook.close()
        output.seek(0)
        fs = FileSystemStorage()
        fs.save('users.xlsx', output)
