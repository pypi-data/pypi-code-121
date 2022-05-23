from .verify import get_errors_fails, mark_incomplete, mark_complete
import os

task1_id = '957cf2c4-bced-4d30-ac99-02632446c449' # Save the processed results in the cloud
task2_id = 'dfc2c5fc-430d-49e2-8472-92063e8af21b' # Check out some of the results

# test_save_to_s3_again(self):
# test_output_in_s3(self):


if 'milestone3.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone3.txt')
    # If there are no errors, mark everything as complete
    if len(errors) == 0:
        print('No errors found in milestone 3!')
        mark_complete(task1_id)
        mark_complete(task2_id)

    elif 'test_save_to_s3_again' in errors:
        mark_incomplete(task1_id)
        mark_incomplete(task2_id)
        print("Feedback for task 1: " + errors['test_save_to_s3_again'] + '\n')

    elif 'test_output_in_s3' in errors:
        print("Task 1 looks good")
        mark_complete(task1_id)
        mark_incomplete(task2_id)
        print("Feedback for task 2: " + errors['test_output_in_s3'] + '\n')

else:
    mark_incomplete(task1_id)
    mark_incomplete(task2_id)