# -*- coding:utf-8 -*-

from Wilson.tasks import Tasks
from Wilson.component.tasksObj import *


class NoRelationWithWilsonAspectStrategy(object):
    def __init__(self):
        self.__tasks = self.assign_tasks()

    @staticmethod
    def assign_tasks():
        tasks = Tasks()
        tasks.assign(InitCommand(InitFilesMethod))
        tasks.assign(GetDataCommand(GetSpecialTagReviewsMethod))
        # tasks.assign(GetDataCommand(GetReviewsMethod))
        tasks.assign(AdjustWeightCommand(NotAdjustWeightMethod))
        tasks.assign(CalBaseLineCommand(CalTargetBaseLineMethod))
        tasks.assign(CalBaseLineCommand(CalTagBaseLineMethod))
        tasks.assign(CalBaseLineCommand(CalModelBaseLineMethod))
        tasks.assign(EvaluateCommand(EvaluateTargetByWilsonMethod))
        tasks.assign(EvaluateCommand(EvaluateTagByWilsonMethod))
        tasks.assign(EvaluateCommand(EvaluateModelByWilsonMethod))
        tasks.assign(RankCommand(RankTargetByWilsonMethod))
        tasks.assign(RankCommand(RankTagByWilsonMethod))
        tasks.assign(RankCommand(RankModelByWilsonMethod))
        tasks.assign(CalAspectCommand(CalTargetBasicPlusAspectMethod))
        tasks.assign(CalAspectCommand(CalTagBasicPlusAspectMethod))
        tasks.assign(CalAspectCommand(CalModelBasicPlusAspectMethod))
        # 100的问题 服务-包装
        tasks.assign(RateCommand(RatingTargetIndependentMethod))
        tasks.assign(RateCommand(RatingTagIndependentMethod))
        tasks.assign(RateCommand(RatingModelIndependentMethod))
        tasks.assign(CalAverAndTopCommand(CalTargetAverAndTopMethod))
        tasks.assign(CalAverAndTopCommand(CalTagAverAndTopMethod))
        tasks.assign(CalAverAndTopCommand(CalModelAverAndTopMethod))
        tasks.assign(SelectCommand(SelectUsefulColumnsMethod))
        tasks.assign(TransToJsonCommand(TargetTransToTagMethod))
        tasks.assign(TransToJsonCommand(TagTransToModelMethod))
        tasks.assign(TransToJsonCommand(JsonReviseMethod))
        tasks.assign(ClearFileCommand(RemainFinalResultMethod))

        return tasks

    def __call__(self, *args, **kwargs):
        return self.__tasks
