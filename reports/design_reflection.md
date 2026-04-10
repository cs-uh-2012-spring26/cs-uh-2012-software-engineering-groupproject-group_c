## Design Reflections – Sprint 3A

This report documents the current design of the Fitness Class Management and Booking System as part of Sprint 3A. The goal of this sprint is to analyze the existing design to prepare for the upcoming implementation of recurring classes (Feature 6) and configurable notifications (Feature 7).


## Summary

**Tools Used:**
- *No automated tools were used.*

**Approach:**
- *We conducted manual code review in a zoom call with all of us reviewing different files*

**Team Member Responsibilities:**
|      Team Member   |     Responsibility    |
|--------------------|-----------------------|
| *Ryan Opande*      | *(TBD)*               |
| *Nelson Mbigili*   | *(TBD)*               |
| *Michael Girum*    | *(TBD)*               |
| *Paul Luziga*      | *(TBD)*               |

---

## 1 - Design Diagrams
### Class Diagram
> Source file: `reports/classumldiag.png`


The diagram below shows the main classes in the system and their associations across the four layers: API, Database,Service and Config.

![Class Diagram ](classumldiag.png)
**Key associations:**
- The four API Resource classes (`FitnessClassList`, `BookClass`, `ClassParticipants`, `ClassReminder`) depend on `FitnessClassResource` for all class-related database operations.
- `BookClass` additionally depends on `UserResource` to retrieve the booking member's details.
- Also `Login` and `Register` depends on `UserResource` to authenticate or add a member respectively.
- `ClassReminder` depends on `EmailService` to send reminder emails.
- Both `FitnessClassResource` and `UserResource` use the `DB` class to obtain their MongoDB collections.
- `EmailService` communicates with the external AWS SES service via a boto3 client.
- `Config` handles both `EmailService` and `DB`

### Sequence Diagram for book class endpoint
![Sequence Diagram for book class endpoint](files/book_class_sequence_diagram.png)

### Sequence Diagram for remind endpoint
![Sequence Diagram for remind endpoint](files/remind_sequence_diagram.png)

---

## 2 - Design Principle Violations

### Violation 1: Single Responsibility Principle (SRP)
**File:** `app/apis/classes.py` 
**Lines:** 159–207 
**Method:** `BookClass.post()`

**Principle:** A class or method should have only one reason to change.

**Screenshot:**
![Single Responsibility Principle ](./files/single_responsibility_A.png)
![Single Responsibility Principle ](./files/single_responsibility_B.png)

**Violation:** The `BookClass.post()` method currently handles at least five distinct responsibilities in a single function:
1. Role authorization (lines 161–164)
2. Fetching and validating the fitness class from the database (lines 167–172)
3. Computing and checking the booking deadline (lines 175–179)
4. Fetching the user's full profile from the database (lines 182–186)
5. Constructing the participant object and performing the booking (lines 189–207)

If any one of these behaviors needs to change (e.g., the deadline window is changed, or the booking logic is updated), the entire method must be modified. These responsibilities are independent and should each have their own home for example, deadline checking and participant construction could be extracted into helper functions.

---

### Violation 2: Dependency Inversion Principle (DIP)

**File:** `app/apis/classes.py` 
**Lines:** 270–271 
**Method:** `ClassReminder.post()`

**Principle:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Violation:** The high-level `ClassReminder` endpoint directly imports and instantiates the concrete `EmailService` class inside the method body:

**Screenshot:**
![Dependency Inversion Principle ](./files/dependency_inversion.png)

There is no abstraction between `ClassReminder` and `EmailService`. This means `ClassReminder` is directly coupled to the concrete email implementation. If we want to send reminders via a different channel (e.g., SMS), we would have to modify this method rather than simply swapping out the dependency.

---

### Violation 3: Open-Closed Principle (OCP)

**File:** `app/services/email_service.py` 
**Lines:** 6–52 
**Class:** `EmailService`

**Principle:** Classes should be open for extension but closed for modification.

**Screenshot:**
![Open-Closed Principle ](./files/open_closed_principle.png)

**Violation:** The `EmailService` class has no abstract base class or interface. It provides only one notification channel (email via AWS SES). Feature 7 requires users to choose between email, Telegram, SMS, and potentially other channels. Since there is no abstract `NotificationService` that other implementations could extend, adding new channels forces us to either:
- Modify `EmailService` directly (violating the "closed for modification" rule), or
- Create entirely unrelated classes with no shared contract.

