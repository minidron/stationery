from fabric_class import DjangoFabric, add_class_methods_as_functions


class Fabric(DjangoFabric):
    app_name = 'stationery'
    host = '85.143.175.229'
    local_db_name = 'stationery'
    remote_db_name = 'stationery_db'
    repository = 'git@github.com:minidron/stationery.git'
    use_bower = True
    user = 'mini'


__all__ = add_class_methods_as_functions(Fabric(), __name__)
