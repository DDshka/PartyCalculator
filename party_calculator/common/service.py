class Service():
    model = None

    def get(self, **kwargs) -> model:
        return self.model.objects.get(**kwargs)

    def get_all(self, excluding=None):
        if excluding:
            return  self.model.objects.exclude(**excluding)

        return self.model.objects.all()

    def create(self, **kwargs) -> model:
        return self.model.objects.create(**kwargs)

    def delete(self, model_obj):
        model_obj.delete()
