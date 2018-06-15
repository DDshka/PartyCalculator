class Service():
    model = None

    def get(self, **kwargs) -> model:
        return self.model.objects.get(**kwargs)

    def get_all(self, excluding=None):
        if excluding:
            return  self.model.objects.exclude(**excluding)

        return self.model.objects.all()

    def filter(self, **kwargs):
        return self.model.objects.filter(**kwargs)

    def create(self, **kwargs) -> model:
        return self.model.objects.create(**kwargs)

    def create_nosave(self, **kwargs) -> model:
        return self.model(**kwargs)

    def delete(self, obj: model):
        obj.delete()
