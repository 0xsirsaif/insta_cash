# Interview Task

### Intro

Thank you for your interest in joining us and for taking the time to do the task.

The goal of this task is to assess your knowledge of Database design, Django Framework, and Programming Best Practices.

This task is imaginary and is designed to test your knowledge and is not related in any way to the company business. We will NOT use your code.

Please follow the best practices and/or design patterns.

Take performance into consideration. make sure that your deliverables can be run in very high throughput environments.

### Problem

We are a Cash Collection application with a restful backend and mobile and web as front ends.

Imagine a `CashCollector` that is responsible for collecting cash

The `CashCollector` has a list of tasks where he/she goes to a customer and collects cash from, indicating the customer's info. i.e. name, address, amount_due (currency), amount_due_at (datetime), etc…

The `CashCollector` can see only one task at a time (the next task only) (They may however have read-only access to the tasks that he/she has already done)

The `CashCollector` should deliver the collected cash to the `Manager`.

The `CashCollector` has the freedom to go to the `Manager` whenever he/she wants to.

However, as a business we are afraid that the `CashCollector` will abuse the system and never deliver the amount they collected, thus we need to mark him/her as `frozen` if he/she has an amount greater than 5000USD for a period longer than 2 Days.

If the cash collector has 5000USD or more for 2 days or more, we should flag their account as `frozen`

`frozen CashCollector` means that he/she can no longer collect any more cash, they have to return the collected amount to the `Manager`

`CashCollector` and `Manager` are both our `Users`

<aside>
⚠️ Notice
2 days should pass after the `CashCollector` has a balance greater than 5000USD. NOT immediately!!

</aside>

### Example

Imagine we have a `CashCollector` called ‘John’

The `CashCollector` collected 1000USD at 2000-01-01 06:00

then `CashCollector` collected 6000USD at 2000-01-01 07:00

then `CashCollector` collected 2000USD at 2000-01-02 08:00

NOTICE that John was able to collect money even when he had 7000USD in his pocket because he only had this amount for less than 2 days

NOTICE also that John is able to do more tasks until just 2000-01-03 06:59 because he only exceeded the amount at  2000-01-01 07:00

| Collected Amount | Timestamp | Status |
| --- | --- | --- |
| 1000 | 2000-01-01 06:00 | Not Frozen |
| 6000 | 2000-01-01 07:00 | Not Frozen |
| 2000 | 2000-01-02 08:00 | Not Frozen |
|  | 2000-01-03 06:00 | Not Frozen |
|  | 2000-01-03 07:00 | Frozen |

### Deliverables

1. Create the Database Models necessary to support the above requirements
2. Create a way to show the status at different time points. this way can be one of the following
    1. admin page `provide it in your [Readme.md](http://Readme.md)`
    2. function call `provide it in your [Readme.md](http://Readme.md)`
    3. API call `provide it in your [Readme.md](http://Readme.md)`
    4. CSV output `provide how to generate it in your [Readme.md](http://Readme.md)`
    5. any other convenient way 
3. Create a Restful API that can expose the above requirements. The following list is just a hint, you can add or remove from it as you see fit
    1.  `tasks/`  to GET the list of the tasks that have been done by the `CashCollector`.
    2. `next_task/` to GET the task that `CashCollector` should do now.
    3. `status/` to GET a flag indicating whether the `CashCollector` is frozen or not.
    4. `collect/` to POST the amount collected for which task
    5. `pay/` to POST the amount delivered to the `Manager`
4. Test cases to cover the main scenario, and any edge cases that you can think of. (This will prove that you understand what your code is doing)
5. Upload the repo 

### Notes

1. Build the above with Django and use any other libraries that you think should benefit you in this task.
2. Assume we have more than one `CashCollector`
3. Use the Best practices that you know to handle the above.
4. Leave comments describing what you are doing if you feel it is ambiguous or unclear, the code will be read by a human.
5. Add [Readme.md](http://Readme.md) if you think your solution needs a description.
6. Assume that any `Manager` can access all `CashCollector` records in the system.
7. You don’t have to handle time zones.
8. You don’t have to handle multiple currencies. we can assume it is always USD.
9. If you have multiple solutions and each has its own Pros/Cons and you cannot determine which is the best. you can add both. but make it clear in the code where each solution begins and ends.
10. If you were not able to finish all the task, describe how you would have done it and all the technologies involved.

### Extra

it is a plus if you are able to 

1. configure the `5000USD threshold` and the`2 days threshold` as env vars
2. handle authentication

The time threshold for this task is 72 hours.

If you have any questions, feel free to reach out by email h.alansary@elham.sa