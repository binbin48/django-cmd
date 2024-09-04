## Problem

A database table/model "Ticket" has 1 million rows. The table has a "token" column that holds a random unique UUID value for each row, determined by Django/Python logic at the time of creation. Due to a data leak, the candidate should write a django management command to iterate over every Ticket record to regenerate the unique UUID value. The command should inform the user of progress as the script runs and estimates the amount of time remaining. The script should also be sensitive to the potentially limited amount of server memory and avoid loading the full dataset into memory all at once, and show an understanding of Django ORM memory usage and query execution. Finally, the script should ensure that if it is interrupted that it should save progress and restart near the point of interruption so that it does not need to process the entire table from the start.

Please use Django / Python for your solution. The logic and thought process demonstrated are the most important considerations rather than truly functional code, however code presentation is important as well as the technical aspect. If you cannot settle on a single perfect solution, you may also discuss alternative solutions to demonstrate your understanding of potential trade-offs as you encounter them. Of course if you consider a solution is too time consuming you are also welcome to clarify or elaborate on potential improvements or multiple solution approaches conceptually to demonstrate understanding and planned solution.


## Investigation
From the provided requirements I break into 2 kinds of requirements.
### functional requirements
- write command to regenerate UUID for each ticket
- show the progress
- estimate the amount of time remaining
- can start from the failure point when the execution is interrupted

### non-functional requirements
- Scalability, Memory efficiency: must handle a large dataset of 1 million rows, should not load entire dataset into memory
- Fault tolerance: minimize redundant processing by restarting near the point of interuption
- Logging and montoring: should have mechanism to log the process, the errors for debugging process.

## Solution Outline:
- to avoid loading all rows into memory we will split queryset into smaller **chunk**
- to generate unique UUID, use Python's `uuid` lib
- to handle interruptions: Use Django’s transaction and checkpointing to save progress to a file.
- use `bulk_update` to reduce the query number to speed up.
- use model's `bulk_update` method with `fields` param to specify the updated column to speed up

## Result

| Batch size | Execution time | Notes |
|------------|----------------|-------|
| 10,000     | 236 seconds    |       |
| 5,000      | 73 seconds     |       |
| 20,000     | > 600 seconds  |       |

## How to run this project
1. Build and start project by using docker compose
`docker compose up -d`
2. Create the initial data
- open shell in web container `docker exec -it web sh`
- run command `python manage.py create_ticket`

3. Generate token for existing tickets
- stay in the web container sell
- run command `python manage.py generate_ticket_token`
    - you can specify the batch size by set `--batch_size` option. Default size is 10000
- If you want to regenerate again. You have to delete `checkpoint.txt` file and do step 3 again.


## Alternative Approaches Discussion.
1. We can use the QuerySet iterator() to avoid loading the entire dataset into memory, but it increases the number of queries.
2. We could use async abulk_update to reduce waiting time from I/O. However, since the dataset isn’t extremely large and this is a one-time command, we can skip this solution.
3. We can use multiple processors to run it in parallel, but the complexity outweighs the benefits.
4. We can use other way to save the checkpoint instead of file.