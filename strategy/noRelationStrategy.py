# -*- coding:utf-8 -*-

from Wilson.tasks import Tasks
from Wilson.component.tasksObj import *


class NoRelationStrategy(object):
    def __init__(self):
        self.__tasks = self.assign_tasks()

    @staticmethod
    def assign_tasks():
        tasks = Tasks()
        tasks.assign(InitCommand(InitFilesMethod))
        # tasks.assign(GetDataCommand(GetSpecialTagReviewsMethod))
        tasks.assign(GetDataCommand(GetReviewsMethod))
        tasks.assign(AdjustWeightCommand(NotAdjustWeightMethod))
        tasks.assign(CalBaseLineCommand(CalTargetBaseLineMethod))
        tasks.assign(CalBaseLineCommand(CalTagBaseLineMethod))
        tasks.assign(CalBaseLineCommand(CalModelBaseLineMethod))
        tasks.assign(EvaluateCommand(EvaluateTargetByWilsonMethod))
        tasks.assign(EvaluateCommand(EvaluateTagByWilsonMethod))
        tasks.assign(EvaluateCommand(EvaluateModelByWilsonMethod))
        tasks.assign(RankCommand(RankTargetByPMethod))
        tasks.assign(RankCommand(RankTagByPMethod))
        tasks.assign(RankCommand(RankModelByPMethod))
        tasks.assign(RankCommand(RankTargetByWilsonMethod))
        tasks.assign(RankCommand(RankTagByWilsonMethod))
        tasks.assign(RankCommand(RankModelByWilsonMethod))
        # tasks.assign(RateCommand(RatingTargetMethod))
        # tasks.assign(RateCommand(RatingTagMethod))
        # tasks.assign(RateCommand(RatingModelMethod))

        # task.assign(DealOtherCommand) # aver, top
        # tasks.assign(json)
        tasks.assign(ClearFileCommand(RemainFinalResultMethod))

        return tasks

    def __call__(self, *args, **kwargs):
        return self.__tasks
