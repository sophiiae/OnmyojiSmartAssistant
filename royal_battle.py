from tasks.royal_battle.task_script import TaskScript
from module.control.server.device import Device

if __name__ == "__main__":
    d = Device(config_name='1qian')
    task = TaskScript(d)
    # task.run()
    task.run_contest()
