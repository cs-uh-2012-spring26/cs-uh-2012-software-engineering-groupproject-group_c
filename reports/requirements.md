# Fitness Class Management and Booking System  
## Sprint 1 – Requirements Document  

---

# 1. Requirements Elicitation and Analysis  

## 1.1 Client Meeting Information  
- **Meeting Date:** February 11, 2026  
- **Client:** Rania Arbash - Fitness Center Owner  
- **Purpose:** Clarify ambiguities in the four high-level user stories and refine them into precise, implementable requirements.

## 1.2 Elicitation Techniques Used  

We used the following elicitation techniques during the meeting:

### 1. Structured Interview  
We prepared targeted clarification questions for each feature, such as:
- Who is allowed to create a class?
- Can guests view classes without signing in?
- Can users withdraw from a class?
- What information should be displayed in the class list?
- How is class capacity determined?
- Can users book after a class has started?

This ensured complete coverage of all features and avoided assumption based implementation.

### 2. Scenario-Based Walkthroughs  
We walked through realistic usage scenarios:
- A guest browsing classes without authentication.
- A member booking a full class.
- A user booking a class that has already started.
- A trainer joining their own class.

This helped clarify expected system behavior and edge cases.

## 1.3 Reflection on Elicitation Process  

The structured interview technique was effective because it allowed us to address ambiguities feature-by-feature and systematically document decisions. Scenario-based walkthroughs were particularly helpful in identifying edge cases such as booking ongoing classes and handling full classes.

In retrospect, preparing a simple visual mockup of the class list interface may have helped clarify display-related decisions more quickly.

A key clarification gained from the meeting was:

> Guests can view all upcoming classes without signing in, but must register and authenticate before booking.

This clarification directly influenced the API design by requiring public access to class-list endpoints while protecting booking functionality behind authentication.

# 2. Requirements Specification  

---

## 2.1 System Overview  

The Fitness Class Management and Booking System is a backend REST API that allows authorized users to create classes and manage bookings, while allowing public users to view upcoming classes.

Sprint 1 focuses only on core backend functionality. The following features are explicitly **out of scope** for Sprint 1:

- Class cancellation or editing  
- Booking withdrawal  
- Recurring classes  
- Time/location conflict management  
- Filtering/search functionality  
- Email verification  
- Third-party authentication  
- Full role-based access control enforcement  
- Kids/adult class categorization  

---

## 2.2 Actors  

### Guest (Unauthenticated User)
- Can view all upcoming classes.
- Cannot book classes.
- Must register to become a Member before booking.

### Member (Registered User)
- Can view classes.
- Can book classes.
- Can book unlimited classes.
- Cannot withdraw or cancel bookings (Sprint 1).

### Trainer
- Can create classes.
- Can view participant lists.
- Can join a class without occupying a participant slot.
- Responsible for managing scheduling conflicts externally.

### Admin (Gym Owner)
- Has the same capabilities as Trainer.
- Can create classes.
- Can view participant lists.

---
## 2.3 Use Case Diagram

**System Boundary:** Fitness Class Management and Booking System

![Sprint 1 Use Case Diagram](./use_case_diagram.png)  

**Actors → Use Cases**

- Guest → View Class List  
- Member → View Class List, Book Class  
- Trainer → Create Class, View Participant List  
- Admin → Create Class, View Participant List  

---

# 3. Use Case Specifications  

---

## Use Case 1: Create Class  

**Primary Actor:** Trainer or Admin  

### Preconditions:
- Actor is authenticated.
- Actor has Trainer/Admin privileges.

### Main Success Scenario:
1. Admin selects “Create Class”.  
2. System prompts for class information including class name, description, date and time, location, trainer, and capacity.  
3. Admin submits the class details.  
4. System validates the input fields.  
5. System stores the class in the database.  
6. The class becomes visible in the class list.

### Extensions:
- 2a. Required fields are missing.  
  - 2a1. System rejects the request and displays a validation error.  
- 2b. Date provided is in the past.  
  - 2b1. System rejects class creation.  
- 2c. Capacity is less than or equal to zero.  
  - 2c1. System rejects class creation.  

### Postconditions:
1. A new class exists in the system.  
2. The class is available for booking.

---

## Use Case 2: View Class List  

**Primary Actor:** Guest, Member, Trainer, Admin  

### Preconditions:
- None (public access allowed).

### Main Success Scenario:
1. Guest, member, trainer, or admin opens the class list.  
2. System retrieves all upcoming classes.  
3. System displays for each class:
   - Name  
   - Trainer  
   - Location  
   - Date and time  
   - Description  
   - Available spots  
   - Capacity  
4. Full classes remain visible in the list.

### Extensions:
- 2a. No classes are available.  
  - 2a1. System displays an empty list message.

### Postconditions:
- Actor receives the complete list of upcoming classes.

---

## Use Case 3: Book Class  

**Primary Actor:** Member  

### Preconditions:
- Actor is authenticated.
- Class exists.

### Main Success Scenario:
1. Member selects a class.  
2. System checks that the class has available spots.   
3. System records the booking.  
4. System decreases the available spots.  
5. Booking confirmation is returned.

### Extensions:
- 2a. Class has no available spots.  
  - 2a1. Booking is rejected.  
- 1a. Member has already booked the class.  
  - 1a1. Booking is rejected.  

### Postconditions:
- Member is recorded in participant list.
- Available slots updated accordingly.

---

## Use Case 4: View Participant List  

**Primary Actor:** Trainer or Admin  

### Preconditions:
- Actor is authenticated.
- Actor has Trainer/Admin privileges.
- Selected class exists.

### Main Success Scenario:
1. Actor selects a class.
2. System retrieves the participant list.
3. System displays:
   - Username  
   - Email  
   - Phone number  

### Extensions:
- 2a. No participants are registered for the class.  
  - 2a1. System displays an empty participant list. 

### Postconditions:
- Trainer/Admin can view complete participant list.

---

# 4. Functional Requirements Summary  

- Guests can view all classes without authentication.
- Only authenticated Members can book classes.
- Only Trainers/Admins can create classes.
- Class capacity is specified at creation time.
- Members may book unlimited classes.
- Full classes must still appear in listings.

---

# 5. Non-Functional Requirements  

- Registration requires username, password, and phone number (mandatory).
- No third-party authentication.
- No email verification required.
- System must enforce capacity limits.

---

This document reflects the clarified requirements agreed upon during the client meeting and serves as the basis for Sprint 1 implementation.
