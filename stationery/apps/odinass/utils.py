import os
import re
import traceback

from io import BytesIO

from django.db import IntegrityError
from django.utils import timezone

from lxml import etree as ET

from mptt.exceptions import InvalidMove

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
    def __init__(self, file_path, logging=False):
        self.file_path = file_path
        filename = os.path.basename(file_path)
        if logging:
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

            if logging:
                log.status = odinass_models.StatusLog.FINISHED
        except Exception as e:
            if logging:
                log.status = odinass_models.StatusLog.FAILD
                log.traceback = traceback.format_exc()
            else:
                raise e
        if logging:
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

            defaults = {
                'parent_id': (get_text(parent.find('Ид', node.nsmap))
                              if parent is not None else None)}

            title = get_text(item.find('Наименование', node.nsmap))
            order_raw = re.match(r'^\d+\.?', title)
            if order_raw:
                title = title[order_raw.end():]
                order = re.findall(r'\d+', order_raw.group())[0]
                defaults['order'] = int(order)
            defaults['title'] = title

            error = 0
            id = get_text(item.find('Ид', node.nsmap))
            try:
                if not get_text(item.find('ПометкаУдаления',
                                          node.nsmap)) == 'true':
                    odinass_models.Category.objects.update_or_create(
                        id=id,
                        defaults=defaults)
                else:
                    odinass_models.Category.objects.filter(id=id).delete()
            except InvalidMove:
                error = 1

            stack = [(group, item)
                     for group in item.findall('Группы/Группа',
                                               node.nsmap)] + stack
        if error:
            self.import_groups(node)

    def import_warehouse(self, node):
        """
        Загрузка Складов.
        """
        id = get_text(node.find('Ид', node.nsmap))
        title = get_text(node.find('Наименование', node.nsmap))

        if not get_text(node.find('ПометкаУдаления', node.nsmap)) == 'true':
            instance, _ = odinass_models.Warehouse.objects.update_or_create(
                id=id, defaults={'title': title})
        else:
            odinass_models.Warehouse.objects.filter(id=id).delete()

    def import_property(self, node):
        """
        Загрузка Свойств и ВариантыЗначений.
        """
        id = get_text(node.find('Ид', node.nsmap))
        value_type = get_text(node.find('ТипЗначений', node.nsmap))
        title = get_text(node.find('Наименование', node.nsmap))

        if not get_text(node.find('ПометкаУдаления', node.nsmap)) == 'true':
            instance, _ = odinass_models.Property.objects.update_or_create(
                id=id, defaults={'title': title, 'value_type': value_type})
        else:
            odinass_models.Property.objects.filter(id=id).delete()
            return

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
        node_title = [nd for nd in details
                      if nd.text == 'Полное наименование'].pop()
        title = get_text(node_title.getparent().find('Значение', node.nsmap))
        if not title or len(title) <= 2:
            return

        id = get_text(node.find('Ид', node.nsmap))
        node_article = [nd for nd in details if nd.text == 'Код'].pop()
        article = get_text(
            node_article.getparent().find('Значение', node.nsmap))

        groups = []
        for group in node.findall('Группы/Ид', node.nsmap):
            try:
                groups.append(
                    odinass_models.Category.objects.get(pk=get_text(group)))
            except odinass_models.Category.DoesNotExist:
                pass
        if not groups:
            odinass_models.Product.objects.filter(id=id).delete()
            return

        instance = None
        if not get_text(node.find('ПометкаУдаления', node.nsmap)) == 'true':
            instance, _ = odinass_models.Product.objects.update_or_create(
                id=id, defaults={'title': title, 'article': article})
        else:
            odinass_models.Product.objects.filter(id=id).delete()

        if instance:
            property_value = 'ЗначенияСвойств/ЗначенияСвойства'
            for value in node.findall(property_value, node.nsmap):
                pv_id = get_text(value.find('Значение', node.nsmap))
                if pv_id:
                    try:
                        instance.property_values.add(
                            odinass_models.PropertyValue.objects.get(
                                pk=pv_id,
                                property_id=get_text(value.find('Ид',
                                                                node.nsmap)))
                        )
                    except odinass_models.PropertyValue.DoesNotExist:
                        pass

            for group in groups:
                instance.category = group
                instance.save()

    def import_offer(self, node):
        """
        Загрузка Предложений.
        """
        title = get_text(node.find('Наименование', node.nsmap))
        if not title or len(title) <= 2:
            return

        ids = get_text(node.find('Ид', node.nsmap)).split('#')
        try:
            product = odinass_models.Product.objects.get(pk=ids[0])
        except odinass_models.Product.DoesNotExist:
            return

        for id in ids:
            if not get_text(node.find('ПометкаУдаления',
                                      node.nsmap)) == 'true':
                odinass_models.Offer.objects.update_or_create(
                    id=id,
                    defaults={
                        'title': title,
                        'product': product})
            else:
                odinass_models.Offer.objects.filter(id=id).delete()

    def import_price_type(self, node):
        """
        Загрузка Типы Цен.
        """
        id = get_text(node.find('Ид', node.nsmap))
        if not get_text(node.find('ПометкаУдаления', node.nsmap)) == 'true':
            odinass_models.PriceType.objects.update_or_create(
                id=id,
                defaults={
                    'title': get_text(node.find('Наименование', node.nsmap)),
                })
        else:
            odinass_models.PriceType.objects.filter(id=id).delete()

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

                try:
                    if not get_text(price.find('ПометкаУдаления',
                                               node.nsmap)) == 'true':
                        odinass_models.Price.objects.update_or_create(
                            offer_id=id,
                            price_type_id=price_type,
                            defaults={
                                'currency': currency,
                                'price': cost,
                            })
                    else:
                        odinass_models.Price.objects.filters(
                            offer_id=id).delete()
                except IntegrityError:
                    pass

    def import_rest(self, node):
        """
        Загрузка остатков.
        """
        offer_ids = get_text(node.find('Ид', node.nsmap)).split('#')
        for offer_id in offer_ids:
            for rest in node.findall('Остатки/Остаток', node.nsmap):
                warehouse_id = get_text(rest.find('Склад/Ид', node.nsmap))
                try:
                    if not get_text(rest.find('ПометкаУдаления',
                                              node.nsmap)) == 'true':
                        odinass_models.Rest.objects.update_or_create(
                            offer_id=offer_id,
                            warehouse_id=warehouse_id,
                            defaults={
                                'value': int(float(get_text(
                                    rest.find('Склад/Количество',
                                              node.nsmap)))),
                            })
                    else:
                        odinass_models.Rest.objects.filter(
                            offer_id=offer_id).delete()
                except IntegrityError:
                    pass


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
