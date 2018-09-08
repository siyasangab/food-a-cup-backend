class ServiceBase():
    '''
        Base service class for django projects
        \r\n
        Usage: 
                #import ServiceBase

                class MyRepo(ServiceBase):
                    def __init__(self):
                        super(MyRepo, self).__init__(DjangoModel)
    '''
    def __init__(self, model):
        self.model = model

    def get_fields(self, field_list, **kwargs):
        '''
            Use when you want specific model fields\r\n
            Example:
                Assumming we initialised this class (self) with a django model 
                consisting of name, cellphone, email, address and we want only
                cellphone and email for object with id 2. We can do this:

                result = self.get_fields(field_list = 'cellphone, email', **{
                    'id': 2
                })

                return result
                
        '''

        values = self.model.objects.filter(**kwargs).values(*field_list)
        return values
