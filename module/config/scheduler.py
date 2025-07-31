import operator
from module.config.function import Function

class TaskScheduler:

    @staticmethod
    def fifo(pending: list["Function"]) -> list["Function"]:
        """
        先来后到，（按照任务的先后顺序进行调度）
        :param pending:
        :return:
        """
        tasks_pending = sorted(pending, key=operator.attrgetter("next_run"))
        for task in tasks_pending:
            # 永远保证 Restart 任务在第一个
            if task.name == 'Restart':
                tasks_pending.remove(task)
                tasks_pending.insert(0, task)
                break
        return tasks_pending

    @staticmethod
    def priority(pending: list["Function"]) -> list["Function"]:
        """
        基于优先级，同一个优先级的任务按照先来后到的顺序进行调度，优先级高的任务先调度
        :param pending:
        :return:
        """
        # 1. 按照优先级进行分组
        sorted(pending, key=operator.attrgetter("priority"))
        groups = {}
        for task in pending:
            if groups.get(task.priority) is None:
                groups[task.priority] = []
            groups[task.priority].append(task)
        # 2. 对每一组进行先来后到的排序
        for priority, tasks in groups.items():
            groups[priority] = TaskScheduler.fifo(tasks)

        # 3.按照顺序合并所有的任务
        tasks_pending = []
        for priority in sorted(groups.keys()):
            tasks_pending.extend(groups[priority])

        return tasks_pending


# 测试代码
if __name__ == '__main__':
    pass
