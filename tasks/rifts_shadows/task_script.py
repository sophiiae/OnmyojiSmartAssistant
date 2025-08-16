from module.base.exception import TaskEnd
from tasks.components.battle.battle import Battle
from tasks.rifts_shadows.assets import RiftsShadowsAssets
from tasks.components.page.page import page_guild, page_main


class TaskScript(RiftsShadowsAssets, Battle):
    name = "RiftsShadows"

    def run(self):
        # 进入庭院页面
        if not self.check_page_appear(page_guild):
            self.goto(page_guild)

        success = True

        if self.appear(self.I_RS_GUILD_ENT):
            self.run_rs()
        else:
            success = False

        self.set_next_run(self.name, finish=True, success=success)
        self.goto(page_main)
        raise TaskEnd(self.name)

    def run_rs(self):
        pass

    def enter_rs_page(self):
        # 进入狭间暗域
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_RIFTS_SHADOW):
                break
            self.appear_then_click(self.I_RS_GUILD_ENT)
