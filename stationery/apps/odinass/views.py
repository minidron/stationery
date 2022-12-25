import logging
import os
import time

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from rest_framework.viewsets import ReadOnlyModelViewSet

from odinass.conf import settings as odinass_settings
from odinass.models import ActionLog, Category, Log, Offer, StatusLog
from odinass.serializers import (
    SearchCategoryFilter,
    SearchCategorySerializer,
    SearchOfferFilter,
    SearchOfferSerializer
)
from odinass.tasks import import_file

logger = logging.getLogger(__name__)




@method_decorator(csrf_exempt, name='dispatch')
class ExchangeView(View):
    def __init__(self, **kwargs):
        self.routes_map = {
            ('catalog', 'checkauth'): 'catalog_checkauth',
            ('catalog', 'init'): 'catalog_init',
            ('catalog', 'file'): 'catalog_file',
            ('catalog', 'import'): 'catalog_import',
            ('catalog', 'complete'): 'catalog_complete',
        }
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        type_mode = (request.GET.get('type'), request.GET.get('mode'))

        method_name = self.routes_map.get(type_mode)
        if not method_name:
            raise Http404

        method = getattr(self, method_name, None)
        if not method:
            raise Http404

        return method(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def success(self, success_text=''):
        response = '{}\n{}'.format('success', success_text)
        return HttpResponse(response)

    def progress(self, success_text=''):
        response = '{}\n{}'.format('progress', success_text)
        return HttpResponse(response)

    def failure(self, error_text=''):
        response = '{}\n{}'.format('failure', error_text)
        return HttpResponse(response)

    def catalog_checkauth(self, request, *args, **kwargs):
        """
        Авторизация на сайте.
        """
        session = request.session
        session.create()
        response = '\n'.join([
            settings.SESSION_COOKIE_NAME,
            session.session_key,
        ])
        return self.success(response)

    def catalog_init(self, request, *args, **kwargs):
        """
        Инициализация на сайте.
        """
        response = '\n'.join([
            'zip=%s' % 'yes' if odinass_settings.USE_ZIP else 'no',
            'file_limit=%s' % odinass_settings.IMPORT_FILE_LIMIT,
            'sessid=%s' % request.session.session_key,
            'version=3.1',
        ])
        return HttpResponse(response)

    def catalog_file(self, request, *args, **kwargs):
        """
        Выгрузка файлов на сайт.
        """
        try:
            filename = os.path.basename(request.GET['filename'])
        except KeyError:
            return self.failure('Filename param required')

        if not os.path.exists(odinass_settings.UPLOAD_ROOT):
            try:
                os.makedirs(odinass_settings.UPLOAD_ROOT)
            except OSError:
                return self.failure('Can\'t create upload directory')

        temp_file = SimpleUploadedFile(filename, request.read(),
                                       content_type='text/xml')

        with open(os.path.join(odinass_settings.UPLOAD_ROOT,
                               filename), 'ab') as f:
            for chunk in temp_file.chunks():
                f.write(chunk)
        return self.success()

    def catalog_import(self, request, *args, **kwargs):
        """
        Ожидание окончания обработки данных на сайте.
        """
        try:
            filename = os.path.basename(request.GET['filename'])
        except KeyError:
            return self.failure('Filename param required')

        file_path = os.path.join(odinass_settings.UPLOAD_ROOT, filename)
        if not os.path.exists(file_path):
            return self.failure('%s doesn\'t exist' % filename)

        try:
            import_log = Log.objects.get(filename=filename)
        except Log.DoesNotExist:
            import_log = Log.objects.create(
                action=ActionLog.IMPORT, status=StatusLog.PROGRESS,
                filename=filename)
            import_file.apply_async((file_path,))

        if import_log:
            if import_log.status == StatusLog.PROGRESS:
                time.sleep(5)  # Небольшая задержка, чтоб 1С не спамил
                return self.progress()

            elif import_log.status == StatusLog.FINISHED:
                if odinass_settings.DELETE_FILES_AFTER_IMPORT:
                    try:
                        os.remove(file_path)
                    except OSError:
                        logger.error('Cant delete %s after import' % filename)
                return self.success()

            elif import_log.status == StatusLog.FAILD:
                return self.failure()

        return self.failure()

    def catalog_complete(self, request, *args, **kwargs):
        """
        Окончание обработки данных на сайте.
        """
        return self.success()


class SearchOfferViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для подсказок товаров.
    """
    filter_class = SearchOfferFilter
    queryset = Offer.objects.select_related('product').all()
    serializer_class = SearchOfferSerializer


class SearchCategoryViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для подсказок категорий.
    """
    filter_class = SearchCategoryFilter
    queryset = Category.objects.all()
    serializer_class = SearchCategorySerializer
