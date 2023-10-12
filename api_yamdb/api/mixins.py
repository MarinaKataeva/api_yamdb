from rest_framework import mixins, viewsets


class CreateListDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
        Специальный вьюсет, разрешающий:
        - получение списка объектов,
        - создание объекта,
        - удаление объекта
    """
    pass
