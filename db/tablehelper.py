from prettytable import PrettyTable

class TableHelper(type):
    """
        生成表格的类。

    """
    def __new__(cls, name, bases, attrs):
        """
            生成表格。

            Args:
                cls: 当前准备创建的类对象、元类自身。
                name: 类名、在定义类时使用的类名。
                bases: 类集成的父类集合。
                attrs: 类的属性和方法集合、字典类型。
        """
        field_names = attrs.get("field_names", [])

        table = PrettyTable()
        table.field_names = field_names

        # 将 PrettyTable 对象添加到 attrs 中
        attrs["table"] = table

        # 返回新的类的对象
        return super().__new__(cls, name, bases, attrs)
    
class PTable(metaclass=TableHelper):
    pass

class TaskTable(PTable):
    """
        任务表格。
    """
    field_names = ["taskid"]

class ComplexTaskTable(PTable):
    """
        复杂任务表格。
    """
    field_names = ["id", "taskid", "duration", "origincodec", "outputcodec", "originresolution", "audiocodec", "bitrate", "framerate", "mode"]
