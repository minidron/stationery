from stationery.apps.fabric_utils.fabric_class import (
    add_class_methods_as_functions,
    DjangoFabric
)


class Fabric(DjangoFabric):
    host = '85.143.175.229'
    app_name = 'stationery'
    repository = 'git@github.com:minidron/stationery.git'
    remote_db_name = 'stationery_db'
    local_db_name = 'stationery'
    use_bower = True


__all__ = add_class_methods_as_functions(Fabric(), __name__)
