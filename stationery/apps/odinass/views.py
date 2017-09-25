import logging
import os
import time

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from celery.result import AsyncResult

from odinass.conf import settings as odinass_settings
from odinass.tasks import import_file
from odinass.utils import ExportManager


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ExchangeView(View):
    def __init__(self, **kwargs):
        self.routes_map = {
            ('catalog', 'checkauth'): 'check_auth',
            ('catalog', 'file'): 'upload_file',
            ('catalog', 'import'): 'import_file',
            ('catalog', 'init'): 'init',
            ('sale', 'checkauth'): 'check_auth',
            ('sale', 'file'): 'fake_upload_file',
            ('sale', 'init'): 'sale_init',
            ('sale', 'query'): 'export_query',
            ('sale', 'success'): 'export_success',
            # ('import', 'import'): import_file,
        }
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        method_name = self.routes_map.get((request.GET.get('type'),
                                           request.GET.get('mode')))
        if not method_name:
            raise Http404

        method = getattr(self, method_name, None)
        if not method:
            raise Http404

        return method(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def success(self, success_text=''):
        result = '{}\n{}'.format('success', success_text)
        return HttpResponse(result)

    def progress(self, success_text=''):
        result = '{}\n{}'.format('progress', success_text)
        return HttpResponse(result)

    def error(self, error_text=''):
        result = '{}\n{}'.format('failure', error_text)
        return HttpResponse(result)

    def check_auth(self, request, *args, **kwargs):
        """
        Создание сессии.
        """
        session = request.session
        session.create()
        success_text = '{}\n{}'.format(settings.SESSION_COOKIE_NAME,
                                       session.session_key)
        return self.success(success_text)

    def init(self, request, *args, **kwargs):
        """
        Настройки импорта.
        """
        result = 'zip={}\nfile_limit={}'.format(
            'yes' if odinass_settings.USE_ZIP else 'no',
            odinass_settings.IMPORT_FILE_LIMIT)
        return HttpResponse(result)

    def sale_init(self, request, *args, **kwargs):
        """
        Настройки экспорта.
        """
        result = 'zip={}\nfile_limit={}'.format(
            'yes' if odinass_settings.USE_ZIP else 'no',
            odinass_settings.EXPORT_FILE_LIMIT)
        return HttpResponse(result)

    def upload_file(self, request, *args, **kwargs):
        """
        Загрузка файлов на сервер.
        """
        try:
            filename = os.path.basename(request.GET['filename'])
        except KeyError:
            return self.error('Filename param required')

        if not os.path.exists(odinass_settings.UPLOAD_ROOT):
            try:
                os.makedirs(odinass_settings.UPLOAD_ROOT)
            except OSError:
                return self.error('Can\'t create upload directory')

        filename = '%s_%s%s' % (filename[:-4], request.session.session_key,
                                filename[-4:])

        temp_file = SimpleUploadedFile(filename, request.read(),
                                       content_type='text/xml')

        with open(os.path.join(odinass_settings.UPLOAD_ROOT,
                               filename), 'ab') as f:
            for chunk in temp_file.chunks():
                f.write(chunk)
        return self.success()

    def import_file(self, request, *args, **kwargs):
        """
        Импорт ранее загруженных файлов.
        """
        try:
            filename = os.path.basename(request.GET['filename'])
        except KeyError:
            return self.error('Filename param required')

        filename = '%s_%s%s' % (filename[:-4], request.session.session_key,
                                filename[-4:])

        file_path = os.path.join(odinass_settings.UPLOAD_ROOT, filename)
        if not os.path.exists(file_path):
            return self.error('%s doesn\'t exist' % filename)

        if AsyncResult(filename).state == 'PENDING':
            import_file.apply_async((file_path,), task_id=filename)

        if AsyncResult(filename).state in ['PENDING', 'STARTED']:
            time.sleep(5)  # Небольшая задержка с ответом, чтоб 1С не спамил
            return self.progress()

        if odinass_settings.DELETE_FILES_AFTER_IMPORT:
            try:
                os.remove(file_path)
            except OSError:
                logger.error('Can\'t delete %s after import' % filename)
        return self.success()

    def export_query(self, request, *args, **kwargs):
        """
        Экспорт изменений.
        """
        export_manager = ExportManager()
        return HttpResponse(export_manager.export(), content_type='text/xml')

    def export_success(self, request, *args, **kwargs):
        return self.success()

    def fake_upload_file(self, request, *args, **kwargs):
        """
        Нам не нужны заказы из 1С.
        """
        return self.success()
