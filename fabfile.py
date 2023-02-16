from fabric.api import local, sudo
from fabric_class import DjangoFabric, add_class_methods_as_functions


class Fabric(DjangoFabric):
    app_name = 'stationery'
    host = '85.143.175.229'
    local_db_name = 'stationery_db'
    remote_db_name = 'stationery_db'
    repository = 'git@github.com:minidron/stationery.git'
    use_bower = True
    user = 'mini'
    vue_app_path = 'kancmir'

    def fab_deploy(self):
        """
        Дополнительные действия для проекта при деплои.
        """
        super().fab_deploy()
        sudo('supervisorctl restart stationery-celery')

    def fab_vue_serve(self):
        """
        Запустить dev сброку VUE приложения с watch.
        """
        local('yarn --cwd %s serve' % self.vue_app_path)

    def fab_vue_build(self):
        """
        Сделать билд VUE приложения.
        """
        local('yarn --cwd %s build' % self.vue_app_path)


__all__ = add_class_methods_as_functions(Fabric(), __name__)
