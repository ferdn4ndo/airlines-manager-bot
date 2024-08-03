from django_cron import CronJobBase, Schedule


class TestCronJob(CronJobBase):
    INTERVAL_MINUTES = 1

    schedule = Schedule(run_every_mins=INTERVAL_MINUTES)
    code = 'ambot.api.cron.test'  # a unique code

    def do(self):
        return "[TestCronJob] Done!"