A proper design would define an abstract `NotificationService` with a `send_reminder()` method, and have `EmailService`, `SMSService`, and `TelegramService` each implement it independently.

---

### Violation 4: Modularity

**File:** `app/apis/classes.py` 
**Lines:** 113–120 
**Method:** `FitnessClassList.post()`

**Principle:** Related logic should be grouped into reusable, cohesive units.

**Violation:** The same field extraction pattern is repeated seven times in sequence:

**Screenshot:**
![Modularity ](./files/Modularity.png)

This is not modular. The same logic (safely extract a string field and strip whitespace) is repeated inline rather than extracted into a helper function. This means if the extraction logic ever needs to change, it would have to be updated in seven places. A simple helper function like `_get_str_field(data, key)` would eliminate this repetition.

---
### Violation 5: Encapsulation

**File:** `app/db/fitness_classes.py` 
**Lines:** 45–56 
**Method:** `FitnessClassResource.book_class()`

**Principle:** Internal state and implementation details should not be exposed through a class's public interface.

**Violation:** The `book_class()` method communicates its result by returning raw string codes: `"not_found"`, `"already_booked"`, `"class_full"`, and `"ok"`. The calling code in `classes.py` (lines 199–204) is then required to know and match against these specific strings:

**Screenshot:**
![Encapsulation ](./files/Encapsulation.png)

This leaks internal implementation details through the public interface of `FitnessClassResource`. The caller must know the exact internal string values the method may return. A better approach would be to raise domain-specific exceptions (e.g., `ClassFullError`, `AlreadyBookedError`) or return a structured result object, which would be a more encapsulated and type-safe design.

---

## 3 – Code Smells

### Code Smell 1: *Duplicate Code*

**File:** `app/apis/classes.py`<br>
**Lines:** *(113-120)*<br>
**Method:** `FitnessClassList.post()`

**Description:**
*The same string field extraction pattern is written out seven times with only the field name changing.
This is a textbook case of duplicated code. Any logic change to how a field is extracted must be applied in seven separate places, which is error-prone and hard to maintain.*

**Screenshot:**
![Duplicate Code ](./files/duplicate_code.png)

### Code Smell 2: *Long Parameter List*

**File:** `app/db/fitness_classes.py`<br>
**Lines:** *(33-34)*<br>
**Method:** `Fitness ClassResource.create_fitness_class()`

**Description:**
*The create_fitness_class() method accepts nine separate parameters: name, description, date, start_time, end_time, location, trainer, capacity, and created_by. A long parameter list is a code smell because it makes the method signature hard to read, easy to call with arguments in the wrong order, and difficult to extend (adding a new field like a recurrence pattern requires changing the method signature and every call site). A better approach would be to group these fields into a single data object or dictionary that is passed as one argument.*

**Screenshot:**
![Long Parameter List](./files/Long_Parameter_List.png)

### Code Smell 3: *Dead Code*

**File:** `app/db/users.py` <br>
**Lines:** *(22-30, 81-82)* <br>
**Method:** `UserResource.get_users(), UserResource.delete_all_users()`

**Description:**
*Both of these methods exist in the production codebase but are never called by any API endpoint. get_users() (lines 22-30) supports filtering by name and role, but no route in app/apis/ invokes it. delete_all_users() (lines 81-82) is only referenced directly from the test suite by accessing the collection object, not through this method. We innitially added these by intuition as they may be usefull in future. However, as with any Dead code, they add maintenance burden - must be kept in sync with the rest of the system even though they deliver no value at the moment - and can create confusion about what is actually in use*

**Screenshot:**
![Dead Code 1](./files/dead_code1.png)
![Dead Code 2](./files/dead_code2.png)

### Code Smell 4: *Long Method*

**File:** `app/apis/classes.py`<br>
**Lines:** *(159-207)*<br>
**Method:** `BookClass.post()`  

**Description:**
*The BookClass.post() method spans 48 lines and performs multiple operations: authorization, class retrieval, deadline checking, user retrieval, participant construction, and booking. A method this long is difficult to read, test, and maintain independently. As a rule of thumb, methods should be short enough to see in one screen and do one thing well.*

**Screenshot:**
![Long Method](./files/Long_Method.png)

---

---


## 4 – Design Reflection on New Features
    
**New Features Being Considered:**
 >TBD


**How Current Design Helps:**
>TBD

**How Current Design Hinders:**
>TBD

**Recommendations:**
>TBD