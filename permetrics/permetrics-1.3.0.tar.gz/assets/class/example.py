#!/usr/bin/env python
# Created by "Thieu" at 16:50, 19/05/2022 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

from permetrics.classification import ClassificationMetric
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score


# y_true = ["cat", "ant", "cat", "cat", "ant", "bird", "bird", "bird"]
# y_pred = ["ant", "ant", "cat", "cat", "ant", "cat", "bird", "ant"]

y_true = [0, 1, 0, 0, 1, 0]
y_pred = [0, 1, 0, 0, 0, 1]

cm = ClassificationMetric(y_true, y_pred, decimal = 5)


# print("==============test f1 score ========================")
print(f1_score(y_true, y_pred))
print(f1_score(y_true, y_pred, average="micro"))
print(f1_score(y_true, y_pred, average="macro"))
print(f1_score(y_true, y_pred, average="weighted"))
print(f1_score(y_true, y_pred, average=None))

print(cm.f1_score())
print(cm.f1_score(average="micro"))
print(cm.f1_score(average="macro"))
print(cm.f1_score(average="weighted"))
print(cm.f1_score(average=None))


# print("==============test accuracy ========================")
# print(accuracy_score(y_true, y_pred))
# print(accuracy_score(y_true, y_pred, normalize=False))
# print(cm.accuracy_score(average="micro"))
# print(cm.accuracy_score(average="macro"))
# print(cm.accuracy_score(average="weighted"))
# print(cm.accuracy_score(average=None))



# print("====================4th test=======================")
# pr = precision_score(y_true, y_pred, average="micro")
# rc = recall_score(y_true, y_pred, average="micro")
# print(pr, rc)
# print(cm.precision_score(average="micro"))


# print("====================3rd test=======================")
# pr = precision_score(y_true, y_pred, average="weighted")
# rc = recall_score(y_true, y_pred, average="weighted")
# print(pr, rc)
# print(cm.precision_score(average="weighted"))



# print("====================2nd test=======================")

# pr = precision_score(y_true, y_pred, average="macro")
# rc = recall_score(y_true, y_pred, average="macro")
# print(pr, rc)
# print(cm.precision_score(average="macro"))


# print("====================1st test=======================")
# pr = precision_score(y_true, y_pred, average=None)
# rc = recall_score(y_true, y_pred, average=None)
# print(pr, rc)
# print(cm.precision_score())
#






