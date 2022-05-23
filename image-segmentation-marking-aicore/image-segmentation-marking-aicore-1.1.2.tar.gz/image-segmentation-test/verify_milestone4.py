from .verify import get_errors_fails, mark_incomplete, mark_complete
import os

task1_id = '6e41bf59-99d3-4166-8c60-f907f643ba16' # Use `nohup` to run the API in the background
task2_id = 'd30b534f-c9c9-46a4-8012-aefc136b8d07' # Check out the dashboard

# def test_nohup(self):
# def  test_ip_dig(self):

if 'milestone4.txt' in os.listdir('.'):
    errors = get_errors_fails('milestone4.txt')
    # If there are no errors, mark everything as complete
    if len(errors) == 0:
        print('No errors found in milestone 4!')
        mark_complete(task1_id)
        mark_complete(task2_id)

    elif 'test_nohup' in errors:
        mark_incomplete(task1_id)
        mark_incomplete(task2_id)
        print("Feedback for task 1: " + errors['test_nohup'] + '\n')

    elif 'test_ip_dig' in errors:
        print("Task 1 looks good")
        mark_complete(task1_id)
        mark_incomplete(task2_id)
        print("Feedback for task 2: " + errors['test_ip_dig'] + '\n')

else:
    mark_incomplete(task1_id)
    mark_incomplete(task2_id)