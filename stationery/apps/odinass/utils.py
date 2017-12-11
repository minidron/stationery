from io import BytesIO
import os

from django.utils import timezone

from lxml import etree as ET

from odinass import models as odinass_models


def format_price(value):
    if not value:
        value = 0
    elif isinstance(value, str):
        value = int(float(value))
    return '{0:,}'.format(value).replace(',', ' ')


def get_text(element):
    return getattr(element, 'text', '')


def get_tag(nstag):
    start = nstag.nsmap.get(None)
    if start:
        start = len(start) + 2
    else:
        start = 0
    return nstag.tag[start:]


class ImportManager(object):
    """
    Импорт данных 1С CommerceML
    """
    def __init__(self, file_path):
        self.file_path = file_path
        filename = os.path.basename(file_path)
        log = odinass_models.Log.objects.get(filename=filename)
        try:
            if 'import' in file_path:
                self._parse({
                    'Группы': {
                        'parent': 'Классификатор',
                        'func_name': 'import_groups',
                    },
                    'ТипЦены': {
                        'parent': 'ТипыЦен',
                        'func_name': 'import_price_type',
                    },
                    'Склад': {
                        'parent': 'Склады',
                        'func_name': 'import_warehouse',
                    },
                    'Свойство': {
                        'parent': 'Свойства',
                        'func_name': 'import_property',
                    },
                    'Товар': {
                        'parent': 'Товары',
                        'func_name': 'import_product',
                    },
                })

            if 'offers' in file_path:
                self._parse({
                    'Предложение': {
                        'parent': 'Предложения',
                        'func_name': 'import_offer',
                    },
                })

            if 'prices' in file_path:
                self._parse({
                    'Предложение': {
                        'parent': 'Предложения',
                        'func_name': 'import_price',
                    },
                })

            if 'rests' in file_path:
                self._parse({
                    'Предложение': {
                        'parent': 'Предложения',
                        'func_name': 'import_rest',
                    },
                })
            log.status = odinass_models.StatusLog.FINISHED
        except Exception:
            log.status = odinass_models.StatusLog.FAILD
        log.save()

    def _parse(self, tags):
        tree = ET.iterparse(self.file_path, events=('start', 'end'))
        tree = iter(tree)
        _, root = next(tree)
        stack = [get_tag(root)]
        parents = [v['parent'] for k, v in tags.items()]
        pairs = ['%s__%s' % (v['parent'], k) for k, v in tags.items()]
        for event, node in tree:
            if event == 'start':
                stack.append(get_tag(node))
            else:
                assert event == 'end'
                stack.pop()

                if get_tag(node) in tags and stack[-1] == tags[get_tag(node)]['parent']:  # NOQA
                    getattr(self, tags[get_tag(node)]['func_name'])(node)
                    node.clear()

                if not bool(set(stack) & set(parents)):
                    node.clear()
                else:
                    path = '__'.join(stack)
                    if not any(pair in path for pair in pairs):
                        node.clear()
        root.clear()

    def import_groups(self, node):
        """
        Загрузка Групп товаров.
        """
        stack = node.findall('Группа', node.nsmap)
        while len(stack):
            item = stack.pop(0)
            if isinstance(item, tuple):
                item, parent = item
            else:
                parent = None

            odinass_models.Category.objects.update_or_create(
                id=get_text(item.find('Ид', node.nsmap)),
                defaults={
                    'title': get_text(item.find('Наименование', node.nsmap)),
                    'parent_id': (get_text(parent.find('Ид', node.nsmap))
                                  if parent is not None else None)})

            stack = [(group, item)
                     for group in item.findall('Группы/Группа',
                                               node.nsmap)] + stack

    def import_warehouse(self, node):
        """
        Загрузка Складов.
        """
        id = get_text(node.find('Ид', node.nsmap))
        title = get_text(node.find('Наименование', node.nsmap))

        instance, created = odinass_models.Warehouse.objects.update_or_create(
            id=id, defaults={'title': title})

    def import_property(self, node):
        """
        Загрузка Свойств и ВариантыЗначений.
        """
        id = get_text(node.find('Ид', node.nsmap))
        value_type = get_text(node.find('ТипЗначений', node.nsmap))
        title = get_text(node.find('Наименование', node.nsmap))

        instance, created = odinass_models.Property.objects.update_or_create(
            id=id, defaults={'title': title, 'value_type': value_type})

        value_type = 'ВариантыЗначений/%s' % value_type
        for value_option in node.findall(value_type, node.nsmap):
            v_id = get_text(value_option.find('ИдЗначения', node.nsmap))
            v_title = get_text(value_option.find('Значение', node.nsmap))
            if v_id:
                odinass_models.PropertyValue.objects.update_or_create(
                    id=v_id,
                    defaults={
                        'title': v_title,
                        'property_id': id})

    def import_product(self, node):
        """
        Загрузка Товаров.
        """
        details = node.findall(
            'ЗначенияРеквизитов/ЗначениеРеквизита/Наименование', node.nsmap)

        title = get_text(node.find('Наименование', node.nsmap))
        if not title:
            node_title = [nd for nd in details
                          if nd.text == 'Полное наименование'].pop()
            title = get_text(
                node_title.getparent().find('Значение', node.nsmap))

        id = get_text(node.find('Ид', node.nsmap))
        node_article = [nd for nd in details if nd.text == 'Код'].pop()
        article = get_text(
            node_article.getparent().find('Значение', node.nsmap))

        instance, created = odinass_models.Product.objects.update_or_create(
            id=id, defaults={'title': title, 'article': article})

        property_value = 'ЗначенияСвойств/ЗначенияСвойства'
        for value in node.findall(property_value, node.nsmap):
            pv_id = get_text(value.find('Значение', node.nsmap))
            if pv_id:
                instance.property_values.add(
                    odinass_models.PropertyValue.objects.get(
                        pk=pv_id,
                        property_id=get_text(value.find('Ид', node.nsmap))))

        for group in node.findall('Группы/Ид', node.nsmap):
            instance.categories.add(
                odinass_models.Category.objects.get(pk=get_text(group)))

    def import_offer(self, node):
        """
        Загрузка Предложений.
        """
        title = get_text(node.find('Наименование', node.nsmap))
        if not title:
            return

        ids = get_text(node.find('Ид', node.nsmap)).split('#')
        for id in ids:
            odinass_models.Offer.objects.update_or_create(
                id=id,
                defaults={
                    'title': title,
                    'product_id': ids[0]})

    def import_price_type(self, node):
        """
        Загрузка Типы Цен.
        """
        odinass_models.PriceType.objects.update_or_create(
            id=get_text(node.find('Ид', node.nsmap)),
            defaults={
                'title': get_text(node.find('Наименование', node.nsmap)),
            })

    def import_price(self, node):
        """
        Загрузка Цен предложений.
        """
        for price in node.findall('Цены/Цена', node.nsmap):
            if not get_text(price.find('ЦенаЗаЕдиницу', node.nsmap)):
                continue

            ids = get_text(node.find('Ид', node.nsmap)).split('#')
            for id in ids:
                price_type = get_text(price.find('ИдТипаЦены', node.nsmap))
                currency = get_text(price.find('Валюта', node.nsmap))
                cost = float(get_text(price.find('ЦенаЗаЕдиницу', node.nsmap)))

                odinass_models.Price.objects.update_or_create(
                    offer_id=id,
                    price_type_id=price_type,
                    defaults={
                        'currency': currency,
                        'price': cost,
                    })

    def import_rest(self, node):
        """
        Загрузка остатков.
        """
        offer_ids = get_text(node.find('Ид', node.nsmap)).split('#')
        for offer_id in offer_ids:
            for rest in node.findall('Остатки/Остаток', node.nsmap):
                warehouse_id = get_text(rest.find('Склад/Ид', node.nsmap))
                odinass_models.Rest.objects.update_or_create(
                    offer_id=offer_id,
                    warehouse_id=warehouse_id,
                    defaults={
                        'value': int(get_text(rest.find('Склад/Количество',
                                                        node.nsmap))),
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
