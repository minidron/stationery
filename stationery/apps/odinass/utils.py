import os

from io import BytesIO

from django.utils import timezone

from xml.etree import cElementTree as ET

from odinass.models import Category, Product, Property, PropertyValue


def get_text(element):
    return getattr(element, 'text', '')


class ImportManager(object):
    """
    Импорт данных из 1С
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = None
        self.groups = []
        self.properties = []
        self.products = []
        self.import_all()

        for group in self.groups:
            Category.objects.update_or_create(
                id=group['id'], defaults={
                    'title': group['name'],
                    'parent_id': group['parent'],
                })

    def _get_tree(self):
        if self.tree is not None:
            return self.tree
        if not os.path.exists(self.file_path):
            message = 'File doesn\'t exist: %s' % self.file_path
            raise OSError(message)
        return ET.parse(self.file_path)

    def _parse_groups(self, node):
        """
        Загрузка Групп товаров
        """
        stack = node.findall('Группа')
        while len(stack):
            item = stack.pop(0)
            if isinstance(item, tuple):
                item, parent = item
            else:
                parent = None

            self.groups.append({
                'id': get_text(item.find('Ид')),
                'name': get_text(item.find('Наименование')),
                'parent': get_text(parent.find('Ид')) if parent else None,
            })

            stack = [(group, item)
                     for group in item.findall('Группы/Группа')] + stack

    def _parse_properties(self, node):
        """
        Загрузка Свойств и ВариантыЗначений
        """
        value_type = get_text(node.find('ТипЗначений'))
        property_item = {
            'id': get_text(node.find('Ид')),
            'name': get_text(node.find('Наименование')),
            'value_type': value_type,
        }

        value_options = []
        for value_option in node.findall(
                'ВариантыЗначений/%s' % value_type):
            value_options.append({
                'id': get_text(value_option.find('ИдЗначения')),
                'value': get_text(value_option.find('Значение')),
            })
        property_item['value_options'] = value_options

        Property.objects.update_or_create(
            id=property_item['id'], defaults={
                'title': property_item['name'],
            })

        for option in property_item['value_options']:
            PropertyValue.objects.update_or_create(
                id=option['id'], defaults={
                    'title': option['value'],
                    'property_id': property_item['id'],
                })

        return None

    def _parse_products(self, node):
        """
        Загрузка Товаров
        """
        property_values = []
        for property_node in node.findall(
                'ЗначенияСвойств/ЗначенияСвойства'):
            property_values.append({
                'id': get_text(property_node.find('Ид')),
                'value': get_text(property_node.find('Значение')),
            })

        requisite_values = []
        for requisite_node in node.findall(
                'ЗначенияРеквизитов/ЗначениеРеквизита'):
            requisite_values.append({
                'name': get_text(requisite_node.find('Наименование')),
                'value': get_text(requisite_node.find('Значение')),
            })

        instance, created = Product.objects.update_or_create(
            id=get_text(node.find('Ид')), defaults={
                'title': get_text(node.find('Наименование')),
                'article': get_text(node.find('Артикул')),
            })

        for group in [get_text(id) for id in node.findall('Группы/Ид')]:
            instance.categories.add(Category.objects.get(pk=group))

        for property_value in property_values:
            if property_value['value']:
                instance.property_values.add(PropertyValue.objects.get(
                    pk=property_value['value'],
                    property_id=property_value['id']))

        # bla = {
        #     'id': get_text(node.find('Ид')),
        #     'article': get_text(node.find('Артикул')),
        #     'name': get_text(node.find('Наименование')),
        #     'groups': [get_text(id)
        #                for id in node.findall('Группы/Ид')],
        #     'property_values': property_values,
        #     'requisite_values': requisite_values,
        # }

        return None

    def _parse_price_types(self, node):
        """
        Загрузка ТипыЦен
        """
        for price_node in node.findall('ТипыЦен/ТипЦены'):
            pass

    def _parse_offers(self, node):
        """
        Загрузка Предложения
        """
        for offer_node in node.findall('Предложения/Предложение'):
            pass

    def import_all(self):
        context = ET.iterparse(self.file_path, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)

        is_classifier = False
        is_catalog = False
        clear = True
        groups = None

        for event, el in context:
            if el.tag == 'Классификатор' and event == 'start':
                is_classifier = True
            if el.tag == 'Классификатор' and event == 'end':
                is_classifier = False

            if el.tag == 'Каталог' and event == 'start':
                is_catalog = True
            if el.tag == 'Каталог' and event == 'end':
                is_catalog = False

            if is_classifier:
                if el.tag == 'Группы' and not groups and event == 'start':
                    groups = el
                    clear = False
                elif el.tag == 'Группы' and el is groups and event == 'end':
                    groups = None
                    clear = True
                    self._parse_groups(el)

                if el.tag == 'Свойство' and event == 'start':
                    clear = False
                elif el.tag == 'Свойство' and event == 'end':
                    clear = True
                    self._parse_properties(el)

            if is_catalog:
                if el.tag == 'Товар' and event == 'start':
                    clear = False
                elif el.tag == 'Товар' and event == 'end':
                    clear = True
                    self._parse_products(el)

            if event == 'end' and clear:
                el.clear()

        root.clear()

        # self.import_offers_pack()

    def import_offers_pack(self):
        tree = self._get_tree()
        offers_pack = tree.find('ПакетПредложений')
        if offers_pack is not None:
            self._parse_price_types(offers_pack)
            self._parse_offers(offers_pack)


class ExportManager(object):
    """
    Экспорт заказов в 1С
    """
    def to_string(self, document):
        file = BytesIO()
        document.write(file, encoding='utf-8', xml_declaration=True)
        return file.getvalue().decode().encode('utf-8-sig')

    def export(self):
        tree = ET.Element('КоммерческаяИнформация')
        tree.set('ВерсияСхемы', '2.05')
        tree.set('ДатаФормирования', timezone.now().strftime('%Y-%m-%d'))

        return self.to_string(ET.ElementTree(tree))
