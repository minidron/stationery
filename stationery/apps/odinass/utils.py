from io import BytesIO

from django.utils import timezone

from xml.etree import cElementTree as ET

from odinass import models as odinass_models
from odinass.models import Category, Product, Property, PropertyValue


def get_text(element):
    return getattr(element, 'text', '')


class ImportManager(object):
    """
    Импорт данных 1С CommerceML
    """
    def __init__(self, file_path):
        self.file_path = file_path
        if 'import' in file_path:
            self._parse({
                'Группы': {
                    'parent': 'Классификатор',
                    'func_name': 'import_groups',
                },
                'Свойство': {
                    'parent': 'Свойства',
                    'func_name': 'import_property',
                },
            })
            self._parse({
                'Товар': {
                    'parent': 'Товары',
                    'func_name': 'import_product',
                },
            })
        if 'offers' in file_path:
            self._parse({
                'ТипЦены': {
                    'parent': 'ТипыЦен',
                    'func_name': 'import_price_type',
                },
            })
            self._parse({
                'Предложение': {
                    'parent': 'Предложения',
                    'func_name': 'import_offer',
                },
            })

    def _parse(self, tags):
        tree = ET.iterparse(self.file_path, events=('start', 'end'))
        tree = iter(tree)
        _, root = next(tree)
        stack = [root.tag]
        parents = [v['parent'] for k, v in tags.items()]
        pairs = ['%s__%s' % (v['parent'], k) for k, v in tags.items()]
        for event, el in tree:
            if event == 'start':
                stack.append(el.tag)
            else:
                assert event == 'end'
                stack.pop()

                if el.tag in tags and stack[-1] == tags[el.tag]['parent']:
                    getattr(self, tags[el.tag]['func_name'])(el)
                    el.clear()

                if not bool(set(stack) & set(parents)):
                    el.clear()
                else:
                    path = '__'.join(stack)
                    if not any(pair in path for pair in pairs):
                        el.clear()

        root.clear()

    def import_groups(self, node):
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

            Category.objects.update_or_create(
                id=get_text(item.find('Ид')),
                defaults={
                    'title': get_text(item.find('Наименование')),
                    'parent_id': get_text(
                        parent.find('Ид')) if parent else None,
                })

            stack = [(group, item)
                     for group in item.findall('Группы/Группа')] + stack

    def import_property(self, node):
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
                'value_type': property_item['value_type'],
            })

        for option in property_item['value_options']:
            PropertyValue.objects.update_or_create(
                id=option['id'], defaults={
                    'title': option['value'],
                    'property_id': property_item['id'],
                })

    def import_product(self, node):
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

    def import_price_type(self, node):
        """
        Загрузка Тип цены
        """
        odinass_models.PriceType.objects.update_or_create(
            id=get_text(node.find('Ид')),
            defaults={
                'title': get_text(node.find('Наименование')),
            })

    def import_offer(self, node):
        """
        Загрузка Предложения
        """
        ids = get_text(node.find('Ид')).split('#')
        if len(ids) == 2:
            prodict_id, id = ids
        else:
            prodict_id = id = ids.pop()
        odinass_models.Offer.objects.update_or_create(
            id=id,
            defaults={
                'title': get_text(node.find('Наименование')),
                'product_id': prodict_id,
            })


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
