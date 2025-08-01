#싱글톤 객체 생성
# class Singleton:
#     __instance = None

#     @classmethod
#     def __getInstance(cls):
#         return cls.__instance

#     @classmethod
#     def instance(cls, *args, **kargs):
#         cls.__instance = cls(*args, **kargs)
#         cls.instance = cls.__getInstance
#         return cls.__instance


class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]
