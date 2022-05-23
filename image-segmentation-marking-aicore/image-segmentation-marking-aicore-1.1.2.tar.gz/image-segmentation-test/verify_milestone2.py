from .verify import get_errors_fails, mark_incomplete, mark_complete
import os

task1_id = 'b31bd19a-077c-4937-ae5c-f7b219577575' # Pass the image data through the segmentation model
task2_id = '577e9084-0ee5-44fe-811d-4f51fad775ee' # Interpret the response from the model


# test_perform(self):
# test_print_segmented(self):


if 'milestone2.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone2.txt')
    # If there are no errors, mark everything as complete
    if len(errors) == 0:
        print('No errors found in milestone 2!')
        mark_complete(task1_id)
        mark_complete(task2_id)

    elif 'test_perform' in errors:
        mark_incomplete(task1_id)
        mark_incomplete(task2_id)
        print("Feedback for task 1: " + errors['test_perform'] + '\n')
    elif 'test_print_segmented' in errors:
        print("Task 1 looks good")
        mark_complete(task1_id)
        mark_incomplete(task2_id)
        print("Feedback for task 2: " + errors['test_print_segmented'] + '\n')

else:
    mark_incomplete(task1_id)
    mark_incomplete(task2_id)