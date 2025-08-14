import time
from tasks.components.page.page import page_summon, page_main
from module.base.logger import logger

class Summon():
    pass

    # def run(self):
    #     if not self.check_page_appear(page_summon):
    #         self.goto(page_summon)

    #     image = self.screenshot()
    #     ticket = self.O_REG_SUMMON_TICKET.digit(image)
    #     if ticket < 10:
    #         print("No enough ticket to summon")

    #     if self.wait_until_appear(self.I_REG_SUMMON, 2, 1):
    #         self.click(self.I_REG_SUMMON)

    #     time.sleep(3)

    #     r = (ticket - 10) // 10
    #     for i in range(r):

    #         time.sleep(0.4)
    #         self.screenshot()
    #         logger.info(f"Summon round {i + 1}")
    #         if not self.wait_until_click(self.I_SUMMON_AGAIN):
    #             break

    #     self.goto(page_main, page_summon)
    #     exit()
